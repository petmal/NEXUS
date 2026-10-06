# Parallelism assessment

Assessment date: 2026-10-06. Runtime: CPython 3.14.7, pinned project dependencies.

## Current solver

Minimax is recursive Python control flow over mutable Pydantic state objects, dictionaries,
frozenset beliefs, and a large shared transposition table. Branches overlap heavily. Splitting
recursive branches between processes duplicates state/memo work, serializes large objects, and
loses short-circuit wins. A multiprocessing Manager dictionary in this hot path would introduce
IPC for fine-grained lookups. No framework alone removes these algorithmic costs.

The independent per-hypothesis physical solves are easy to distribute, but diagnostic seed-17
P3 measurements put them below one second of about 150 seconds total. Even eliminating that
phase would improve the whole generation by less than one percent in that measured case.
Parallelizing requested action values also forfeits reuse of the minimax memo; it needs a
separate measured design, not a blind executor wrapper.

## CPU options

- ProcessPoolExecutor: chosen for the PoC's independent-episode batch. Standard library,
  explicit spawn context, bounded worker count, one cold child per episode, per-case timeout,
  deterministic result identifiers, and parent-only atomic checkpoint writes. This improves
  throughput; it does not reduce the search work of an individual episode. Worker RSS is
  reported per child, not mislabeled as aggregate peak memory.
- ThreadPoolExecutor: the current interpreter has the GIL; CPU-bound Python search does not
  gain ordinary multicore execution simply by using threads. Free-threaded Python would need
  separate dependency, global-cache safety and performance validation.
- InterpreterPoolExecutor: supports multicore execution in Python 3.14, but a local import
  probe failed with `ImportError: module pydantic_core._pydantic_core does not support loading
  in subinterpreters`. Not viable with the pinned stack.
- Joblib/loky, Ray and Dask: useful for other scheduling/distributed requirements, but unnecessary
  dependencies for this bounded local batch. They do not make the shared recursive search
  efficiently parallel. Revisit only if distributed preparation becomes an actual requirement.

Default to one worker. Size concurrency from CPU quota and measured memory, not os.cpu_count
alone. The execution container exposes an eight-CPU quota and 8 GiB memory. Two baseline P3
workers at roughly 4 GiB each are unsafe here; only test multiple optimized workers after
measuring their RSS. Never parallelize baseline and optimized cases to estimate single-case
speedup; use a separate throughput experiment with the same case set.

## GPU options

The current solver is not an easy GPU port. NVIDIA's maintained numba-cuda package implements
CUDA kernels with restricted Python features and SIMT execution. The existing object graph,
dynamic memo tables, Pydantic transitions and recursive branching cannot be transferred with
a decorator. A GPU backend would require compact numeric state arrays, batched transition
evaluation and a redesigned search frontier, then new exact-equivalence proofs.

T1's dense signatures are a more plausible GPU target than minimax. This PoC constructs its
compact universe in about 0.03 seconds, however; device startup/transfers are unlikely to be
worth pursuing at this scale. No CUDA device is exposed in this environment, so no GPU
performance result is claimed. GPU implementation is not recommended for the next phase.

## Primary references

- Python 3.14 executors, process isolation, pickle and interpreter constraints:
  https://docs.python.org/3.14/library/concurrent.futures.html
- NVIDIA maintained CUDA Python support and restrictions:
  https://nvidia.github.io/numba-cuda/user/cudapysupported.html
- Numba's built-in CUDA target moved to NVIDIA numba-cuda:
  https://numba.readthedocs.io/en/stable/cuda/index.html

Measured batch results and final recommendation are in performance-poc-findings.md.

Subinterpreter compatibility can be reproduced without running generation:

```python
from concurrent.futures import InterpreterPoolExecutor
with InterpreterPoolExecutor(max_workers=1) as pool:
    pool.submit(eval, "__import__('nexus.models.episode', fromlist=['PrivateEpisode']).PrivateEpisode.__name__").result()
```
