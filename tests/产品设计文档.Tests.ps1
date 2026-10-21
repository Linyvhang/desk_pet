$ErrorActionPreference = 'Stop'

$documentPath = Join-Path $PSScriptRoot '..\产品设计文档.md'
$document = Get-Content -Raw -Encoding UTF8 $documentPath

Describe '产品设计文档批注约束' {
    It '声明透明背景不显示额外内容' {
        $document | Should Match '透明背景模式下不显示额外内容'
    }

    It '包含拖动触发的害怕动作' {
        $document | Should Match '拖动.*害怕|害怕.*拖动'
    }

    It '将特定互动限定为生气状态' {
        $document | Should Match '特定互动：只触发生气状态'
    }

    It '规定滑块范围和鼠标响应' {
        $document | Should Match '20%～100%'
        $document | Should Match '64×64'
        $document | Should Match '鼠标响应'
    }

    It '规定动作完成后回到待机' {
        $document | Should Match '每次动作播放完成后统一回到待机状态'
    }
}
