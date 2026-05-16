"""Self-Organizing Incremental Neural Network (SOINN) — dynamic substrate.

Background
----------
SOINN was introduced by Furao & Hasegawa in:

* Furao S., Hasegawa O., 2006. *An incremental network for on-line
  unsupervised classification and topology learning*. Neural Networks
  19 (1): 90-106.
* Furao S., Ogura T., Hasegawa O., 2007. *An enhanced self-organizing
  incremental neural network for online unsupervised learning*.

Unlike a Kohonen Self-Organizing Map (SOM), whose neuron count is
**fixed at design time**, SOINN starts empty and adds / removes
neurons on-line as data flows in.  Neurons that are co-active
develop edges (Hebbian-style topology growth); edges that are not
refreshed age out and die.  The result is a graph whose size and
connectivity match the *intrinsic* complexity of the data — a much
better match for biological cortex than a fixed-size tensor.

We adopt SOINN as the substrate for CHIME but specialise it for
discrete HDC code:

* The "stimulus" is a 2048-bit bipolar hypervector of an
  anonymized Go chunk (see :mod:`.hdc`).
* Each neuron stores **two** hypervectors: a Go-side
  *prototype* (its receptive field on the input) and a Cj-side
  *prototype* (the associated output).  Neurons therefore
  embody the entire Go→Cj cross-modal association rather than only
  acting as a quantizer of one modality.
* New neurons are added with vigilance threshold ``insert_thresh``;
  when an input lies within the threshold of an existing best-match
  unit (BMU), the BMU's prototype is shifted toward the input (online
  averaging).  Both behaviours follow standard SOINN; the difference is
  that we use **HDC similarity** instead of Euclidean distance.

The auxiliary fields ``win_count`` and ``age`` are SOINN's standard
homeostasis-and-pruning signals: rarely-used neurons can be culled,
old edges decay.  In this prototype we keep them all to maximise recall
on the small (~300-pair) trainset.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from . import hdc


@dataclass
class Neuron:
    """A single SOINN node.

    Attributes
    ----------
    hv_in : np.ndarray
        The Go-side prototype hypervector (the neuron's receptive
        field — what input it likes to fire for).
    template_in : str
        Anonymized Go template (token-space string) — preserved
        verbatim so we have a textual readout for debugging.
    template_out : str
        Anonymized Cangjie template — emitted on activation.
    win_count : int
        How many times this neuron has been the BMU.  Inverse of
        novelty; used by the criticality controller to shape firing.
    avg_error : float
        Running similarity score with its winners — proxy for the
        SOINN "local error" quantity.
    """

    hv_in: np.ndarray
    template_in: str
    template_out: str
    win_count: int = 0
    avg_error: float = 0.0


@dataclass
class SOINN:
    """A growing graph of :class:`Neuron` with Hebbian edge formation."""

    insert_thresh: float = 0.55
    edge_max_age: int = 200
    neurons: List[Neuron] = field(default_factory=list)
    # Edges: undirected, keyed by frozenset({i, j}) → age (int).
    edges: Dict[frozenset, int] = field(default_factory=dict)
    # Exact-template index for O(1) deduplication during training.  In a
    # purely vector-space SOINN duplicate inputs would shift an existing
    # prototype; for our discrete-template setting that risks merging
    # neurons whose Cangjie outputs disagree.  Keep the templates
    # discrete and only let HD similarity drive *retrieval*.
    _by_template_in: Dict[str, int] = field(default_factory=dict)

    # ----- core operations ------------------------------------------------ #

    def _topk(self, hv: np.ndarray, k: int = 2) -> List[Tuple[int, float]]:
        """Return the top-k most similar neurons and their similarities."""
        if not self.neurons:
            return []
        sims = [hdc.similarity(n.hv_in, hv) for n in self.neurons]
        order = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
        return [(i, sims[i]) for i in order[:k]]

    def insert(self, hv_in: np.ndarray, template_in: str,
               template_out: str) -> int:
        """Add a new neuron and return its index."""
        idx = len(self.neurons)
        self.neurons.append(Neuron(
            hv_in=hv_in.copy(),
            template_in=template_in,
            template_out=template_out,
        ))
        if template_in:
            self._by_template_in[template_in] = idx
        return idx

    def observe(self, hv_in: np.ndarray, template_in: str,
                template_out: str) -> Tuple[int, float]:
        """Process one training stimulus.

        Returns ``(neuron_index, similarity_to_bmu)``.  Mutates the network:

        * Exact template-text duplicate → bump win-count of that neuron.
          We keep templates atomic because the discrete Cangjie outputs
          must not silently change when two superficially similar Go
          chunks happen to land near each other in HD space.
        * Otherwise → grow a new neuron.  Capacity is cheap (≤ 1 KiB
          per neuron) and the trainset is small (~ 300 pairs).
        * BMU-and-second pair form / refresh a Hebbian edge.  Edges
          older than :attr:`edge_max_age` are pruned (SOINN's
          habituation).
        """
        # Exact-template dedup first (deterministic, no HV drift).
        if template_in in self._by_template_in:
            idx = self._by_template_in[template_in]
            n = self.neurons[idx]
            n.win_count += 1
            # Refresh the Hebbian neighbour as if this were a normal BMU.
            top = self._topk(hv_in, k=2)
            if len(top) >= 2 and top[0][0] == idx:
                key = frozenset({idx, top[1][0]})
                self.edges[key] = 0
            return idx, 1.0

        # Fresh template → grow a neuron.
        # Compute the closest pre-existing neuron *before* inserting so
        # the Hebbian edge isn't a self-loop.
        pre = self._topk(hv_in, k=1)
        new_idx = self.insert(hv_in, template_in, template_out)
        if pre:
            key = frozenset({new_idx, pre[0][0]})
            if len(key) == 2:
                self.edges[key] = 0
        # Age all edges; prune dead ones.
        dead = []
        for key, age in self.edges.items():
            new_age = age + 1
            if new_age > self.edge_max_age:
                dead.append(key)
            else:
                self.edges[key] = new_age
        for k in dead:
            self.edges.pop(k, None)
        return new_idx, 0.0

    # ----- inference ------------------------------------------------------ #

    def best(self, hv_in: np.ndarray, k: int = 1) -> List[Tuple[int, float]]:
        """Return top-k (neuron_idx, similarity) for inference / readout."""
        return self._topk(hv_in, k=k)

    def neighbours(self, idx: int) -> List[int]:
        """Return the indices linked to neuron ``idx`` via Hebbian edges."""
        out: List[int] = []
        for key in self.edges:
            if idx in key:
                others = key - {idx}
                if others:
                    out.append(next(iter(others)))
        return out

    # ----- persistence ---------------------------------------------------- #

    def save(self, path: Path) -> None:
        """Persist the network to a ``.npz`` archive next to a small
        JSON sidecar holding the textual templates and edges."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        hv = (np.stack([n.hv_in for n in self.neurons]).astype(np.int8)
              if self.neurons else np.zeros((0, hdc.DIM), dtype=np.int8))
        np.savez_compressed(path.with_suffix(".npz"), hv=hv)
        meta = {
            "insert_thresh": self.insert_thresh,
            "edge_max_age": self.edge_max_age,
            "templates_in": [n.template_in for n in self.neurons],
            "templates_out": [n.template_out for n in self.neurons],
            "win_count": [n.win_count for n in self.neurons],
            "avg_error": [n.avg_error for n in self.neurons],
            "edges": [
                [list(k)[0], list(k)[1], age] for k, age in self.edges.items()
            ],
        }
        path.with_suffix(".json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "SOINN":
        path = Path(path)
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        arr = np.load(path.with_suffix(".npz"))["hv"]
        net = cls(
            insert_thresh=meta["insert_thresh"],
            edge_max_age=meta["edge_max_age"],
        )
        for i in range(arr.shape[0]):
            net.neurons.append(Neuron(
                hv_in=arr[i].astype(np.int8),
                template_in=meta["templates_in"][i],
                template_out=meta["templates_out"][i],
                win_count=int(meta["win_count"][i]),
                avg_error=float(meta["avg_error"][i]),
            ))
            if net.neurons[i].template_in:
                net._by_template_in[net.neurons[i].template_in] = i
        for a, b, age in meta["edges"]:
            net.edges[frozenset({int(a), int(b)})] = int(age)
        return net

    def __len__(self) -> int:
        return len(self.neurons)
