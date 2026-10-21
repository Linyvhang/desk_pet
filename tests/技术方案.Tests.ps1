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
        $document | Should Match 'Ctrl\+左键'
    }

    It '包含害怕状态和拖动交互' {
        $document | Should Match '包含：.*害怕'
        $document | Should Match '移动超过拖动阈值.*害怕'
    }

    It '规定滑块边界和动作回退' {
        $document | Should Match '0\.2～1\.0'
        $document | Should Match '64×64'
        $document | Should Match '每次动作播放完成后统一回到待机状态'
    }
}
