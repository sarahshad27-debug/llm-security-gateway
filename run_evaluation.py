"""
run_evaluation.py
Runs the full evaluation dataset through the gateway and produces:
  - results/evaluation_results.csv
  - results/metrics_summary.json
  - Printed confusion matrix and per-language breakdown
"""

import csv
import json
import os
import time
from policy_engine import process_input
from injection_detector import calculate_injection_score  # for rule-only baseline

os.makedirs("results", exist_ok=True)

EVAL_PATH = "data/final_eval.csv"
RESULTS_PATH = "results/evaluation_results.csv"
METRICS_PATH = "results/metrics_summary.json"


# ── Helpers ───────────────────────────────────────────────────────────────────

def rule_only_decision(prompt: str) -> str:
    """Simulate rule-only baseline (midterm approach)."""
    score = calculate_injection_score(prompt)
    if score >= 1:
        return "BLOCK"
    return "ALLOW"


def compute_metrics(true_labels: list, pred_labels: list, positive_class="BLOCK"):
    """Compute accuracy, precision, recall, F1, FP, FN."""
    tp = sum(1 for t, p in zip(true_labels, pred_labels) if t == positive_class and p == positive_class)
    tn = sum(1 for t, p in zip(true_labels, pred_labels) if t != positive_class and p != positive_class)
    fp = sum(1 for t, p in zip(true_labels, pred_labels) if t != positive_class and p == positive_class)
    fn = sum(1 for t, p in zip(true_labels, pred_labels) if t == positive_class and p != positive_class)

    accuracy  = round((tp + tn) / max(len(true_labels), 1), 4)
    precision = round(tp / max(tp + fp, 1), 4)
    recall    = round(tp / max(tp + fn, 1), 4)
    f1        = round(2 * precision * recall / max(precision + recall, 1e-9), 4)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn
    }


def policy_match(expected: str, predicted: str) -> bool:
    """
    For binary BLOCK detection: treat MASK and ALLOW as non-BLOCK.
    For full 3-class: exact match.
    """
    return expected.strip().upper() == predicted.strip().upper()


# ── Main evaluation loop ──────────────────────────────────────────────────────

