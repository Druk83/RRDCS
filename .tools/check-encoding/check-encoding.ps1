param(
    [string[]]$Paths = @(".")
)

$ErrorActionPreference = "Stop"

$rg = Get-Command rg -ErrorAction SilentlyContinue
if (-not $rg) {
    Write-Error "ripgrep (rg) is required. Install rg and rerun this script."
    exit 2
}

$excludeGlobs = @(
    "!.git/**",
    "!target/**",
    "!server/target/**",
    "!client/node_modules/**",
    "!client/dist/**"
)

# Detect common mojibake patterns without non-ASCII literals in the script.
$patterns = @(
    "\uFFFD",
    "[\u0403\u0409\u040A\u040B\u040E\u040F\u0453\u0459\u045A\u045B\u045E\u045F]",
    "(\u0420[\u0410-\u044F\u0401\u0451]){3,}",
    "(\u0421[\u0410-\u044F\u0401\u0451]){3,}",
    "(\u0420[\u0410-\u044F\u0401\u0451]\u0421[\u0410-\u044F\u0401\u0451]){2,}",
    "([\u00D0\u00D1])[A-Za-z]{2,}"
)

$args = @("--line-number", "--with-filename", "--color", "never", "--hidden")
foreach ($glob in $excludeGlobs) {
    $args += @("-g", $glob)
}
foreach ($pattern in $patterns) {
    $args += @("-e", $pattern)
}
$args += $Paths

$output = & rg @args 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Encoding check failed. Suspicious strings found:"
    $output
    exit 1
}

if ($LASTEXITCODE -eq 1) {
    Write-Host "OK: no suspicious encoding patterns were found."
    exit 0
}

Write-Error "rg failed with exit code $LASTEXITCODE."
exit $LASTEXITCODE
