$ErrorActionPreference = 'Stop'

$documentPath = Join-Path $PSScriptRoot '..\产品设计文档.md'
$document = Get-Content -Raw -Encoding UTF8 $documentPath

Describe '产品设计文档批注约束' {
    It '声明透明背景不显示额外内容' {
        $document | Should Match '透明背景模式下不显示额外内容'
    }

    It '不再包含害怕或害羞动作' {
        $document | Should Not Match '害怕|害羞'
    }

    It '将特定互动限定为生气状态' {
        $document | Should Match '特定互动：只触发生气状态'
    }
}
