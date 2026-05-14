"""go2cj-v2 — Go → 仓颉转换器（基于 CodeT5-small 微调）。

二代方案：复用 go2cj 的词法/分块/结构提升流水线，但把 chunk 级翻译核心从
"从零训 0.6 M 参数 Transformer" 替换为"基于 Salesforce/codet5-small (~60 M
参数，T5 enc-dec，预训练含 Go 等 6 语言代码语料) 的微调模型"。

底座模型由 ``scripts/download_base.sh`` 放到 ``base_model/``；微调模型由
``python -m go2cj_v3.train`` 写到 ``go2cj_v3/finetuned/``。
"""

from .converter import ConversionResult, convert_source

__all__ = ["ConversionResult", "convert_source"]
