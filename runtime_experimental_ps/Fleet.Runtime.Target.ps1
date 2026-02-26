Set-StrictMode -Version Latest

function Get-EnemyUnitIdsInPerception {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)]$Unit,
        [Parameter(Mandatory)][double]$EffectiveRadius
    )

    $visible = @()
    foreach ($otherUnitId in $Snapshot.Units.Keys) {
        $other = $Snapshot.Units[$otherUnitId]
        if ($other.HitPoints -le 0.0) { continue }
        if ($other.FleetId -eq $Unit.FleetId) { continue }

        $distance = Get-Distance2D -A $Unit.Position -B $other.Position
        if ($distance -le $EffectiveRadius) {
            $visible += $otherUnitId
        }
    }

    return $visible
}

function Get-LocalDensityScore {
    param(
        [Parameter(Mandatory)]$Snapshot,
        [Parameter(Mandatory)]$CandidateUnit,
        [double]$Radius = 16.0
    )

    $sameFleetIds = @()
    foreach ($unitId in $Snapshot.Units.Keys) {
        $unit = $Snapshot.Units[$unitId]
        if ($unit.HitPoints -le 0.0) { continue }
        if ($unit.FleetId -ne $CandidateUnit.FleetId) { continue }
        if ($unit.UnitId -eq $CandidateUnit.UnitId) { continue }
        $sameFleetIds += $unitId
    }

    if ($sameFleetIds.Count -eq 0) {
        return 0.0
    }

    $neighbors = 0
    foreach ($unitId in $sameFleetIds) {
        $distance = Get-Distance2D -A $CandidateUnit.Position -B $Snapshot.Units[$unitId].Position
        if ($distance -le $Radius) {
            $neighbors += 1
        }
    }

    return ($neighbors / $sameFleetIds.Count)
}

function Invoke-TargetLayer {
    param([Parameter(Mandatory)]$Snapshot)

    $targetVectors = [ordered]@{}
    $visibleSetsByUnit = [ordered]@{}
    $featureSetsByUnit = [ordered]@{}

    foreach ($unitId in $Snapshot.Units.Keys) {
        $unit = $Snapshot.Units[$unitId]
        if ($unit.HitPoints -le 0.0) {
            continue
        }

        $fleet = $Snapshot.Fleets[$unit.FleetId]
        $params = $fleet.Parameters.Normalized

        $pr = [double]$params.PerceptionRadius
        $tl = [double]$params.TargetingLogic
        $odw = [double]$params.OffenseDefenseWeight
        $fcr = [double]$params.ForceConcentrationRatio

        $basePerceptionRadius = 65.0
        $effectiveRadius = $basePerceptionRadius * $pr
        if ($effectiveRadius -lt 5.0) {
            $effectiveRadius = 5.0
        }

        $visibleSet = @(Get-EnemyUnitIdsInPerception -Snapshot $Snapshot -Unit $unit -EffectiveRadius $effectiveRadius)
        $visibleSetsByUnit[$unitId] = @($visibleSet)

        if ($visibleSet.Count -eq 0) {
            $targetVectors[$unitId] = [pscustomobject]@{
                UnitId               = $unitId
                TargetUnitId         = $null
                TargetDirection      = New-Vector2
                EngagementIntensity  = 0.0
                TargetScore          = 0.0
                DistanceScore        = 1.0
            }

            $featureSetsByUnit[$unitId] = @()
            continue
        }

        $resolutionK = 0.9
        $perceptionResolution = 1.0 / (1.0 + ($resolutionK * $pr))

        $bestCandidate = $null
        $candidateFeatures = @()

        foreach ($candidateId in $visibleSet) {
            $candidate = $Snapshot.Units[$candidateId]

            $distance = Get-Distance2D -A $unit.Position -B $candidate.Position
            $distanceScore = Clamp-Scalar -Value ($distance / $effectiveRadius) -Min 0.0 -Max 1.0

            $densityTrue = Get-LocalDensityScore -Snapshot $Snapshot -CandidateUnit $candidate
            $isolationTrue = 1.0 - $densityTrue
            $strategicTrue = 1.0 - ($candidate.HitPoints / [Math]::Max(1.0, $candidate.MaxHitPoints))

            $densityObserved = $densityTrue * $perceptionResolution
            $isolationObserved = $isolationTrue * $perceptionResolution
            $strategicObserved = $strategicTrue * $perceptionResolution

            $w1 = $tl
            $w2 = 1.0 - $tl
            $w3 = 0.20 + (0.40 * $odw)
            $w4 = 0.20 + (0.30 * (1.0 - $fcr))

            $score = ($w1 * $densityObserved) + ($w2 * $isolationObserved) + ($w3 * $strategicObserved) - ($w4 * $distanceScore)

            $entry = [pscustomobject]@{
                CandidateId      = $candidateId
                DistanceScore    = $distanceScore
                DensityScore     = $densityObserved
                IsolationScore   = $isolationObserved
                StrategicScore   = $strategicObserved
                TargetScore      = $score
                Distance         = $distance
            }

            $candidateFeatures += $entry

            if ($null -eq $bestCandidate -or $entry.TargetScore -gt $bestCandidate.TargetScore) {
                $bestCandidate = $entry
            }
        }

        $featureSetsByUnit[$unitId] = @($candidateFeatures)

        $targetUnit = $Snapshot.Units[$bestCandidate.CandidateId]
        $targetDirection = Normalize-Vector2 -A (Subtract-Vector2 -A $targetUnit.Position -B $unit.Position)
        $baseIntensity = Clamp-Scalar -Value ((0.5 + $bestCandidate.TargetScore) * 0.9) -Min 0.0 -Max 1.0

        $targetVectors[$unitId] = [pscustomobject]@{
            UnitId               = $unitId
            TargetUnitId         = $bestCandidate.CandidateId
            TargetDirection      = $targetDirection
            EngagementIntensity  = $baseIntensity
            TargetScore          = $bestCandidate.TargetScore
            DistanceScore        = $bestCandidate.DistanceScore
        }
    }

    return [pscustomobject]@{
        VisibleSetsByUnit = $visibleSetsByUnit
        FeatureSetsByUnit = $featureSetsByUnit
        TargetVectors     = $targetVectors
    }
}
