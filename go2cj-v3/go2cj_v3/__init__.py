"""go2cj-v3 — Go → 仓颉转换器（基于 CodeT5p-220m 微调）。

三代方案：在 [go2cj-v2](../go2cj-v2) 的工程结构基础上，把底座从
``Salesforce/codet5-small`` (60.5 M params) 升级为
``Salesforce/codet5p-220m`` (220 M params, CodeT5+) ——
更大的代码先验 + 更深的 T5+ enc-dec 编码器 + 更广的预训练语料，
期望端到端 cjc 编译率 / 运行匹配率比 v2 大幅提升，转出的仓颉代码也
更贴近"仓颉最优表达"。

底座模型由 ``scripts/download_base.sh`` 放到 ``base_model/``；微调模型由
``python -m go2cj_v3.train`` 写到 ``go2cj_v3/finetuned/``。
"""

from .converter import ConversionResult, convert_source

__all__ = ["ConversionResult", "convert_source"]
