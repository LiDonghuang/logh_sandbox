Set-StrictMode -Version Latest

function Get-CombatDamageEvents {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)]$MovedUnitsById,
        [Parameter(Mandatory)]$AdjustedVectors
    )

    $damageByTarget = [ordered]@{}
    foreach ($unitId in $MovedUnitsById.Keys) {
        $attacker = $MovedUnitsById[$unitId]
        if ($attacker.HitPoints -le 0.0) { continue }

        $attackVector = $AdjustedVectors[$unitId]
        if ($null -eq $attackVector) { continue }
        if ([string]::IsNullOrEmpty($attackVector.TargetUnitId)) { continue }
        if (-not $MovedUnitsById.Contains($attackVector.TargetUnitId)) { continue }

        $target = $MovedUnitsById[$attackVector.TargetUnitId]
        if ($target.HitPoints -le 0.0) { continue }
        if ($target.FleetId -eq $attacker.FleetId) { continue }

        $distance = Get-Distance2D -A $attacker.Position -B $target.Position
        $weaponRange = 18.0
        if ($distance -gt $weaponRange) { continue }

        $rangeFactor = 1.0 - ($distance / $weaponRange)
        $baseDamage = 8.0
        $damage = $baseDamage * $attackVector.EngagementIntensity * $rangeFactor
        if ($damage -le 0.0) { continue }

        if (-not $damageByTarget.Contains($target.UnitId)) {
            $damageByTarget[$target.UnitId] = 0.0
        }
        $damageByTarget[$target.UnitId] += $damage
    }

    return $damageByTarget
}

function Invoke-StateCommit {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)]$MovedUnitsById,
        [Parameter(Mandatory)]$AdjustedVectors,
        [Parameter(Mandatory)]$FleetCohesionForNextTick
    )

    $damageByTarget = Get-CombatDamageEvents -Snapshot $Snapshot -MovedUnitsById $MovedUnitsById -AdjustedVectors $AdjustedVectors

    $committedUnits = [ordered]@{}
    foreach ($unitId in $MovedUnitsById.Keys) {
        $unit = $MovedUnitsById[$unitId]
        $damageTaken = 0.0
        if ($damageByTarget.Contains($unitId)) {
            $damageTaken = [double]$damageByTarget[$unitId]
        }

        $newHp = [double]$unit.HitPoints - $damageTaken
        if ($newHp -lt 0.0) { $newHp = 0.0 }

        $committedUnits[$unitId] = New-UnitState `
            -UnitId $unit.UnitId `
            -FleetId $unit.FleetId `
            -Position $unit.Position `
            -Velocity $unit.Velocity `
            -HitPoints $newHp `
            -MaxHitPoints $unit.MaxHitPoints `
            -MaxSpeed $unit.MaxSpeed
    }

    $fleets = [ordered]@{}
    $nextFleetCohesion = [ordered]@{}
    foreach ($fleetId in $Snapshot.Fleets.Keys) {
        $fleet = $Snapshot.Fleets[$fleetId]
        $aliveUnitIds = @()
        foreach ($unitId in $fleet.UnitIds) {
            if ($committedUnits.Contains($unitId) -and $committedUnits[$unitId].HitPoints -gt 0.0) {
                $aliveUnitIds += $unitId
            }
        }

        $fleets[$fleetId] = New-FleetState -FleetId $fleetId -Parameters $fleet.Parameters -UnitIds $aliveUnitIds
        if ($aliveUnitIds.Count -eq 0) {
            $nextFleetCohesion[$fleetId] = 0.0
        } else {
            $nextFleetCohesion[$fleetId] = [double]$FleetCohesionForNextTick[$fleetId]
        }
    }

    $tickEntry = [pscustomobject]@{
        Tick = $Snapshot.Tick + 1
        DamageByTarget = $damageByTarget
        FleetCohesion = $nextFleetCohesion
    }

    return [pscustomobject]@{
        Tick              = $Snapshot.Tick + 1
        Dt                = $Snapshot.Dt
        ArenaSize         = $Snapshot.ArenaSize
        Units             = $committedUnits
        Fleets            = $fleets
        LastFleetCohesion = $nextFleetCohesion
        TickEntry         = $tickEntry
    }
}
