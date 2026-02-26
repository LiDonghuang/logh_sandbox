Set-StrictMode -Version Latest

function New-SeedManager {
    param([Parameter(Mandatory)][long]$RootSeed)

    return [pscustomobject]@{
        RootSeed = $RootSeed
    }
}

function Get-DerivedSeed {
    param(
        [Parameter(Mandatory)]$SeedManager,
        [Parameter(Mandatory)][string]$StreamKey
    )

    $payload = "{0}:{1}" -f $SeedManager.RootSeed, $StreamKey
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($bytes)
    } finally {
        $sha.Dispose()
    }
    $seed64 = [System.BitConverter]::ToUInt32($hash, 0)
    $signedSeed = [int]($seed64 % [int]::MaxValue)
    if ($signedSeed -lt 0) {
        $signedSeed = -1 * $signedSeed
    }
    return $signedSeed
}

function New-DeterministicRandom {
    param(
        [Parameter(Mandatory)]$SeedManager,
        [Parameter(Mandatory)][string]$StreamKey
    )

    $seed = Get-DerivedSeed -SeedManager $SeedManager -StreamKey $StreamKey
    return [System.Random]::new($seed)
}
