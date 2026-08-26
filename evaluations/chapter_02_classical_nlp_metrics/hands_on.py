"""
Chapter 2: Classical NLP Metrics - Hands-On
Covers: sklearn, BLEU, ROUGE, METEOR, BERTScore, CIDEr, Perplexity, MoverScore, BLEURT, Calibration
"""
import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import random, math, warnings
from collections import Counter
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

# --- guarded imports ---
try:
    import nltk; nltk.download("punkt_tab", quiet=True); nltk.download("wordnet", quiet=True)
    from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score as nltk_meteor
    HAS_NLTK = True
except ImportError:
    print("[SKIP] nltk not installed"); HAS_NLTK = False
try:
    from rouge_score import rouge_scorer; HAS_ROUGE = True
except ImportError:
    print("[SKIP] rouge_score not installed"); HAS_ROUGE = False
try:
    from bert_score import score as bert_score_fn; HAS_BERTSCORE = True
except ImportError:
    print("[SKIP] bert_score not installed"); HAS_BERTSCORE = False
try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    HAS_SKLEARN = True
except ImportError:
    print("[SKIP] sklearn not installed"); HAS_SKLEARN = False

random.seed(42)
DATA_PATH = r"D:\Study\Git_repo\evaluations\data\train.csv"
SEP = "=" * 60

