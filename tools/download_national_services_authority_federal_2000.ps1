$ErrorActionPreference = 'Stop'

# Downloads fictional training telemetry, then shifts every timestamp together
# so a short Splunk/Wise lookback window can see the newest event.
$source = 'national_services_authority_wise_federal_2000.json'
$output = 'national_services_authority_wise_federal_latest.json'
$url = 'https://raw.githubusercontent.com/AnamulPalash/trxwise/main/data/national_services_authority_wise_federal_2000.json'

Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $source
$lines = [IO.File]::ReadAllLines((Join-Path (Get-Location).Path $source))
$timestampPattern = [regex]'"timestamp":"([^"]+)"'
$latest = [DateTimeOffset]::MinValue

foreach ($line in $lines) {
  $match = $timestampPattern.Match($line)
  if (-not $match.Success) { throw 'A JSON record is missing timestamp.' }
  $candidate = [DateTimeOffset]::Parse($match.Groups[1].Value)
  if ($candidate -gt $latest) { $latest = $candidate }
}

$shift = [DateTimeOffset]::UtcNow - $latest
$updated = foreach ($line in $lines) {
  $match = $timestampPattern.Match($line)
  $newTimestamp = ([DateTimeOffset]::Parse($match.Groups[1].Value).Add($shift)).UtcDateTime.ToString('yyyy-MM-ddTHH:mm:ssZ')
  $line.Replace($match.Value, ('"timestamp":"' + $newTimestamp + '"'))
}

[IO.File]::WriteAllLines((Join-Path (Get-Location).Path $output), [string[]]$updated, [Text.UTF8Encoding]::new($false))
Write-Host ("Created {0} with {1} synthetic events. Latest timestamp: {2}" -f $output, $updated.Count, [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))
