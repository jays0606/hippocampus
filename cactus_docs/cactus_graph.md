# Cactus Graph API

Source: https://docs.cactuscompute.com/latest/docs/cactus_graph/

A computational framework for building tensor operation graphs (PyTorch-equivalent for mobile).

## Precision Types

INT4, INT8, FP16, FP32. INT4 tensors use packed storage (2 values per byte) and automatically unpack to INT8 for computation.

## Operation Categories

**Tensor ops:** element-wise add/sub/mul/div, scalar ops, exp/log.

**Matrix ops:** matrix multiplication, transpose, reshape.

**Neural network ops:** layer normalization, RMS normalization, softmax, attention, activation functions (SiLU, GeLU, sigmoid, ReLU), convolution, recurrent ops.

**Advanced ops:** concatenation, slicing, indexing, top-K, bilinear interpolation.

## Key Features

- Automatic broadcasting for compatible tensor shapes
- Precision conversion between types
- "Build once, execute many" — construct graph once, run repeatedly with different inputs
- Save/load graphs from disk
- `hard_reset()` clears all nodes and buffers
- `soft_reset()` preserves graph structure, clears buffers
- Memory-map large tensors
- Profile execution: `execute("profile.json")`
