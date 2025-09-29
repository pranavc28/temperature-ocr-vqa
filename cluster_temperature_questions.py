import json
import os
from typing import Dict, List, Tuple
import statistics


def load_temperature_accuracy(path: str) -> Dict[str, Dict[str, float]]:
    with open(path, "r") as f:
        raw = json.load(f)
    # Build question -> temp -> accuracy map
    question_to_temp_to_acc: Dict[str, Dict[str, float]] = {}
    for temp_str, qdict in raw.items():
        for question, metrics in qdict.items():
            acc = metrics.get("accuracy")
            if acc is None:
                # Skip if missing
                continue
            if question not in question_to_temp_to_acc:
                question_to_temp_to_acc[question] = {}
            question_to_temp_to_acc[question][temp_str] = float(acc)
    return question_to_temp_to_acc


def linear_regression_slope(xs: List[float], ys: List[float]) -> float:
    # Simple OLS slope without numpy: slope = cov(x,y)/var(x)
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    var_x = sum((x - mean_x) ** 2 for x in xs)
    if var_x == 0:
        return 0.0
    cov_xy = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    return cov_xy / var_x


def is_non_monotonic_significant(values: List[float], eps: float = 0.01) -> bool:
    # Detect both positive and negative significant steps
    deltas = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    has_pos = any(d > eps for d in deltas)
    has_neg = any(d < -eps for d in deltas)
    return has_pos and has_neg


def cluster_questions(q_to_ta: Dict[str, Dict[str, float]]) -> Tuple[Dict[str, List[dict]], List[dict]]:
    # Clusters
    clusters: Dict[str, List[dict]] = {
        "Low-temperature optimal": [],
        "Mid-temperature optimal": [],
        "High-temperature optimal": [],
        "Temperature-robust": [],
        "Temperature-sensitive": [],
    }

    # Sort temperatures once
    all_temp_strs = set()
    for temp_map in q_to_ta.values():
        all_temp_strs.update(temp_map.keys())
    sorted_temps = sorted([float(t) for t in all_temp_strs])
    sorted_temp_strs = [f"{t:.1f}" for t in sorted_temps]

    all_rows: List[dict] = []

    for question, temp_to_acc in q_to_ta.items():
        # Ensure consistent order and handle missing temps by skipping
        temps_present = [t for t in sorted_temp_strs if t in temp_to_acc]
        xs = [float(t) for t in temps_present]
        ys = [temp_to_acc[t] for t in temps_present]
        if not xs:
            continue

        mean_acc = sum(ys) / len(ys)
        std_acc = statistics.pstdev(ys) if len(ys) > 1 else 0.0
        max_acc = max(ys)
        min_acc = min(ys)
        acc_range = max_acc - min_acc
        slope = linear_regression_slope(xs, ys)

        # Best temperature: choose the lowest temp among ties to prefer determinism
        best_indices = [i for i, v in enumerate(ys) if abs(v - max_acc) < 1e-12]
        best_temp = xs[min(best_indices)]

        # Heuristics
        ROBUST_STD = 0.015
        ROBUST_RANGE = 0.02
        NONMONO_EPS = 0.015

        is_robust = std_acc <= ROBUST_STD or acc_range <= ROBUST_RANGE
        non_monotonic = is_non_monotonic_significant(ys, eps=NONMONO_EPS)

        cluster_name: str
        if is_robust:
            cluster_name = "Temperature-robust"
        else:
            if best_temp <= 0.2 + 1e-9:
                cluster_name = "Low-temperature optimal"
            elif best_temp >= 0.8 - 1e-9:
                cluster_name = "High-temperature optimal"
            elif 0.4 - 1e-9 <= best_temp <= 0.6 + 1e-9:
                cluster_name = "Mid-temperature optimal"
            else:
                # Fallback to slope and sensitivity
                if non_monotonic and acc_range >= 0.05:
                    cluster_name = "Temperature-sensitive"
                else:
                    cluster_name = "High-temperature optimal" if slope > 0 else "Low-temperature optimal"

        row = {
            "question": question,
            "cluster": cluster_name,
            "best_temperature": round(best_temp, 1),
            "best_accuracy": round(max_acc, 4),
            "mean_accuracy": round(mean_acc, 4),
            "std_accuracy": round(std_acc, 4),
            "slope": round(slope, 4),
            "accuracies": {t: round(temp_to_acc[t], 4) for t in temps_present},
        }
        clusters[cluster_name].append(row)
        all_rows.append(row)

    # Sort entries within clusters by question for consistency
    for lst in clusters.values():
        lst.sort(key=lambda r: r["question"].lower())

    # Sort overall rows
    all_rows.sort(key=lambda r: (r["cluster"], r["question"].lower()))

    return clusters, all_rows


def write_outputs(clusters: Dict[str, List[dict]], rows: List[dict], out_dir: str) -> None:
    clusters_path = os.path.join(out_dir, "temperature_clusters.json")
    with open(clusters_path, "w") as f:
        json.dump(clusters, f, indent=2)

    # Summary markdown
    summary_path = os.path.join(out_dir, "CLUSTERING_SUMMARY.md")
    lines: List[str] = []
    lines.append("## Temperature-based Clustering Summary")
    lines.append("")
    # Counts
    lines.append("### Cluster sizes")
    for cname in [
        "Low-temperature optimal",
        "Mid-temperature optimal",
        "High-temperature optimal",
        "Temperature-robust",
        "Temperature-sensitive",
    ]:
        lines.append(f"- {cname}: {len(clusters.get(cname, []))}")
    lines.append("")

    # Criteria
    lines.append("### Criteria")
    lines.append("- Low-temperature optimal: Best accuracy at T<=0.2 or decreasing trend.")
    lines.append("- Mid-temperature optimal: Best accuracy at T in {0.4, 0.6}.")
    lines.append("- High-temperature optimal: Best accuracy at T>=0.8 or increasing trend.")
    lines.append("- Temperature-robust: Accuracy nearly flat across temperatures (std<=0.015 or range<=0.02).")
    lines.append("- Temperature-sensitive: Non-monotonic with notable swings (range>=0.05).")
    lines.append("")

    # Detailed table
    lines.append("### Per-question overview")
    lines.append("Question | Cluster | Best T | Best Acc | Mean | Std | Slope")
    lines.append("--- | --- | --- | --- | --- | --- | ---")
    for r in rows:
        lines.append(
            f"{r['question']} | {r['cluster']} | {r['best_temperature']:.1f} | {r['best_accuracy']:.3f} | "
            f"{r['mean_accuracy']:.3f} | {r['std_accuracy']:.3f} | {r['slope']:.3f}"
        )

    with open(summary_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "temperature_accuracy_data.json")
    q_to_ta = load_temperature_accuracy(data_path)
    clusters, rows = cluster_questions(q_to_ta)
    write_outputs(clusters, rows, base_dir)
    print("Wrote temperature_clusters.json and CLUSTERING_SUMMARY.md")


if __name__ == "__main__":
    main()


