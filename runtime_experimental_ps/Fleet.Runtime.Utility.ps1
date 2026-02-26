Set-StrictMode -Version Latest

function Get-EnemyCohesionEstimate {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)][string]$FleetId,
        [Parameter(Mandatory)]$LastFleetCohesion
    )

    $opponents = @(Get-OpponentFleetIds -State $Snapshot -FleetId $FleetId)
    if ($opponents.Count -eq 0) {
        return 0.0
    }

    $sum = 0.0
    foreach ($enemyFleetId in $opponents) {
        $sum += [double]$LastFleetCohesion[$enemyFleetId]
    }

    return ($sum / $opponents.Count)
}

function Invoke-UtilityLayer {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)]$TargetLayerOutput,
        [Parameter(Mandatory)]$LastFleetCohesion
    )

    $decisionByUnit = [ordered]@{}
    $adjustedVectors = [ordered]@{}

    foreach ($unitId in $TargetLayerOutput.TargetVectors.Keys) {
        $targetVector = $TargetLayerOutput.TargetVectors[$unitId]
        $unit = $Snapshot.Units[$unitId]
        $fleet = $Snapshot.Fleets[$unit.FleetId]
        $params = $fleet.Parameters.Normalized

        $tp = [double]$params.TimePreference
        $ra = [double]$params.RiskAppetite
        $pursuitThreshold = [double]$params.PursuitThreshold
        $retreatThreshold = [double]$params.RetreatThreshold

        $immediateValue = [double]$targetVector.EngagementIntensity
        $futureValue = [double](1.0 - $targetVector.DistanceScore)

        $lambda = 0.15 + (1.35 * $tp)
        $discountedFutureValue = $futureValue * [Math]::Exp(-1.0 * $lambda * $Snapshot.Dt)
        $utilityValue = $immediateValue + $discountedFutureValue

        $commitThreshold = 0.60 - (0.25 * $ra)
        $cautiousThreshold = 0.30 - (0.10 * $ra)

        $decision = "Disengage"
        $intensityScale = 0.15
        if ($utilityValue -ge $commitThreshold) {
            $decision = "Commit"
            $intensityScale = 1.0
        } elseif ($utilityValue -ge $cautiousThreshold) {
            $decision = "Cautious"
            $intensityScale = 0.60
        }

        $ownCohesion = [double]$LastFleetCohesion[$fleet.FleetId]
        $enemyCohesion = Get-EnemyCohesionEstimate -Snapshot $Snapshot -FleetId $fleet.FleetId -LastFleetCohesion $LastFleetCohesion

        $ownCollapseSignal = 1.0 - $ownCohesion
        $enemyCollapseSignal = 1.0 - $enemyCohesion

        if ($ownCollapseSignal -gt $retreatThreshold) {
            $decision = "Disengage"
            $intensityScale = 0.0
        } elseif ($enemyCollapseSignal -gt $pursuitThreshold -and $decision -ne "Disengage") {
            $decision = "Commit"
            $intensityScale = [Math]::Max($intensityScale, 1.0)
        }

        $adjustedIntensity = Clamp-Scalar -Value ($targetVector.EngagementIntensity * $intensityScale) -Min 0.0 -Max 1.0

        $decisionByUnit[$unitId] = [pscustomobject]@{
            UnitId                = $unitId
            FleetId               = $fleet.FleetId
            DecisionSignal        = $decision
            ImmediateValue        = $immediateValue
            ExpectedFutureValue   = $futureValue
            UtilityValue          = $utilityValue
            OwnCollapseSignal     = $ownCollapseSignal
            EnemyCollapseSignal   = $enemyCollapseSignal
        }

        $adjustedVectors[$unitId] = [pscustomobject]@{
            UnitId               = $unitId
            TargetUnitId         = $targetVector.TargetUnitId
            TargetDirection      = $targetVector.TargetDirection
            EngagementIntensity  = $adjustedIntensity
            DecisionSignal       = $decision
        }
    }

    return [pscustomobject]@{
        DecisionByUnit = $decisionByUnit
        AdjustedVectors = $adjustedVectors
    }
}
