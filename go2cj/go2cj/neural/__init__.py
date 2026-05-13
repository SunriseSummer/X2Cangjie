"""Neural Go → Cangjie translation subpackage.

Contains the synthetic training-corpus generator (:mod:`.corpus`), the
word-level tokenizer / vocabulary (:mod:`.vocab`), the PyTorch
Transformer encoder-decoder seq2seq model (:mod:`.model`), the training
loop (:mod:`.train`) and the runtime translator (:mod:`.translator`).

The training corpus is **generated** from a small set of Go chunk
*skeletons* by randomly substituting names / types / expressions /
bodies — there is no hand-coded rule lookup at inference time.
"""

from __future__ import annotations
