import json
import csv
import os
import sys
from collections import defaultdict

# Setup import path for src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from pii_remover import analyzer_engine

def load_docs(filepath="eval/synthetic_docs.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation():
    # Make sure we have the test documents
    if not os.path.exists("eval/synthetic_docs.json"):
        print("Test documents not found! Please run generate_test_docs.py first.")
        sys.exit(1)

    docs = load_docs()
    engine = analyzer_engine()
    
    metrics = {
        "true_positives": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "by_type": defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    }
    
    for doc in docs:
        text = doc["text"]
        expected = doc["expected_entities"]
        
        # We run the actual presidio engine used in production
        results = engine.analyze(text=text, language="en", score_threshold=0.3)
        
        detected_entities = [{"type": r.entity_type, "value": text[r.start:r.end]} for r in results]
        
        matched_detected = set()
        
        # Match expected to detected (Overlap + Type logic)
        # We use an overlap string match because Presidio might detect "John Smith" while we exact-matched "Mr. John Smith", etc.
        for exp in expected:
            exp_type = exp["type"]
            exp_val = exp["value"].lower()
            
            match_found = False
            for i, det in enumerate(detected_entities):
                if i in matched_detected:
                    continue
                    
                det_type = det["type"]
                det_val = det["value"].lower()
                
                # Check for label match
                type_match = (exp_type == det_type) or (exp_type == "PERSON" and det_type == "PERSON")
                
                # Check for string overlap: expected value in detected value, or vice versa
                if type_match and (exp_val in det_val or det_val in exp_val):
                    match_found = True
                    matched_detected.add(i)
                    break
                    
            if match_found:
                metrics["true_positives"] += 1
                metrics["by_type"][exp_type]["tp"] += 1
            else:
                metrics["false_negatives"] += 1
                metrics["by_type"][exp_type]["fn"] += 1
                
        # Unmatched detections count as false positives (if we care about that type)
        expected_types = {e["type"] for e in expected}
        for i, det in enumerate(detected_entities):
            if i not in matched_detected and det["type"] in expected_types:
                metrics["false_positives"] += 1
                metrics["by_type"][det["type"]]["fp"] += 1

    # Calculation helper
    def calc_prf(tp, fp, fn):
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0
        return p, r, f1

    overall_p, overall_r, overall_f1 = calc_prf(
        metrics["true_positives"], metrics["false_positives"], metrics["false_negatives"]
    )
    
    # Render Output
    print("=" * 60)
    print("                 EVALUATION RESULTS                 ")
    print("=" * 60)
    print(f"Overall Precision: {overall_p:.2%}")
    print(f"Overall Recall:    {overall_r:.2%}")
    print(f"Overall F1 Score:  {overall_f1:.2%}")
    print("-" * 60)
    print(f"{'Entity Type':<20} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10}")
    print("-" * 60)
    
    summary = {
        "overall": {"precision": round(overall_p, 4), "recall": round(overall_r, 4), "f1": round(overall_f1, 4)},
        "by_type": {}
    }
    
    for ent_type, counts in metrics["by_type"].items():
        p, r, f1 = calc_prf(counts["tp"], counts["fp"], counts["fn"])
        summary["by_type"][ent_type] = {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}
        print(f"{ent_type:<20} | {p:<10.2%} | {r:<10.2%} | {f1:<10.2%}")
    print("=" * 60)
    
    # Save reports
    with open("eval/results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    with open("eval/results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Entity Type", "Precision", "Recall", "F1 Score"])
        writer.writerow(["OVERALL", overall_p, overall_r, overall_f1])
        for ent_type, s in summary["by_type"].items():
            writer.writerow([ent_type, s["precision"], s["recall"], s["f1"]])
            
    print("Saved evaluation reports to eval/results.json and eval/results.csv")

if __name__ == "__main__":
    run_evaluation()
