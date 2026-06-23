import argparse
import json
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "results" / "log_final.jsonl"
DEFAULT_OUTPUT = REPO_ROOT / "assets" / "relative_gaps.png"
DEFAULT_ZOOM_MIN_SIZE = 200

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-mini-project-opt")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PREFERRED_ALGORITHM_ORDER = ["ACO", "ALNS", "GA", "Greedy", "HC", "SA", "TS"]
IGNORED_KEYS = {"size", "capacity"}


def load_records(log_path):
    records = []

    with log_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {log_path}:{line_no}") from exc

            if "size" not in record:
                raise ValueError(f"Missing 'size' at {log_path}:{line_no}")

            records.append(record)

    if not records:
        raise ValueError(f"No records found in {log_path}")

    return sorted(records, key=lambda record: record["size"])


def get_algorithm_names(records):
    names = set()

    for record in records:
        for key, value in record.items():
            if key in IGNORED_KEYS:
                continue
            if isinstance(value, list) and value:
                names.add(key)

    preferred = [name for name in PREFERRED_ALGORITHM_ORDER if name in names]
    remaining = sorted(names - set(preferred))

    return preferred + remaining


def extract_relative_gap(record, algorithm):
    value = record.get(algorithm)

    if not isinstance(value, list) or not value:
        return None

    # value[0] is the relative gap. value[1] is the runtime string and is ignored.
    return float(value[0])


def plot_lines(ax, records, algorithms, markers):
    sizes = [record["size"] for record in records]
    x_positions = list(range(len(sizes)))

    for idx, algorithm in enumerate(algorithms):
        gaps = [extract_relative_gap(record, algorithm) for record in records]
        ax.plot(
            x_positions,
            gaps,
            marker=markers[idx % len(markers)],
            linewidth=2,
            markersize=5,
            label=algorithm,
        )

    ax.set_xticks(x_positions, sizes, rotation=45)
    ax.set_ylabel("Relative gap (%)")
    ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.5)


def get_max_gap(records, algorithms):
    gaps = []

    for record in records:
        for algorithm in algorithms:
            gap = extract_relative_gap(record, algorithm)
            if gap is not None:
                gaps.append(gap)

    if not gaps:
        raise ValueError("No relative gap values found in the selected records")

    return max(gaps)


def plot_relative_gaps(records, output_path, zoom_min_size):
    algorithms = get_algorithm_names(records)

    if not algorithms:
        raise ValueError("No algorithm columns found in the log records")

    zoom_records = [record for record in records if record["size"] >= zoom_min_size]
    if not zoom_records:
        zoom_records = records

    markers = ["o", "s", "^", "D", "v", "P", "X", "*", "h"]
    fig, (overview_ax, zoom_ax) = plt.subplots(
        2,
        1,
        figsize=(13, 9),
        gridspec_kw={"height_ratios": [2, 1.35]},
    )

    plot_lines(overview_ax, records, algorithms, markers)
    overview_ax.set_title("Relative Gap by Problem Size")

    plot_lines(zoom_ax, zoom_records, algorithms, markers)
    zoom_ax.set_title(f"Zoomed View for n >= {zoom_records[0]['size']}")
    zoom_ax.set_xlabel("Size n")

    zoom_top = get_max_gap(zoom_records, algorithms) * 1.15
    zoom_ax.set_ylim(0, max(1.0, zoom_top))

    handles, labels = overview_ax.get_legend_handles_labels()
    fig.legend(handles, labels, title="Algorithm", loc="upper right", ncol=2)
    fig.tight_layout(rect=(0, 0, 0.84, 1))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot algorithm relative gaps from results/log_final.jsonl."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the JSONL log file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path to the output PNG image.",
    )
    parser.add_argument(
        "--zoom-min-size",
        type=int,
        default=DEFAULT_ZOOM_MIN_SIZE,
        help="Smallest problem size to include in the zoomed subplot.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    records = load_records(args.input)
    plot_relative_gaps(records, args.output, args.zoom_min_size)
    print(f"[info] Saved visualization to: {args.output}")


if __name__ == "__main__":
    main()
