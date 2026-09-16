---
name: max-throughput
description: Makes coding agents use the full machine - probes CPU/GPU/RAM, parallelizes independent work (multi-GPU DDP, per-GPU packing, pytest-xdist, make -j), then profiles the running job to find the real bottleneck and tune batch size, DataLoader workers, and pre-encoding.
---

# Max Throughput

Teaches Claude Code (and other coding agents) to stop running an expensive
machine single-threaded. The default objective becomes **minimum wall-clock
completion time**: measure the hardware first, dispatch independent work
concurrently, then profile the running job and tune the measured bottleneck
instead of guessing knobs.

## When to Use This Skill

- Launching model training, fine-tuning, evaluation, or benchmarks on a machine with one or more GPUs
- Running builds, test suites, data preprocessing, or dataset generation that could be parallelized
- A job is slower than expected and you need to find the actual bottleneck before tuning
- Deciding whether to pre-encode / pre-tokenize a dataset or raise DataLoader workers

## What This Skill Does

1. **Resource discovery**: probes CPU cores, RAM, free VRAM per GPU, and disk, then proposes a concrete parallel execution plan (worker counts, free GPU list, torchrun command).
2. **Aggressive-but-safe parallelism**: converts `python train.py` into `torchrun --standalone --nproc_per_node=<N>`, packs independent experiments one per GPU via `CUDA_VISIBLE_DEVICES`, uses `pytest -n auto` for tests and `-j$(nproc)` for builds, shards preprocessing across workers.
3. **Profiling-led tuning**: samples GPU/CPU utilization of the running job, classifies the bottleneck (data pipeline, compute, VRAM, I/O, under-occupancy), and maps it to the right knob: batch size, num_workers/prefetch, pre-encode, AMP/bf16, torch.compile.

## How to Use

### Basic Usage

```
Before running my training script, inspect the machine and launch it with maximum safe parallelism.
```

### Advanced Usage

```
This training run feels slow. Profile it while it runs, tell me the real bottleneck,
and apply the tuning playbook (batch size / dataloader workers / pre-encode) one knob at a time.
```

## Example

**User**: "Train the model on this 8-GPU box, as fast as possible."

**Output**: The agent runs the resource probe, finds 8 free GPUs, launches
`torchrun --standalone --nproc_per_node=8 train.py` with `OMP_NUM_THREADS=1`,
sets DataLoader `num_workers` from measurement, then samples `nvidia-smi`
during the run - sees spiky GPU utilization with high CPU, concludes the JPEG
decode pipeline is starving the GPUs, and pre-encodes the dataset to uint8
tensors before resuming.

**Source:** [Promethe-us/max-throughput](https://github.com/Promethe-us/max-throughput)

## Tips

- Change ONE tuning knob at a time and re-measure throughput; two changes at once tell you nothing.
- Benchmark the DataLoader alone first: if its throughput already exceeds GPU consumption, the data pipeline is not the problem.
- Stop tuning when a change buys less than ~5% - spend the remaining effort on launching more concurrent work instead.

## Common Use Cases

- Multi-GPU training that is accidentally running on a single GPU
- Experiment sweeps serialized on one GPU while seven sit idle
- Test suites and preprocessing loops that never touch more than one core
- GPU utilization spiking 0%-100% due to a starved input pipeline
