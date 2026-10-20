$ErrorActionPreference = 'Stop'

$documentPath = Join-Path $PSScriptRoot '..\docs\技术方案.md'
$document = Get-Content -Raw -Encoding UTF8 $documentPath

Describe '技术方案约束' {
    It '明确使用 Python 和 PySide6' {
        $document | Should Match 'Python 3\.12\+'
        $document | Should Match 'PySide6 / Qt 6'
    }

    It '明确项目只支持 Windows' {
        $document | Should Match '仅支持 Windows 10/11'
    }

    It '覆盖文档要求的核心能力' {
        $document | Should Match '透明背景'
        $document | Should Match 'QMovie'
        $document | Should Match '本地配置'
        $document | Should Match '系统托盘'
        $document | Should Match 'PyInstaller'
    }

    It '没有把已删除的害怕动作重新加入状态列表' {
        $document | Should Not Match '包含：.*害怕'
    }
}
