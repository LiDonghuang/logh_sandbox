Set-StrictMode -Version Latest

function New-Vector2 {
    param(
        [double]$X = 0.0,
        [double]$Y = 0.0
    )

    return [pscustomobject]@{
        X = $X
        Y = $Y
    }
}

function Add-Vector2 {
    param(
        [Parameter(Mandatory)]$A,
        [Parameter(Mandatory)]$B
    )

    return (New-Vector2 -X ($A.X + $B.X) -Y ($A.Y + $B.Y))
}

function Subtract-Vector2 {
    param(
        [Parameter(Mandatory)]$A,
        [Parameter(Mandatory)]$B
    )

    return (New-Vector2 -X ($A.X - $B.X) -Y ($A.Y - $B.Y))
}

function Scale-Vector2 {
    param(
        [Parameter(Mandatory)]$A,
        [double]$Scalar
    )

    return (New-Vector2 -X ($A.X * $Scalar) -Y ($A.Y * $Scalar))
}

function Get-Vector2Magnitude {
    param([Parameter(Mandatory)]$A)
    return [Math]::Sqrt(($A.X * $A.X) + ($A.Y * $A.Y))
}

function Normalize-Vector2 {
    param([Parameter(Mandatory)]$A)

    $magnitude = Get-Vector2Magnitude -A $A
    if ($magnitude -le 1e-9) {
        return (New-Vector2)
    }

    return (Scale-Vector2 -A $A -Scalar (1.0 / $magnitude))
}

function Clamp-Vector2Magnitude {
    param(
        [Parameter(Mandatory)]$A,
        [double]$MaxMagnitude
    )

    $magnitude = Get-Vector2Magnitude -A $A
    if ($magnitude -le $MaxMagnitude -or $magnitude -le 1e-9) {
        return $A
    }

    return (Scale-Vector2 -A $A -Scalar ($MaxMagnitude / $magnitude))
}

function Get-Distance2D {
    param(
        [Parameter(Mandatory)]$A,
        [Parameter(Mandatory)]$B
    )

    return (Get-Vector2Magnitude -A (Subtract-Vector2 -A $A -B $B))
}

function Get-Vector2Dot {
    param(
        [Parameter(Mandatory)]$A,
        [Parameter(Mandatory)]$B
    )

    return (($A.X * $B.X) + ($A.Y * $B.Y))
}

function Rotate-VectorTowards {
    param(
        [Parameter(Mandatory)]$CurrentDirection,
        [Parameter(Mandatory)]$DesiredDirection,
        [double]$MaxRadians
    )

    $current = Normalize-Vector2 -A $CurrentDirection
    $desired = Normalize-Vector2 -A $DesiredDirection

    $dot = Get-Vector2Dot -A $current -B $desired
    if ($dot -gt 1.0) { $dot = 1.0 }
    if ($dot -lt -1.0) { $dot = -1.0 }

    $angle = [Math]::Acos($dot)
    if ($angle -le $MaxRadians -or $angle -le 1e-9) {
        return $desired
    }

    $ratio = $MaxRadians / $angle
    $interpolated = Add-Vector2 -A (Scale-Vector2 -A $current -Scalar (1.0 - $ratio)) -B (Scale-Vector2 -A $desired -Scalar $ratio)
    return (Normalize-Vector2 -A $interpolated)
}

function Clamp-Scalar {
    param(
        [double]$Value,
        [double]$Min,
        [double]$Max
    )

    if ($Value -lt $Min) { return $Min }
    if ($Value -gt $Max) { return $Max }
    return $Value
}
