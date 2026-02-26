param(
    [long]$RootSeed = 20260222,
    [int]$MaxTicks = 80
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$runtimeRoot = Join-Path $PSScriptRoot "runtime"
. (Join-Path $runtimeRoot "Fleet.Runtime.Math2D.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.CoreData.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.Seed.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.Cohesion.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.Target.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.Utility.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.Movement.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.StateCommit.ps1")
. (Join-Path $runtimeRoot "Fleet.Runtime.Engine.ps1")

function New-InitialBattleState {
    param([Parameter(Mandatory)]$SeedManager)

    $alpha = New-PersonalityParameters `
        -ArchetypeId "Decisive-Prototype" `
        -ForceConcentrationRatio 9 `
        -MobilityBias 6 `
        -OffenseDefenseWeight 8 `
        -RiskAppetite 8 `
        -TimePreference 7 `
        -TargetingLogic 9 `
        -FormationRigidity 8 `
        -PerceptionRadius 8 `
        -PursuitThreshold 3 `
        -RetreatThreshold 8

    $beta = New-PersonalityParameters `
        -ArchetypeId "IronWall-Prototype" `
        -ForceConcentrationRatio 4 `
        -MobilityBias 3 `
        -OffenseDefenseWeight 3 `
        -RiskAppetite 2 `
        -TimePreference 3 `
        -TargetingLogic 7 `
        -FormationRigidity 9 `
        -PerceptionRadius 8 `
        -PursuitThreshold 8 `
        -RetreatThreshold 3

    $randAlpha = New-DeterministicRandom -SeedManager $SeedManager -StreamKey "init.alpha"
    $randBeta = New-DeterministicRandom -SeedManager $SeedManager -StreamKey "init.beta"

    $units = [ordered]@{}

    for ($i = 0; $i -lt 3; $i++) {
        $unitId = "A$($i + 1)"
        $jitterX = ($randAlpha.NextDouble() - 0.5) * 6.0
        $jitterY = ($randAlpha.NextDouble() - 0.5) * 6.0
        $units[$unitId] = New-UnitState `
            -UnitId $unitId `
            -FleetId "Alpha" `
            -Position (New-Vector2 -X (36.0 + $jitterX) -Y (38.0 + ($i * 20.0) + $jitterY)) `
            -Velocity (New-Vector2 -X 0.5 -Y 0.0) `
            -MaxSpeed 5.5
    }

    for ($i = 0; $i -lt 3; $i++) {
        $unitId = "B$($i + 1)"
        $jitterX = ($randBeta.NextDouble() - 0.5) * 6.0
        $jitterY = ($randBeta.NextDouble() - 0.5) * 6.0
        $units[$unitId] = New-UnitState `
            -UnitId $unitId `
            -FleetId "Beta" `
            -Position (New-Vector2 -X (80.0 + $jitterX) -Y (38.0 + ($i * 20.0) + $jitterY)) `
            -Velocity (New-Vector2 -X (-0.5) -Y 0.0) `
            -MaxSpeed 5.5
    }

    $fleets = [ordered]@{
        Alpha = New-FleetState -FleetId "Alpha" -Parameters $alpha -UnitIds @("A1", "A2", "A3")
        Beta  = New-FleetState -FleetId "Beta" -Parameters $beta -UnitIds @("B1", "B2", "B3")
    }

    return (New-BattleState -Dt 1.0 -ArenaSize 120.0 -UnitsById $units -FleetsById $fleets)
}

function Write-TickSummary {
    param([Parameter(Mandatory)]$FinalState)

    $interesting = @(
        $FinalState.TickLog | Where-Object { ($_.Tick % 10 -eq 0) -or ($_.Tick -eq $FinalState.Tick) }
    )

    if ($interesting.Count -eq 0) {
        return
    }

    Write-Host "Tick summaries:"
    foreach ($entry in $interesting) {
        $line = "Tick {0}" -f $entry.Tick
        foreach ($fleetId in $entry.Fleets.Keys) {
            $fleet = $entry.Fleets[$fleetId]
            $line += " | {0}: units={1}, hp={2}, cohesion={3}" -f $fleetId, $fleet.AliveUnits, $fleet.HitPoints, $fleet.Cohesion
        }
        Write-Host $line
    }
}

$seedManager = New-SeedManager -RootSeed $RootSeed

$runA = Invoke-BattleSimulation -InitialState (New-InitialBattleState -SeedManager $seedManager) -MaxTicks $MaxTicks
$runB = Invoke-BattleSimulation -InitialState (New-InitialBattleState -SeedManager $seedManager) -MaxTicks $MaxTicks

$deterministicReplay = ($runA.Signature -eq $runB.Signature)

Write-Host "Fleet Sandbox deterministic battle run"
Write-Host "Seed: $RootSeed"
Write-Host "Ticks executed: $($runA.FinalState.Tick)"
Write-Host "Winner: $($runA.Winner)"
Write-Host "Deterministic replay match: $deterministicReplay"
Write-Host ""

Write-TickSummary -FinalState $runA.FinalState

Write-Host ""
Write-Host "Final fleet status:"
foreach ($fleetId in $runA.FinalState.Fleets.Keys) {
    $alive = $runA.FinalState.Fleets[$fleetId].UnitIds.Count
    $hp = [Math]::Round((Get-FleetTotalHitPoints -State $runA.FinalState -FleetId $fleetId), 2)
    Write-Host ("{0}: alive_units={1}, hp_total={2}" -f $fleetId, $alive, $hp)
}

Write-Host ""
Write-Host "Signature:"
Write-Host $runA.Signature
