Set-StrictMode -Version Latest

function Get-FleetTotalHitPoints {
    param(
        [Parameter(Mandatory)]$State,
        [Parameter(Mandatory)][string]$FleetId
    )

    $sum = 0.0
    foreach ($unitId in $State.Fleets[$FleetId].UnitIds) {
        if ($State.Units.Contains($unitId)) {
            $sum += [double]$State.Units[$unitId].HitPoints
        }
    }

    return $sum
}

function Get-AliveFleetIds {
    param([Parameter(Mandatory)]$State)

    $alive = @()
    foreach ($fleetId in $State.Fleets.Keys) {
        if ($State.Fleets[$fleetId].UnitIds.Count -gt 0) {
            $alive += $fleetId
        }
    }
    return $alive
}

function Invoke-EngineTick {
    param([Parameter(Mandatory)]$State)

    # 1. State Snapshot Capture
    $snapshot = Copy-BattleStateSnapshot -State $State

    # 2-5. VisibleSet, Feature Extraction, Target Score, TargetVector
    $targetLayerOutput = Invoke-TargetLayer -Snapshot $snapshot

    # 6-7. Utility Evaluation and Engagement Adjustment
    $utilityLayerOutput = Invoke-UtilityLayer `
        -Snapshot $snapshot `
        -TargetLayerOutput $targetLayerOutput `
        -LastFleetCohesion $snapshot.LastFleetCohesion

    # 8. Cohesion Force Evaluation
    $cohesionOutput = Invoke-CohesionLayer -Snapshot $snapshot

    # 9. Movement Integration
    $movedUnits = Invoke-MovementLayer `
        -Snapshot $snapshot `
        -AdjustedVectors $utilityLayerOutput.AdjustedVectors `
        -CohesionForcesByUnit $cohesionOutput.ForcesByUnit

    # 10. State Commit
    $committed = Invoke-StateCommit `
        -Snapshot $snapshot `
        -MovedUnitsById $movedUnits `
        -AdjustedVectors $utilityLayerOutput.AdjustedVectors `
        -FleetCohesionForNextTick $cohesionOutput.FleetCohesion

    $tickSummary = [ordered]@{
        Tick = $committed.Tick
        Fleets = [ordered]@{}
    }
    foreach ($fleetId in $committed.Fleets.Keys) {
        $tickSummary.Fleets[$fleetId] = [pscustomobject]@{
            AliveUnits = $committed.Fleets[$fleetId].UnitIds.Count
            HitPoints  = [Math]::Round((Get-FleetTotalHitPoints -State $committed -FleetId $fleetId), 2)
            Cohesion   = [Math]::Round([double]$committed.LastFleetCohesion[$fleetId], 4)
        }
    }

    return [pscustomobject]@{
        Tick              = $committed.Tick
        Dt                = $committed.Dt
        ArenaSize         = $committed.ArenaSize
        Units             = $committed.Units
        Fleets            = $committed.Fleets
        LastFleetCohesion = $committed.LastFleetCohesion
        TickLog           = @($State.TickLog + @([pscustomobject]$tickSummary))
    }
}

function Get-BattleSignature {
    param([Parameter(Mandatory)]$State)

    $parts = @("Tick=$($State.Tick)")
    foreach ($unitId in ($State.Units.Keys | Sort-Object)) {
        $unit = $State.Units[$unitId]
        $parts += "{0}:{1}:{2:F4}:{3:F4}:{4:F4}" -f $unit.UnitId, $unit.FleetId, $unit.HitPoints, $unit.Position.X, $unit.Position.Y
    }

    return ($parts -join "|")
}

function Invoke-BattleSimulation {
    param(
        [Parameter(Mandatory)]$InitialState,
        [int]$MaxTicks = 60
    )

    $state = $InitialState
    while ($state.Tick -lt $MaxTicks) {
        $aliveFleets = @(Get-AliveFleetIds -State $state)
        if ($aliveFleets.Count -le 1) {
            break
        }
        $state = Invoke-EngineTick -State $state
    }

    $aliveAfter = @(Get-AliveFleetIds -State $state)
    $winner = if ($aliveAfter.Count -eq 1) { $aliveAfter[0] } else { "Draw" }

    return [pscustomobject]@{
        FinalState = $state
        Winner = $winner
        Signature = Get-BattleSignature -State $state
    }
}
