Set-StrictMode -Version Latest

function Get-FleetCentroid {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)][string]$FleetId
    )

    $unitIds = @(Get-AliveUnitIdsForFleet -State $Snapshot -FleetId $FleetId)
    if ($unitIds.Count -eq 0) {
        return (New-Vector2)
    }

    $sum = New-Vector2
    foreach ($unitId in $unitIds) {
        $sum = Add-Vector2 -A $sum -B $Snapshot.Units[$unitId].Position
    }

    return (Scale-Vector2 -A $sum -Scalar (1.0 / $unitIds.Count))
}

function Get-FleetMeanVelocity {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)][string]$FleetId
    )

    $unitIds = @(Get-AliveUnitIdsForFleet -State $Snapshot -FleetId $FleetId)
    if ($unitIds.Count -eq 0) {
        return (New-Vector2)
    }

    $sum = New-Vector2
    foreach ($unitId in $unitIds) {
        $sum = Add-Vector2 -A $sum -B $Snapshot.Units[$unitId].Velocity
    }

    return (Scale-Vector2 -A $sum -Scalar (1.0 / $unitIds.Count))
}

function Get-FleetDispersion {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)][string]$FleetId,
        [Parameter(Mandatory)]$Centroid
    )

    $unitIds = @(Get-AliveUnitIdsForFleet -State $Snapshot -FleetId $FleetId)
    if ($unitIds.Count -eq 0) {
        return 0.0
    }

    $sumDistance = 0.0
    foreach ($unitId in $unitIds) {
        $sumDistance += Get-Distance2D -A $Snapshot.Units[$unitId].Position -B $Centroid
    }

    return ($sumDistance / $unitIds.Count)
}

function Invoke-CohesionLayer {
    param([Parameter(Mandatory)]$Snapshot)

    $forcesByUnit = [ordered]@{}
    $fleetCohesion = [ordered]@{}

    foreach ($fleetId in $Snapshot.Fleets.Keys) {
        $fleet = $Snapshot.Fleets[$fleetId]
        $unitIds = @(Get-AliveUnitIdsForFleet -State $Snapshot -FleetId $fleetId)

        if ($unitIds.Count -eq 0) {
            $fleetCohesion[$fleetId] = 0.0
            continue
        }

        $centroid = Get-FleetCentroid -Snapshot $Snapshot -FleetId $fleetId
        $meanVelocity = Get-FleetMeanVelocity -Snapshot $Snapshot -FleetId $fleetId
        $dispersion = Get-FleetDispersion -Snapshot $Snapshot -FleetId $fleetId -Centroid $centroid

        $fr = [double]$fleet.Parameters.Normalized.FormationRigidity
        $fcr = [double]$fleet.Parameters.Normalized.ForceConcentrationRatio

        # Discrete interpretation of frozen continuous model:
        # stiffness ~ FR, damping ~ (1 - FR)
        $stiffness = 0.25 * $fr
        $damping = 0.20 * (1.0 - $fr)

        $baseClusterRadius = 18.0
        $clusterScale = 0.70
        $desiredClusterRadius = $baseClusterRadius * (1.0 - ($fcr * $clusterScale))
        if ($desiredClusterRadius -lt 1.0) { $desiredClusterRadius = 1.0 }

        $cohesionValue = 1.0 / (1.0 + ($dispersion / $desiredClusterRadius))
        $fleetCohesion[$fleetId] = Clamp-Scalar -Value $cohesionValue -Min 0.0 -Max 1.0

        foreach ($unitId in $unitIds) {
            $unit = $Snapshot.Units[$unitId]
            $toCentroid = Subtract-Vector2 -A $centroid -B $unit.Position
            $alignmentDelta = Subtract-Vector2 -A $meanVelocity -B $unit.Velocity

            $restoring = Scale-Vector2 -A $toCentroid -Scalar $stiffness
            $dampingTerm = Scale-Vector2 -A $unit.Velocity -Scalar (-1.0 * $damping)
            $alignmentTerm = Scale-Vector2 -A $alignmentDelta -Scalar (0.08 * (1.0 - $fr))

            $force = Add-Vector2 -A $restoring -B (Add-Vector2 -A $dampingTerm -B $alignmentTerm)
            $forcesByUnit[$unitId] = $force
        }
    }

    return [pscustomobject]@{
        ForcesByUnit  = $forcesByUnit
        FleetCohesion = $fleetCohesion
    }
}
