#!/usr/bin/env python3
"""llama-bench YAML wrapper — run parameterized benchmarks and collect CSV results."""

import argparse
import csv
import io
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml


# Maps YAML config keys → llama-bench CLI flags
PARAM_FLAGS = {
    "model": "-m",
    "hf_repo": "-hf",
    "hf_file": "-hff",
    "hf_token": "-hft",
    "n_prompt": "-p",
    "n_gen": "-n",
    "pg": "-pg",
    "n_depth": "-d",
    "batch_size": "-b",
    "ubatch_size": "-ub",
    "cache_type_k": "-ctk",
    "cache_type_v": "-ctv",
    "threads": "-t",
    "cpu_mask": "-C",
    "cpu_strict": "--cpu-strict",
    "poll": "--poll",
    "n_gpu_layers": "-ngl",
    "n_cpu_moe": "-ncmoe",
    "split_mode": "-sm",
    "main_gpu": "-mg",
    "no_kv_offload": "-nkvo",
    "flash_attn": "-fa",
    "device": "-dev",
    "mmap": "-mmp",
    "direct_io": "-dio",
    "embeddings": "-embd",
    "tensor_split": "-ts",
    "override_tensor": "-ot",
    "no_op_offload": "-nopo",
    "no_host": "--no-host",
    "fit_target": "-fitt",
    "fit_ctx": "-fitc",
    "repetitions": "-r",
    "delay": "--delay",
    "prio": "--prio",
    "numa": "--numa",
}

# Keys consumed by this wrapper, not passed to llama-bench
WRAPPER_KEYS = {"name", "llama_bench"}


def parse_k_suffix(val):
    """Convert '32k' → 32768, '128k' → 131072, etc. Other values pass through."""
    if isinstance(val, str) and val.lower().endswith("k") and val[:-1].lstrip("-").isdigit():
        return int(val[:-1]) * 1024
    return val


def to_flag_value(val):
    if isinstance(val, list):
        return ",".join(str(parse_k_suffix(v)) for v in val)
    return str(parse_k_suffix(val))


def resolve_models(val, model_map):
    """Replace model alias(es) with their paths; unknown values pass through."""
    if isinstance(val, list):
        return [model_map.get(v, v) for v in val]
    return model_map.get(val, val)


def build_bench_args(run_params, defaults):
    merged = {**defaults, **run_params}
    # "iterations" is the preferred alias for "repetitions" (-r)
    if "iterations" in merged:
        merged["repetitions"] = merged.pop("iterations")
    args = []
    for key, flag in PARAM_FLAGS.items():
        if key in merged:
            args.extend([flag, to_flag_value(merged[key])])
    # Pass through any flags set via boolean keys (no-warmup, progress, verbose)
    for key in ("no_warmup", "progress", "verbose"):
        if merged.get(key):
            args.append(f"--{key.replace('_', '-')}")
    return args


def parse_csv_output(text):
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return rows, reader.fieldnames or []


class Logger:
    """Tees messages to stderr and an optional log file."""

    def __init__(self, log_path: Path | None):
        self._file = None
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            self._file = open(log_path, "w", encoding="utf-8")

    def log(self, msg: str = ""):
        print(msg, file=sys.stderr)
        if self._file:
            print(msg, file=self._file)

    def close(self):
        if self._file:
            self._file.close()
            self._file = None


def main():
    parser = argparse.ArgumentParser(
        description="Run llama-bench from a YAML config and write results to CSV."
    )
    parser.add_argument("config", help="YAML config file")
    parser.add_argument("--output", "-o", help="Override output CSV path from config")
    parser.add_argument("--log", "-l", help="Log file path (default: <output>.log)")
    parser.add_argument(
        "--no-log", action="store_true", help="Disable log file output"
    )
    parser.add_argument(
        "--bench", default=None, help="Path to llama-bench binary (overrides config)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing"
    )
    parser.add_argument(
        "--append", action="store_true", help="Append to output CSV instead of overwriting"
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_output = args.output or config.get("output", f"results/bench_{timestamp}.csv")
    output_path = Path(raw_output.replace("{timestamp}", timestamp))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.no_log or args.dry_run:
        log_path = None
    elif args.log:
        log_path = Path(args.log)
    else:
        log_path = output_path.with_suffix(".log")

    logger = Logger(log_path)

    if log_path:
        logger.log(f"# llama-bench run  {timestamp}")
        logger.log(f"# config: {config_path}")
        logger.log(f"# output: {output_path}")
        logger.log("")

    bench_bin = args.bench or config.get("llama_bench", "llama-bench")
    defaults = config.get("defaults", {})
    model_map = config.get("models", {})
    runs = config.get("runs", [])

    if not runs:
        print("No runs defined in config.", file=sys.stderr)
        sys.exit(1)

    all_rows = []
    fieldnames = None

    for i, run in enumerate(runs):
        run_name = run.get("name", f"run_{i+1}")
        run_bin = run.get("llama_bench", bench_bin)
        run_params = {k: v for k, v in run.items() if k not in WRAPPER_KEYS}
        if "model" in run_params and model_map:
            run_params["model"] = resolve_models(run_params["model"], model_map)
        bench_args = build_bench_args(run_params, defaults)
        cmd = [run_bin, "-o", "csv"] + bench_args

        if args.dry_run:
            print(f"[{run_name}]  " + " ".join(cmd))
            continue

        logger.log(f"→ {run_name}")
        if log_path:
            logger.log(f"  cmd: {' '.join(cmd)}")

        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if result.stderr:
            for line in result.stderr.splitlines():
                logger.log(f"  {line}")

        if result.returncode != 0:
            logger.log(f"  FAILED (exit {result.returncode})")
            continue

        rows, fields = parse_csv_output(result.stdout)
        if not rows:
            logger.log("  no output rows")
            continue

        if fieldnames is None:
            fieldnames = ["run_name"] + list(fields)

        for row in rows:
            all_rows.append({"run_name": run_name, **row})

        logger.log(f"  {len(rows)} row(s)")

    if args.dry_run:
        logger.close()
        return

    if not all_rows:
        logger.log("No results to write.")
        logger.close()
        sys.exit(1)

    mode = "a" if args.append and output_path.exists() else "w"
    write_header = mode == "w" or not output_path.exists()

    with open(output_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(all_rows)

    logger.log(f"\nWrote {len(all_rows)} row(s) → {output_path}")
    if log_path:
        logger.log(f"Log → {log_path}")

    logger.close()


if __name__ == "__main__":
    main()
