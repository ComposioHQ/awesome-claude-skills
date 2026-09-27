# adversarial-review skill installer (Windows PowerShell)
[CmdletBinding()]
param(
    [string]$TargetDir = (Join-Path $env:USERPROFILE ".claude\skills")
)

$ErrorActionPreference = "Stop"

$SkillName = "adversarial-review"
$RepoUrl   = "https://github.com/RevolutionLA/adversarial-review.git"
# skills.sh 结构：skill 位于仓库的 skills/<name>/ 子目录
$SkillSub  = "skills/$SkillName"
# 归一化目标目录（去尾部分隔符），再推导备份根：
# 备份必须落在 skills 目录之外——留在里面的 `.bak.*` 带着同名
# frontmatter（name: adversarial-review），会与主 skill 抢触发路由
# （v2.1 三方评审 B4/T6 实证的缺陷）。
$TargetDir = [System.IO.Path]::GetFullPath($TargetDir.TrimEnd('\','/'))
$Dest      = Join-Path $TargetDir $SkillName
$BackupRoot = Join-Path ([System.IO.Path]::GetDirectoryName($TargetDir)) "skill-backups"

function Write-Info($m) { Write-Host "[info] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[ ok ] $m" -ForegroundColor Green }
function Write-Warn2($m){ Write-Host "[warn] $m" -ForegroundColor Yellow }
function Write-Fail($m) { Write-Host "[fail] $m" -ForegroundColor Red; exit 1 }

function Get-SkillVersion($skillMd) {
    if (-not (Test-Path $skillMd)) { return "unknown" }
    $m = Select-String -Path $skillMd -Pattern '^\s+version:\s*"?([^"\r\n]+)"?' | Select-Object -First 1
    if ($m) { return $m.Matches[0].Groups[1].Value.Trim() }
    return "unknown"
}

Write-Info "installing $SkillName -> $Dest"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("advreview-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

try {
    $hasGit = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    if ($hasGit) {
        git clone --depth 1 $RepoUrl (Join-Path $tmp "repo") 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Fail "git clone failed. Check network access to $RepoUrl" }
    }
    else {
        Write-Warn2 "git not found, falling back to zip download"
        $zipUrl = "https://codeload.github.com/RevolutionLA/$SkillName/zip/refs/heads/main"
        $zip    = Join-Path $tmp "skill.zip"
        Invoke-WebRequest -Uri $zipUrl -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath (Join-Path $tmp "x") -Force
        Move-Item (Join-Path $tmp "x\$SkillName-main") (Join-Path $tmp "repo")
    }

    $src = Join-Path $tmp ($SkillSub -replace '/', '\')
    if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
        Write-Fail "SKILL.md not found at $SkillSub — repo layout may have changed"
    }

    $newVer = Get-SkillVersion (Join-Path $src "SKILL.md")

    # 已有安装：备份而不是直接删除（用户可能有本地自定义修改）
    if (Test-Path $Dest) {
        $oldVer  = Get-SkillVersion (Join-Path $Dest "SKILL.md")
        $backup  = Join-Path $BackupRoot ($SkillName + ".bak." + (Get-Date -Format "yyyyMMddHHmmss"))
        Write-Warn2 "existing install found (version: $oldVer)"
        Write-Info "backing up to $backup (outside the skills dir, not deleting — your local edits are preserved there)"
        New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
        Move-Item $Dest $backup
        Write-Info "new version: $newVer"

        # 备份只保留最近 3 份（评审 R13）：只按本脚本自己的命名 (.bak.<时间戳>) 排序清理
        $KeepBackups = 3
        $stale = @(Get-ChildItem -Path $BackupRoot -Directory -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -match ("^" + [regex]::Escape($SkillName) + "\.bak\.") } |
                   Sort-Object Name -Descending |
                   Select-Object -Skip $KeepBackups)
        foreach ($s in $stale) {
            Remove-Item -Recurse -Force $s.FullName
            Write-Info ("pruned old backup (kept newest $KeepBackups): " + $s.Name)
        }
    }

    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    Copy-Item -Recurse -Force (Join-Path $src "*") $Dest

    # sanity check: frontmatter name must match directory name (Agent Skills spec)
    $headName = (Select-String -Path (Join-Path $Dest "SKILL.md") -Pattern '^name:\s*(.+)$' |
                 Select-Object -First 1).Matches[0].Groups[1].Value.Trim()
    if ($headName -ne $SkillName) { Write-Fail "frontmatter name '$headName' != directory '$SkillName'" }

    Write-Ok "installed: $Dest (version $newVer)"
    Write-Ok "frontmatter name verified: $headName"
    Write-Host ""
    Write-Host 'Next: restart your agent, then say "跑一次蓝军评审" or "adversarial review this module".'
}
finally {
    if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }
}
