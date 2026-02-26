Set-StrictMode -Version Latest

function ConvertTo-NormalizedParameter {
    param([double]$Value)

    if ($Value -lt 1.0 -or $Value -gt 10.0) {
        throw "Parameter value $Value is outside canonical domain [1,10]."
    }

    return (($Value - 1.0) / 9.0)
}

function New-PersonalityParameters {
    param(
        [Parameter(Mandatory)][string]$ArchetypeId,
        [Parameter(Mandatory)][double]$ForceConcentrationRatio,
        [Parameter(Mandatory)][double]$MobilityBias,
        [Parameter(Mandatory)][double]$OffenseDefenseWeight,
        [Parameter(Mandatory)][double]$RiskAppetite,
        [Parameter(Mandatory)][double]$TimePreference,
        [Parameter(Mandatory)][double]$TargetingLogic,
        [Parameter(Mandatory)][double]$FormationRigidity,
        [Parameter(Mandatory)][double]$PerceptionRadius,
        [Parameter(Mandatory)][double]$PursuitThreshold,
        [Parameter(Mandatory)][double]$RetreatThreshold
    )

    $raw = [ordered]@{
        ForceConcentrationRatio = $ForceConcentrationRatio
        MobilityBias            = $MobilityBias
        OffenseDefenseWeight    = $OffenseDefenseWeight
        RiskAppetite            = $RiskAppetite
        TimePreference          = $TimePreference
        TargetingLogic          = $TargetingLogic
        FormationRigidity       = $FormationRigidity
        PerceptionRadius        = $PerceptionRadius
        PursuitThreshold        = $PursuitThreshold
        RetreatThreshold        = $RetreatThreshold
    }

    $normalized = [ordered]@{}
    foreach ($entry in $raw.GetEnumerator()) {
        $normalized[$entry.Key] = ConvertTo-NormalizedParameter -Value $entry.Value
    }

    return [pscustomobject]@{
        ArchetypeId = $ArchetypeId
        Raw         = [pscustomobject]$raw
        Normalized  = [pscustomobject]$normalized
    }
}

function New-UnitState {
    param(
        [Parameter(Mandatory)][string]$UnitId,
        [Parameter(Mandatory)][string]$FleetId,
        [Parameter(Mandatory)]$Position,
        [Parameter(Mandatory)]$Velocity,
        [double]$HitPoints = 100.0,
        [double]$MaxHitPoints = 100.0,
        [double]$MaxSpeed = 5.0
    )

    return [pscustomobject]@{
        UnitId        = $UnitId
        FleetId       = $FleetId
        Position      = New-Vector2 -X $Position.X -Y $Position.Y
        Velocity      = New-Vector2 -X $Velocity.X -Y $Velocity.Y
        HitPoints     = $HitPoints
        MaxHitPoints  = $MaxHitPoints
        MaxSpeed      = $MaxSpeed
    }
}

function New-FleetState {
    param(
        [Parameter(Mandatory)][string]$FleetId,
        [Parameter(Mandatory)]$Parameters,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]]$UnitIds
    )

    return [pscustomobject]@{
        FleetId     = $FleetId
        Parameters  = $Parameters
        UnitIds     = @($UnitIds)
    }
}

function Copy-UnitState {
    param([Parameter(Mandatory)]$Unit)

    return (New-UnitState `
        -UnitId $Unit.UnitId `
        -FleetId $Unit.FleetId `
        -Position $Unit.Position `
        -Velocity $Unit.Velocity `
        -HitPoints $Unit.HitPoints `
        -MaxHitPoints $Unit.MaxHitPoints `
        -MaxSpeed $Unit.MaxSpeed)
}

function Copy-BattleStateSnapshot {
    param([Parameter(Mandatory)]$State)

    $units = [ordered]@{}
    foreach ($unitId in $State.Units.Keys) {
        $units[$unitId] = Copy-UnitState -Unit $State.Units[$unitId]
    }

    $fleets = [ordered]@{}
    foreach ($fleetId in $State.Fleets.Keys) {
        $fleet = $State.Fleets[$fleetId]
        $fleets[$fleetId] = New-FleetState -FleetId $fleet.FleetId -Parameters $fleet.Parameters -UnitIds $fleet.UnitIds
    }

    $lastFleetCohesion = [ordered]@{}
    foreach ($fleetId in $State.LastFleetCohesion.Keys) {
        $lastFleetCohesion[$fleetId] = [double]$State.LastFleetCohesion[$fleetId]
    }

    return [pscustomobject]@{
        Tick              = [int]$State.Tick
        Dt                = [double]$State.Dt
        ArenaSize         = [double]$State.ArenaSize
        Units             = $units
        Fleets            = $fleets
        LastFleetCohesion = $lastFleetCohesion
    }
}

function New-BattleState {
    param(
        [Parameter(Mandatory)][double]$Dt,
        [Parameter(Mandatory)][double]$ArenaSize,
        [Parameter(Mandatory)]$UnitsById,
        [Parameter(Mandatory)]$FleetsById
    )

    $lastFleetCohesion = [ordered]@{}
    foreach ($fleetId in $FleetsById.Keys) {
        $lastFleetCohesion[$fleetId] = 1.0
    }

    return [pscustomobject]@{
        Tick              = 0
        Dt                = $Dt
        ArenaSize         = $ArenaSize
        Units             = $UnitsById
        Fleets            = $FleetsById
        LastFleetCohesion = $lastFleetCohesion
        TickLog           = @()
    }
}

function Get-AliveUnitIdsForFleet {
    param(
        [Parameter(Mandatory)]$State,
        [Parameter(Mandatory)][string]$FleetId
    )

    $unitIds = @()
    foreach ($unitId in $State.Fleets[$FleetId].UnitIds) {
        if ($State.Units.Contains($unitId) -and $State.Units[$unitId].HitPoints -gt 0.0) {
            $unitIds += $unitId
        }
    }

    return $unitIds
}

function Get-OpponentFleetIds {
    param(
        [Parameter(Mandatory)]$State,
        [Parameter(Mandatory)][string]$FleetId
    )

    return @($State.Fleets.Keys | Where-Object { $_ -ne $FleetId })
}
