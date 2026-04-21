# Witness compiler (minimal tree)

This directory contains **only** what is needed to build and run:

- **`witnessc`** — C++ compiler for `.wit` files (`make`).
- **`tree_fold_cuda`** — external CUDA satisfiability solver used when `witnessc` runs with `--solver=external`.

## Build `witnessc`

Requires: **g++** (C++17), **bison**, **flex**.

```bash
make clean && make
```

Produces `./witnessc` in this directory.

## Build `tree_fold_cuda` (optional, GPU solver)

Requires: **CUDA toolkit** (`nvcc`), **Intel TBB**, **libzstd** — see typical flags:

```bash
nvcc -arch=native -std=c++17 tree_fold_cuda.cu -o tree_fold_cuda -ltbb -lzstd
```

(`-arch=` must match your GPU.)

## Run

Run `witnessc` from a working directory where solver outputs should be written (this project uses `results/zdd/`). Ensure `./tree_fold_cuda` is available on **`PATH`** or as **`./tree_fold_cuda` in that working directory** (symlink from `methods/witness/` if needed).

```bash
./witnessc --solver=external --quiet /path/to/model.wit
```
