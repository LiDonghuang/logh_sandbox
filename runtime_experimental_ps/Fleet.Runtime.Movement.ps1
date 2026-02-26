Set-StrictMode -Version Latest

function Get-TurnLimitedVelocity {
    param(
        [Parameter(Mandatory)]$CurrentVelocity,
        [Parameter(Mandatory)]$DesiredVelocity,
        [double]$MaxTurnRadians
    )

    $currentSpeed = Get-Vector2Magnitude -A $CurrentVelocity
    $desiredSpeed = Get-Vector2Magnitude -A $DesiredVelocity

    if ($currentSpeed -le 1e-9 -or $desiredSpeed -le 1e-9) {
        return $DesiredVelocity
    }

    $currentDirection = Normalize-Vector2 -A $CurrentVelocity
    $desiredDirection = Normalize-Vector2 -A $DesiredVelocity
    $limitedDirection = Rotate-VectorTowards -CurrentDirection $currentDirection -DesiredDirection $desiredDirection -MaxRadians $MaxTurnRadians

    return (Scale-Vector2 -A $limitedDirection -Scalar $desiredSpeed)
}

function Invoke-MovementLayer {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)]$AdjustedVectors,
        [Parameter(Mandatory)]$CohesionForcesByUnit
    )

    $updatedUnits = [ordered]@{}

    foreach ($unitId in $Snapshot.Units.Keys) {
        $unit = $Snapshot.Units[$unitId]
        if ($unit.HitPoints -le 0.0) {
            $updatedUnits[$unitId] = Copy-UnitState -Unit $unit
            continue
        }

        $fleet = $Snapshot.Fleets[$unit.FleetId]
        $mobility = [double]$fleet.Parameters.Normalized.MobilityBias

        $targetVector = $AdjustedVectors[$unitId]
        $cohesionForce = $CohesionForcesByUnit[$unitId]
        if ($null -eq $cohesionForce) {
            $cohesionForce = New-Vector2
        }

        $targetForceGain = 1.6
        $targetForce = Scale-Vector2 -A $targetVector.TargetDirection -Scalar ($targetVector.EngagementIntensity * $targetForceGain)
        $combinedAcceleration = Add-Vector2 -A $targetForce -B $cohesionForce

        $maxAcceleration = 0.8 + (1.4 * $mobility)
        $combinedAcceleration = Clamp-Vector2Magnitude -A $combinedAcceleration -MaxMagnitude $maxAcceleration

        $unconstrainedVelocity = Add-Vector2 -A $unit.Velocity -B (Scale-Vector2 -A $combinedAcceleration -Scalar $Snapshot.Dt)

        $velocityUtilization = $unit.MaxSpeed * $mobility
        if ($velocityUtilization -lt 0.4) {
            $velocityUtilization = 0.4
        }
        $boundedVelocity = Clamp-Vector2Magnitude -A $unconstrainedVelocity -MaxMagnitude $velocityUtilization

        $maxTurnDegrees = 10.0 + (170.0 * $mobility)
        $maxTurnRadians = $maxTurnDegrees * [Math]::PI / 180.0
        $turnLimitedVelocity = Get-TurnLimitedVelocity -CurrentVelocity $unit.Velocity -DesiredVelocity $boundedVelocity -MaxTurnRadians ($maxTurnRadians * $Snapshot.Dt)

        $newPosition = Add-Vector2 -A $unit.Position -B (Scale-Vector2 -A $turnLimitedVelocity -Scalar $Snapshot.Dt)

        $arenaMin = 0.0
        $arenaMax = $Snapshot.ArenaSize

        if ($newPosition.X -lt $arenaMin) {
            $newPosition.X = $arenaMin
            $turnLimitedVelocity.X = 0.0
        } elseif ($newPosition.X -gt $arenaMax) {
            $newPosition.X = $arenaMax
            $turnLimitedVelocity.X = 0.0
        }

        if ($newPosition.Y -lt $arenaMin) {
            $newPosition.Y = $arenaMin
            $turnLimitedVelocity.Y = 0.0
        } elseif ($newPosition.Y -gt $arenaMax) {
            $newPosition.Y = $arenaMax
            $turnLimitedVelocity.Y = 0.0
        }

        $updatedUnits[$unitId] = New-UnitState `
            -UnitId $unit.UnitId `
            -FleetId $unit.FleetId `
            -Position $newPosition `
            -Velocity $turnLimitedVelocity `
            -HitPoints $unit.HitPoints `
            -MaxHitPoints $unit.MaxHitPoints `
            -MaxSpeed $unit.MaxSpeed
    }

    return $updatedUnits
}
