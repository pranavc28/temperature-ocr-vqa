import json
from typing import Dict, List, Tuple
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Bucketing Function
# -----------------------------
def bucket_question(q: str) -> str:
    q_lower = q.lower().strip()

    # 1. No ',' and '&' in the question
    if ',' not in q and '&' not in q:
        if q_lower.startswith(("what", "who", "when", "where", "why", "which", "whom", "whose", "how")):
            return "Wh Questions"
        return "Most open ended questions"

    # 2. Only ',' or '&' in the question (one, not both)
    if (',' in q) ^ ('&' in q):  # XOR: only one present
        return "Medium open ended questions"

    # 3. Both ',' and '&' in the question
    if ',' in q and '&' in q:
        return "Least open ended questions"

    # 4. "wh" starting questions (fallback)
    if q_lower.startswith(("what", "who", "when", "where", "why", "which", "whom", "whose", "how")):
        return "Wh Questions"

    # 5. Questions not in the above buckets
    return "Other"


def build_clusters(path: str) -> Dict[str, List[str]]:
    with open(path, "r") as f:
        raw = json.load(f)

    # Collect all questions from one temperature key (questions repeat across temps)
    first_key = next(iter(raw))
    clusters: Dict[str, List[str]] = {
        "Most open ended questions": [],
        "Medium open ended questions": [],
        "Least open ended questions": [],
        "Both , and &": [],
        "Wh Questions": [],
        "Other": [],
    }

    for question in raw[first_key].keys():
        cname = bucket_question(question)
        clusters[cname].append(question)

    return clusters


# -----------------------------
# Data Loading
# -----------------------------
def load_data(path: str) -> Tuple[np.ndarray, List[float], Dict[str, Dict[float, float]]]:
    """Load JSON data into a usable structure."""
    with open(path, "r") as f:
        raw = json.load(f)

    per_q: Dict[str, Dict[float, float]] = {}
    temps_set = set()
    for t_str, qd in raw.items():
        t = float(t_str)
        temps_set.add(t)
        for q, stats in qd.items():
            per_q.setdefault(q, {})
            per_q[q][t] = float(stats["accuracy"])

    temps = sorted(list(temps_set))
    return np.array(temps, dtype=float), temps, per_q


# -----------------------------
# Matrix + Plotting
# -----------------------------
def make_cluster_matrix(
    cluster_questions: List[str], temps: List[float], per_q: Dict[str, Dict[float, float]]
) -> Tuple[np.ndarray, List[str]]:
    """Build a (num_questions × num_temps) accuracy matrix for the given cluster."""
    rows = []
    present_qs = []
    for q in cluster_questions:
        if q not in per_q:
            continue
        row = [per_q[q].get(t, np.nan) for t in temps]
        rows.append(row)
        present_qs.append(q)
    if not rows:
        return np.zeros((0, len(temps))), present_qs
    return np.array(rows, dtype=float), present_qs


def plot_cluster_heatmap(cname: str, matrix: np.ndarray, qlabels: List[str], temps: List[float]) -> None:
    """Save a heatmap for one cluster."""
    plt.figure(figsize=(10, 6))
    im = plt.imshow(matrix, aspect="auto", vmin=0.0, vmax=1.0)
    plt.xticks(range(len(temps)), [str(t) for t in temps], rotation=45, ha="right")
    plt.yticks(range(len(qlabels)), qlabels, fontsize=8)
    plt.xlabel("Temperature")
    plt.ylabel("Question")
    plt.title(f"Heatmap — {cname}")
    cbar = plt.colorbar(im)
    cbar.set_label("Accuracy")
    plt.tight_layout()
    out_path = f"{cname.replace(' ', '_').lower()}_heatmap.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved {out_path}")


def plot_cluster_avg_line(cname: str, matrix: np.ndarray, temps: List[float]) -> None:
    """Save a line plot of average accuracy per temperature."""
    if matrix.size == 0:
        return
    avg_acc = np.nanmean(matrix, axis=0)

    plt.figure(figsize=(8, 5))
    plt.plot(temps, avg_acc, marker="o")
    plt.ylim(0, 1)
    plt.xlabel("Temperature")
    plt.ylabel("Average Accuracy")
    plt.title(f"Average Accuracy vs Temperature — {cname}")
    plt.grid(True, linestyle="--", alpha=0.6)
    out_path = f"{cname.replace(' ', '_').lower()}_avg.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved {out_path}")


# -----------------------------
# Main
# -----------------------------
def main():
    JSON_PATH = "temperature_accuracy_data.json"

    # Auto-generate clusters
    CLUSTERS = build_clusters(JSON_PATH)

    temps_arr, temps, per_q = load_data(JSON_PATH)

    for cname, qlist in CLUSTERS.items():
        matrix, qlabels = make_cluster_matrix(qlist, temps, per_q)
        if matrix.size == 0:
            print(f"Skipping {cname} (no data)")
            continue

        # Save heatmap
        plot_cluster_heatmap(cname, matrix, qlabels, temps)

        # Save average accuracy line plot
        plot_cluster_avg_line(cname, matrix, temps)


if __name__ == "__main__":
    main()