def main():
    print(f"{SEP}\nCHAPTER 2: CLASSICAL NLP METRICS\n{SEP}")

    # ---- 1. Load data, create reference/hypothesis pairs ----
    df = pd.read_csv(DATA_PATH)
    sample = df.head(5).copy()
    choices = ["A", "B", "C", "D", "E"]
    references, hypotheses, sim_letters = [], [], []
    for _, row in sample.iterrows():
        references.append(row[row["answer"]])
        pick = row["answer"] if random.random() < 0.5 else random.choice(choices)
        sim_letters.append(pick); hypotheses.append(row[pick])
    true_letters = sample["answer"].tolist()

    print(f"\nUsing {len(sample)} sample questions")
    for i in range(5):
        tag = "CORRECT" if true_letters[i] == sim_letters[i] else "WRONG"
        print(f"\nQ{i+1} [{tag}] true={true_letters[i]} pred={sim_letters[i]}")
        print(f"  Ref: {references[i][:80]}...")
        print(f"  Hyp: {hypotheses[i][:80]}...")

    # ---- 2. sklearn classification metrics ----
    print(f"\n{SEP}\nSECTION 1: CLASSIFICATION METRICS (sklearn)\n{SEP}")
    if HAS_SKLEARN:
        acc = accuracy_score(true_letters, sim_letters)
        prec = precision_score(true_letters, sim_letters, average="macro", zero_division=0)
        rec = recall_score(true_letters, sim_letters, average="macro", zero_division=0)
        f1_val = f1_score(true_letters, sim_letters, average="macro", zero_division=0)
        cm = confusion_matrix(true_letters, sim_letters, labels=choices)
        print(f"Accuracy: {acc:.4f}  Precision: {prec:.4f}  Recall: {rec:.4f}  F1: {f1_val:.4f}")
        print(f"Confusion Matrix:\n{pd.DataFrame(cm, index=choices, columns=choices)}")
    else:
        acc = prec = rec = f1_val = float("nan")

    # ---- 3. NLTK BLEU ----
    print(f"\n{SEP}\nSECTION 2: BLEU SCORE (nltk)\n{SEP}")
    bleu_scores, corpus_bleu_val = [0.0]*5, 0.0
    if HAS_NLTK:
        smoother = SmoothingFunction().method1
        for i in range(5):
            rt = nltk.word_tokenize(references[i].lower())
            ht = nltk.word_tokenize(hypotheses[i].lower())
            bleu_scores[i] = sentence_bleu([rt], ht, smoothing_function=smoother)
            print(f"Q{i+1} Sentence BLEU: {bleu_scores[i]:.4f}")
        all_refs = [[nltk.word_tokenize(r.lower())] for r in references]
        all_hyps = [nltk.word_tokenize(h.lower()) for h in hypotheses]
        corpus_bleu_val = corpus_bleu(all_refs, all_hyps, smoothing_function=smoother)
        print(f"Corpus BLEU: {corpus_bleu_val:.4f}")

    # ---- 4. ROUGE ----
    print(f"\n{SEP}\nSECTION 3: ROUGE SCORE\n{SEP}")
    r1s, r2s, rLs = [0.0]*5, [0.0]*5, [0.0]*5
    if HAS_ROUGE:
        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        for i in range(5):
            s = scorer.score(references[i], hypotheses[i])
            r1s[i], r2s[i], rLs[i] = s["rouge1"].fmeasure, s["rouge2"].fmeasure, s["rougeL"].fmeasure
            print(f"Q{i+1} R1: {r1s[i]:.4f}  R2: {r2s[i]:.4f}  RL: {rLs[i]:.4f}")

    # ---- 5. METEOR ----
    print(f"\n{SEP}\nSECTION 4: METEOR SCORE (nltk)\n{SEP}")
    meteor_scores = [0.0]*5
    if HAS_NLTK:
        for i in range(5):
            rt = nltk.word_tokenize(references[i].lower())
            ht = nltk.word_tokenize(hypotheses[i].lower())
            meteor_scores[i] = nltk_meteor([rt], ht)
            print(f"Q{i+1} METEOR: {meteor_scores[i]:.4f}")
        print(f"Avg METEOR: {np.mean(meteor_scores):.4f}")
    print("METEOR adds synonym/stem matching on top of BLEU-style n-gram overlap.")

    # ---- 6. BERTScore ----
    print(f"\n{SEP}\nSECTION 5: BERTScore\n{SEP}")
    bert_f1 = [0.0]*5
    if HAS_BERTSCORE:
        P, R, F1 = bert_score_fn(hypotheses, references, lang="en", verbose=False)
        for i in range(5):
            bert_f1[i] = F1[i].item()
            print(f"Q{i+1} P: {P[i]:.4f}  R: {R[i]:.4f}  F1: {F1[i]:.4f}")
        print(f"Avg BERTScore F1: {F1.mean():.4f}")

    # ---- 7. CIDEr (from scratch) ----
    print(f"\n{SEP}\nSECTION 6: CIDEr (TF-IDF n-gram cosine)\n{SEP}")
    def cider_score(ref, hyp, n=4):
        def ng(tokens, k): return [tuple(tokens[j:j+k]) for j in range(len(tokens)-k+1)]
        rt, ht = ref.lower().split(), hyp.lower().split()
        scores = []
        for k in range(1, n+1):
            rc, hc = Counter(ng(rt, k)), Counter(ng(ht, k))
            keys = set(rc) | set(hc)
            if not keys: continue
            rv = np.array([rc.get(g, 0) for g in keys], dtype=float)
            hv = np.array([hc.get(g, 0) for g in keys], dtype=float)
            d = np.linalg.norm(rv) * np.linalg.norm(hv)
            scores.append(float(np.dot(rv, hv) / d) if d > 0 else 0.0)
        return np.mean(scores) if scores else 0.0

    cider_scores = [cider_score(references[i], hypotheses[i]) for i in range(5)]
    for i in range(5): print(f"Q{i+1} CIDEr: {cider_scores[i]:.4f}")
    print(f"Avg CIDEr: {np.mean(cider_scores):.4f}")
    print("Full CIDEr uses corpus-level IDF weighting; this is a simplified per-pair version.")

    # ---- 8. Perplexity (character-level frequency model) ----
    print(f"\n{SEP}\nSECTION 7: PERPLEXITY (character-level, conceptual)\n{SEP}")
    def char_perplexity(text):
        freq = Counter(text.lower()); total = sum(freq.values())
        entropy = -sum(freq[c] * math.log2(freq[c] / total) for c in freq) / total
        return 2 ** entropy

    ppl_scores = [char_perplexity(hypotheses[i]) for i in range(5)]
    for i in range(5): print(f"Q{i+1} Char-Perplexity: {ppl_scores[i]:.2f}")
    print(f"Avg Perplexity: {np.mean(ppl_scores):.2f}")
    print("Real perplexity uses a language model's token probabilities. Lower = less surprised.")

    # ---- 9. MoverScore (simplified word-overlap proxy) ----
    print(f"\n{SEP}\nSECTION 8: MOVERSCORE (simplified proxy)\n{SEP}")
    def simple_moverscore(ref, hyp):
        rw, hw = set(ref.lower().split()), set(hyp.lower().split())
        return len(rw & hw) / max(len(rw), len(hw)) if rw and hw else 0.0

    mover_scores = [simple_moverscore(references[i], hypotheses[i]) for i in range(5)]
    for i in range(5): print(f"Q{i+1} MoverScore: {mover_scores[i]:.4f}")
    print(f"Avg MoverScore: {np.mean(mover_scores):.4f}")
    print("Real MoverScore uses contextual embeddings (BERT) + Earth Mover's Distance.")

    # ---- 10. BLEURT (explanation + BERTScore proxy) ----
    print(f"\n{SEP}\nSECTION 9: BLEURT (learned metric)\n{SEP}")
    print("BLEURT: BERT fine-tuned on human quality judgments. Requires 'bleurt' package (~2GB).")
    print("BERTScore is the closest available proxy — both use BERT embeddings.")
    print(f"Proxy (BERTScore F1): {[round(b, 4) for b in bert_f1]}")

    # ---- 11. Calibration ----
    print(f"\n{SEP}\nSECTION 10: CALIBRATION\n{SEP}")
    np.random.seed(42)
    confidences = [round(np.random.uniform(0.6, 0.95) if true_letters[i] == sim_letters[i]
                         else np.random.uniform(0.3, 0.7), 2) for i in range(5)]
    correct = [1 if true_letters[i] == sim_letters[i] else 0 for i in range(5)]
    print("Simulated confidence vs correctness:")
    for i in range(5): print(f"  Q{i+1}  conf={confidences[i]}  correct={correct[i]}")
    bins = [(0.0, 0.5), (0.5, 0.75), (0.75, 1.0)]
    print("\nCalibration bins:")
    for lo, hi in bins:
        ib = [(confidences[j], correct[j]) for j in range(5) if lo <= confidences[j] < hi]
        if ib:
            ac, aa = np.mean([c for c,_ in ib]), np.mean([a for _,a in ib])
            print(f"  [{lo:.2f},{hi:.2f}) n={len(ib)} avg_conf={ac:.2f} avg_acc={aa:.2f} gap={abs(ac-aa):.2f}")
        else:
            print(f"  [{lo:.2f},{hi:.2f}) n=0")
    print("Well-calibrated => avg_confidence ~ avg_accuracy in each bin.")

    # ---- 12. Summary DataFrame ----
    print(f"\n{SEP}\nSUMMARY: ALL METRICS\n{SEP}")
    summary = []
    for i in range(5):
        summary.append({"Q": f"Q{i+1}",
            "Match": "Y" if true_letters[i] == sim_letters[i] else "N",
            "BLEU": round(bleu_scores[i], 4), "ROUGE-1": round(r1s[i], 4),
            "ROUGE-L": round(rLs[i], 4), "METEOR": round(meteor_scores[i], 4),
            "BERTSc": round(bert_f1[i], 4), "CIDEr": round(cider_scores[i], 4),
            "PPL": round(ppl_scores[i], 2), "Mover": round(mover_scores[i], 4),
            "Conf": confidences[i]})
    print(f"\n{pd.DataFrame(summary).to_string(index=False)}")

    print(f"\nClassification:  Acc={acc:.4f}  P={prec:.4f}  R={rec:.4f}  F1={f1_val:.4f}")
    print(f"Corpus BLEU: {corpus_bleu_val:.4f}   Avg METEOR: {np.mean(meteor_scores):.4f}")
    print(f"Avg ROUGE-1: {np.mean(r1s):.4f}  ROUGE-L: {np.mean(rLs):.4f}")
    print(f"Avg BERTScore F1: {np.mean(bert_f1):.4f}  Avg CIDEr: {np.mean(cider_scores):.4f}")
    print(f"Avg Perplexity: {np.mean(ppl_scores):.2f}  Avg MoverScore: {np.mean(mover_scores):.4f}")

    print("\n--- Key Takeaways ---")
    print("- BLEU: precision-focused n-gram overlap")
    print("- ROUGE: recall-focused n-gram overlap")
    print("- METEOR: synonyms/stems on top of n-gram matching")
    print("- BERTScore: contextual embedding similarity")
    print("- CIDEr: TF-IDF n-gram cosine (designed for captions)")
    print("- Perplexity: language model surprise (lower = better)")
    print("- MoverScore: EMD over contextual embeddings")
    print("- BLEURT: learned metric from human judgments")
    print("- Calibration: confidence vs actual accuracy")
    print("\nDone!")

if __name__ == "__main__":
    main()
