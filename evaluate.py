import json
import os
from typing import Dict, List, Set
from extractor import MockLocalExtractor
import database

def calculate_metrics(predicted: Set[str], ground_truth: Set[str]) -> Dict[str, float]:
    """
    Calculates Precision, Recall, and F1-score for a single document.
    """
    if not ground_truth and not predicted:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not predicted:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not ground_truth:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    true_positives = len(predicted.intersection(ground_truth))
    precision = true_positives / len(predicted) if predicted else 0.0
    recall = true_positives / len(ground_truth) if ground_truth else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": true_positives,
        "predicted_count": len(predicted),
        "ground_truth_count": len(ground_truth)
    }

def run_evaluation(
    ground_truth_path: str = "data/ground_truth.json",
    sample_data_dir: str = "sample_data"
):
    """
    Evaluates extraction accuracy against the manually labeled ground-truth set.
    Note: Evaluates extraction quality only. Does not rank candidates.
    """
    if not os.path.exists(ground_truth_path):
        raise FileNotFoundError(f"Ground truth file not found at: {ground_truth_path}")

    with open(ground_truth_path, "r", encoding="utf-8") as f:
        ground_truth: Dict[str, List[str]] = json.load(f)

    extractor = MockLocalExtractor()
    total_tp = 0
    total_predicted = 0
    total_expected = 0

    print("=" * 65)
    print("RESUME SKILL EXTRACTION - ACCURACY EVALUATION REPORT")
    print("=" * 65)

    for filename, expected_skills in ground_truth.items():
        file_path = os.path.join(sample_data_dir, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {filename} not found in {sample_data_dir}, skipping.")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        pred_skills = extractor.extract_skills(content)
        pred_set = set(pred_skills)
        gt_set = set(expected_skills)

        metrics = calculate_metrics(pred_set, gt_set)
        total_tp += metrics.get("tp", 0)
        total_predicted += metrics.get("predicted_count", 0)
        total_expected += metrics.get("ground_truth_count", 0)

        print(f"\nDocument: {filename}")
        print(f" - Ground Truth ({len(gt_set)}): {sorted(list(gt_set))}")
        print(f" - Extracted    ({len(pred_set)}): {sorted(list(pred_set))}")
        print(f" - Precision: {metrics['precision']:.2%} | Recall: {metrics['recall']:.2%} | F1: {metrics['f1']:.2%}")

    # Micro-average overall
    overall_prec = total_tp / total_predicted if total_predicted > 0 else 0.0
    overall_rec = total_tp / total_expected if total_expected > 0 else 0.0
    overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0.0

    print("\n" + "=" * 65)
    print("OVERALL PERFORMANCE SUMMARY:")
    print(f" - Overall Precision : {overall_prec:.2%}")
    print(f" - Overall Recall    : {overall_rec:.2%}")
    print(f" - Overall F1-Score  : {overall_f1:.2%}")
    print("=" * 65)

if __name__ == "__main__":
    run_evaluation()