def run_evaluation():
    print("=" * 60)
    print("LLM Security Gateway — Evaluation Script")
    print("=" * 60)

    rows = []
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} prompts from {EVAL_PATH}\n")

    results = []
    true_labels_hybrid  = []
    pred_labels_hybrid  = []
    true_labels_rule    = []
    pred_labels_rule    = []
    latencies_hybrid    = []
    latencies_rule      = []

    # Per-language tracking
    lang_results = {}

    for row in rows:
        prompt          = row["prompt"]
        expected_policy = row["expected_policy"].strip().upper()
        language        = row.get("language", "en")
        attack_type     = row.get("attack_type", "unknown")

        # --- Hybrid (full gateway) ---
        t0 = time.time()
        hybrid_result = process_input(prompt, input_id=row["id"])
        hybrid_latency = round((time.time() - t0) * 1000, 2)
        hybrid_decision = hybrid_result["decision"]

        # --- Rule-only baseline ---
        t1 = time.time()
        rule_decision = rule_only_decision(prompt)
        rule_latency = round((time.time() - t1) * 1000, 2)

        hybrid_correct = policy_match(expected_policy, hybrid_decision)
        rule_correct   = policy_match(expected_policy, rule_decision)

        true_labels_hybrid.append(expected_policy)
        pred_labels_hybrid.append(hybrid_decision)
        true_labels_rule.append(expected_policy)
        pred_labels_rule.append(rule_decision)
        latencies_hybrid.append(hybrid_latency)
        latencies_rule.append(rule_latency)

        # Per-language tracking
        if language not in lang_results:
            lang_results[language] = {"total": 0, "correct": 0, "fp": 0, "fn": 0}
        lang_results[language]["total"] += 1
        if hybrid_correct:
            lang_results[language]["correct"] += 1
        elif expected_policy == "BLOCK" and hybrid_decision != "BLOCK":
            lang_results[language]["fn"] += 1
        elif expected_policy != "BLOCK" and hybrid_decision == "BLOCK":
            lang_results[language]["fp"] += 1

        result_row = {
            "id": row["id"],
            "prompt": prompt[:80],
            "language": language,
            "attack_type": attack_type,
            "expected_policy": expected_policy,
            "hybrid_decision": hybrid_decision,
            "rule_decision": rule_decision,
            "hybrid_correct": hybrid_correct,
            "rule_correct": rule_correct,
            "rule_score": hybrid_result.get("rule_score", 0),
            "semantic_score": hybrid_result.get("semantic_score", 0),
            "final_risk": hybrid_result.get("final_risk", 0),
            "reason_codes": "|".join(hybrid_result.get("reason_codes", [])),
            "hybrid_latency_ms": hybrid_latency,
            "rule_latency_ms": rule_latency,
        }
        results.append(result_row)

        status = "✓" if hybrid_correct else "✗"
        print(f"[{status}] ID {row['id']:>3} | Expected: {expected_policy:<5} | "
              f"Hybrid: {hybrid_decision:<5} | Rule: {rule_decision:<5} | "
              f"Lang: {language:<5} | {prompt[:50]}")

    # ── Write results CSV ──────────────────────────────────────────────────────
    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"\nResults written to {RESULTS_PATH}")

    # ── Compute metrics ────────────────────────────────────────────────────────
    hybrid_metrics = compute_metrics(true_labels_hybrid, pred_labels_hybrid)
    rule_metrics   = compute_metrics(true_labels_rule,   pred_labels_rule)

    # 3-class accuracy (ALLOW/MASK/BLOCK exact match)
    hybrid_exact = sum(1 for r in results if r["hybrid_correct"]) / len(results)
    rule_exact   = sum(1 for r in results if r["rule_correct"])   / len(results)

    # Latency stats
    def latency_stats(lat_list):
        sorted_lat = sorted(lat_list)
        n = len(sorted_lat)
        return {
            "mean_ms":   round(sum(sorted_lat) / n, 2),
            "median_ms": round(sorted_lat[n // 2], 2),
            "p95_ms":    round(sorted_lat[int(n * 0.95)], 2),
        }

    # Per-language recall
    lang_breakdown = {}
    for lang, data in lang_results.items():
        lang_breakdown[lang] = {
            "total": data["total"],
            "correct": data["correct"],
            "accuracy": round(data["correct"] / max(data["total"], 1), 4),
            "false_positives": data["fp"],
            "false_negatives": data["fn"],
        }

    # Error analysis
    errors = [r for r in results if not r["hybrid_correct"]]
    error_analysis = [
        {
            "id": e["id"],
            "prompt": e["prompt"],
            "expected": e["expected_policy"],
            "predicted": e["hybrid_decision"],
            "attack_type": e["attack_type"],
            "rule_score": e["rule_score"],
            "semantic_score": e["semantic_score"],
        }
        for e in errors
    ]

    summary = {
        "dataset": {
            "total_prompts": len(results),
            "benign": sum(1 for r in results if r["expected_policy"] == "ALLOW"),
            "mask": sum(1 for r in results if r["expected_policy"] == "MASK"),
            "block": sum(1 for r in results if r["expected_policy"] == "BLOCK"),
        },
        "hybrid_metrics_block_detection": hybrid_metrics,
        "rule_only_metrics_block_detection": rule_metrics,
        "exact_3class_accuracy": {
            "hybrid": round(hybrid_exact, 4),
            "rule_only": round(rule_exact, 4),
        },
        "latency": {
            "hybrid": latency_stats(latencies_hybrid),
            "rule_only": latency_stats(latencies_rule),
        },
        "per_language_accuracy": lang_breakdown,
        "error_analysis": error_analysis,
        "total_errors": len(errors),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Metrics written to {METRICS_PATH}")

    # ── Print summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"\n{'Metric':<25} {'Hybrid':>10} {'Rule-Only':>10}")
    print("-" * 47)
    for key in ["accuracy", "precision", "recall", "f1", "false_positives", "false_negatives"]:
        print(f"{key:<25} {str(hybrid_metrics[key]):>10} {str(rule_metrics[key]):>10}")

    print(f"\n{'3-Class Accuracy':<25} {hybrid_exact:>10.4f} {rule_exact:>10.4f}")

    print(f"\n{'Mode':<15} {'Mean':>8} {'Median':>8} {'P95':>8}")
    print("-" * 41)
    for mode, lats in [("Hybrid", latency_stats(latencies_hybrid)),
                       ("Rule-Only", latency_stats(latencies_rule))]:
        print(f"{mode:<15} {lats['mean_ms']:>8} {lats['median_ms']:>8} {lats['p95_ms']:>8}")

    print(f"\nPer-Language Accuracy:")
    print(f"  {'Language':<10} {'Total':>6} {'Correct':>8} {'Accuracy':>10}")
    print("  " + "-" * 36)
    for lang, data in lang_breakdown.items():
        print(f"  {lang:<10} {data['total']:>6} {data['correct']:>8} {data['accuracy']:>10.4f}")

    print(f"\nTotal errors: {len(errors)} / {len(results)}")
    if errors:
        print("\nError cases:")
        for e in errors[:10]:
            print(
                f"  ID {e['id']:>3}: Expected {e.get('expected', 'N/A')}, Got {e.get('predicted', 'N/A')} — {e.get('prompt', '')[:60]}")

    print("\nEvaluation complete.")


if __name__ == "__main__":
    run_evaluation()