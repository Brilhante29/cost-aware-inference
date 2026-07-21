param(
  [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message)
}

function Require-File {
  param([string]$RelativePath)
  if (-not (Test-Path -LiteralPath (Join-Path $root $RelativePath) -PathType Leaf)) {
    Add-Failure "Missing file: $RelativePath"
  }
}

function Invoke-Checked {
  param([string]$Label, [scriptblock]$Command)
  & $Command
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "$Label failed with exit code $LASTEXITCODE"
  }
  $global:LASTEXITCODE = 0
}

$requiredFiles = @(
  "README.md",
  "project.yaml",
  "REFERENCES.md",
  "AGENTS.md",
  "Dockerfile",
  ".dockerignore",
  "data/fixtures/requests.jsonl",
  "data/pricing/providers.json",
  "benchmarks/results/cost-aware-baseline.json",
  "tools/validate-benchmark.py",
  "tools/validate-runtime.py",
  "sdd/spec.md",
  "sdd/benchmark-plan.md",
  "sdd/architecture-decision.md",
  "sdd/technical-decision.md",
  "sdd/agent-handoff.md",
  "sdd/reuse-improvement-review.md"
)
foreach ($file in $requiredFiles) { Require-File $file }

$reuseReviewPath = Join-Path $root "sdd/reuse-improvement-review.md"
if (Test-Path -LiteralPath $reuseReviewPath -PathType Leaf) {
  $reuseReview = Get-Content -Raw -LiteralPath $reuseReviewPath
  if ($reuseReview -match "<id>|<project-name>") {
    Add-Failure "Reuse improvement review still contains template placeholders"
  }
  $requiredFinalGatePatterns = @(
    "(?m)^- \[x\] Reusable improvements were patched or recorded\.\r?$",
    "(?m)^- \[x\] Project-specific implementation was not moved into the kit\.\r?$",
    "(?m)^- \[x\] Validation reflects .+\.\r?$"
  )
  foreach ($pattern in $requiredFinalGatePatterns) {
    if ($reuseReview -notmatch $pattern) {
      Add-Failure "Reuse improvement review final gate is incomplete: $pattern"
    }
  }
}

Push-Location -LiteralPath $root
$previousPythonPath = $env:PYTHONPATH
try {
  $srcPath = Join-Path $root "src"
  $env:PYTHONPATH = if ($previousPythonPath) {
    $srcPath + [System.IO.Path]::PathSeparator + $previousPythonPath
  } else {
    $srcPath
  }
  Invoke-Checked "runtime validation" { python tools/validate-runtime.py }

  $legacy = ("ro" + "che" + "do")
  $patterns = @($legacy, ($legacy.Substring(0,1).ToUpper() + $legacy.Substring(1)))
  $searchFiles = Get-ChildItem -Path $root -Recurse -File | Where-Object {
    $normalized = $_.FullName -replace "\\", "/"
    $normalized -notmatch "/.git/" -and
    $normalized -notmatch "/data/runtime/" -and
    $_.Extension -in @(".md", ".yaml", ".yml", ".json", ".ps1", ".py", ".js", ".ts", ".tsx", ".go", ".kt", ".java")
  }
  $forbidden = Select-String -Path $searchFiles.FullName -Pattern $patterns -SimpleMatch -ErrorAction SilentlyContinue
  if ($forbidden) { Add-Failure "Forbidden legacy project nickname found" }

  if (-not $SkipDocker) {
    Invoke-Checked "docker build" { docker build -t cost-aware-inference $root | Out-Null }
  }
} finally {
  $env:PYTHONPATH = $previousPythonPath
  Pop-Location
}

if ($failures.Count -gt 0) {
  $failures | ForEach-Object { Write-Error $_ }
  exit 1
}

Write-Host "portfolio project validation passed"
