import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 3 - Modern LLM Evaluation: All 17 Dimensions Demonstrated
=================================================================

This script walks through every evaluation dimension implemented in
evaluator.py, using curated data from sample_data.json and synthetic
data from dataset.py.

Dimensions covered:
  1. Correctness           10. Fluency
  2. Relevance             11. Coherence
  3. Helpfulness           12. Safety
  4. Completeness          13. Toxicity
  5. Consistency           14. Bias
  6. Hallucination         15. Creativity
  7. Faithfulness          16. Readability
  8. Groundedness          17. Reasoning Quality
  9. Instruction Following
"""

from dataset import (
    load_sample_data,
    load_wiki_contexts,
    generate_simulated_responses,
    simulate_mcq_predictions,
)
from evaluator import (
    CorrectnessEvaluator,
    RelevanceEvaluator,
    HelpfulnessEvaluator,
    CompletenessEvaluator,
    ConsistencyEvaluator,
    HallucinationEvaluator,
    FaithfulnessEvaluator,
    GroundednessEvaluator,
    InstructionFollowingEvaluator,
    FluencyEvaluator,
    CoherenceEvaluator,
    SafetyEvaluator,
    ToxicityEvaluator,
    BiasEvaluator,
    CreativityEvaluator,
    ReadabilityEvaluator,
    ReasoningEvaluator,
    MultiDimensionEvaluator,
)

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
SEPARATOR = "=" * 78
SUBSEP = "-" * 78


def banner(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def sub_banner(title: str) -> None:
    print(f"\n{SUBSEP}")
    print(f"  {title}")
    print(SUBSEP)


def print_result(result: dict, indent: int = 2) -> None:
    """Pretty-print a result dict, skipping very long nested lists."""
    prefix = " " * indent
    for key, value in result.items():
        if isinstance(value, list) and len(value) > 5:
            print(f"{prefix}{key}: [{len(value)} items, showing first 3]")
            for item in value[:3]:
                print(f"{prefix}  {item}")
        elif isinstance(value, dict):
            print(f"{prefix}{key}:")
            print_result(value, indent + 4)
        else:
            print(f"{prefix}{key}: {value}")


def show_dimension_header(number: int, name: str, problem: str,
                          intuition: str) -> None:
    banner(f"DIMENSION {number}: {name}")
    print(f"\n  PROBLEM   : {problem}")
    print(f"  INTUITION : {intuition}")


def show_advantages_limitations(advantages: list[str],
                                 limitations: list[str]) -> None:
    print("\n  ADVANTAGES:")
    for a in advantages:
        print(f"    + {a}")
    print("\n  LIMITATIONS:")
    for l in limitations:
        print(f"    - {l}")


# ---------------------------------------------------------------------------
# Load data once
# ---------------------------------------------------------------------------
def load_all_data() -> dict:
    sample = load_sample_data()
    contexts = load_wiki_contexts(limit=5)
    simulated = generate_simulated_responses(contexts, seed=42)
    return {
        "sample": sample,
        "contexts": contexts,
        "simulated": simulated,
    }


# ===================================================================
# DIMENSION 1: CORRECTNESS
# ===================================================================
def demo_correctness(data: dict) -> float:
    show_dimension_header(
        1, "CORRECTNESS",
        "Is the model's answer factually correct?",
        "Like grading a test -- compare the student's answer to the answer key.",
    )

    evaluator = CorrectnessEvaluator()
    sample = data["sample"]

    # --- A. Exact match on MCQ ---
    sub_banner("A. Exact-Match Evaluation (MCQ)")
    mcq = sample["mcq_evaluation_set"]
    gt_list = [q["ground_truth"] for q in mcq]
    good_preds = [q["good_model_pred"] for q in mcq]
    bad_preds = [q["bad_model_pred"] for q in mcq]

    good_batch = evaluator.evaluate_batch(gt_list, good_preds)
    bad_batch = evaluator.evaluate_batch(gt_list, bad_preds)

    print(f"\n  Good model accuracy : {good_batch['accuracy']}  ({good_batch['correct']}/{good_batch['total']})")
    print(f"  Bad  model accuracy : {bad_batch['accuracy']}  ({bad_batch['correct']}/{bad_batch['total']})")

    # --- B. Open-ended ---
    sub_banner("B. Open-Ended Correctness")
    sq = sample["science_questions"][0]
    good_resp = sample["llm_responses"]["good_responses"][0]["response"]
    bad_resp = sample["llm_responses"]["bad_responses"][0]["response"]

    key_facts = ["tidal forces", "disintegrate", "Roche", "gravity"]

    res_good = evaluator.evaluate_open_ended(sq["reference_answer"], good_resp, key_facts)
    res_bad = evaluator.evaluate_open_ended(sq["reference_answer"], bad_resp, key_facts)

    print(f"\n  Question: {sq['question']}")
    print(f"\n  Good response score : {res_good['score']}  (overlap={res_good['word_overlap']}, cosine={res_good['cosine_similarity']}, facts={res_good['fact_coverage']})")
    print(f"  Bad  response score : {res_bad['score']}  (overlap={res_bad['word_overlap']}, cosine={res_bad['cosine_similarity']}, facts={res_bad['fact_coverage']})")

    show_advantages_limitations(
        [
            "Simple and interpretable for MCQ/classification tasks",
            "No external dependencies -- pure string comparison",
            "Batch evaluation gives quick accuracy overview",
        ],
        [
            "Exact match is too strict for open-ended answers",
            "Keyword overlap misses paraphrases and synonyms",
            "Cannot evaluate novel correct answers not in reference",
        ],
    )
    return res_good["score"]


# ===================================================================
# DIMENSION 2: RELEVANCE
# ===================================================================
def demo_relevance(data: dict) -> float:
    show_dimension_header(
        2, "RELEVANCE",
        "Does the response address the question that was actually asked?",
        "Like asking a waiter for the dessert menu and getting a wine list.",
    )

    evaluator = RelevanceEvaluator()
    sample = data["sample"]
    sq = sample["science_questions"][1]
    good_resp = sample["llm_responses"]["good_responses"][1]["response"]
    bad_resp = sample["llm_responses"]["bad_responses"][1]["response"]

    res_good = evaluator.evaluate(sq["question"], good_resp)
    res_bad = evaluator.evaluate(sq["question"], bad_resp)

    print(f"\n  Question: {sq['question']}")
    print(f"\n  Good response (on-topic):")
    print(f"    score={res_good['score']}, topic_overlap={res_good['topic_overlap']}, terms_covered={res_good['question_terms_covered']}")
    print(f"\n  Bad response (off-topic):")
    print(f"    score={res_bad['score']}, topic_overlap={res_bad['topic_overlap']}, terms_covered={res_bad['question_terms_covered']}")

    # Deliberately off-topic example
    sub_banner("Completely Off-Topic Example")
    off_topic = evaluator.evaluate(
        "What is photosynthesis?",
        "The stock market crashed in 1929, leading to the Great Depression.",
    )
    print(f"  Question : What is photosynthesis?")
    print(f"  Response : The stock market crashed in 1929 ... (off-topic)")
    print(f"  Score    : {off_topic['score']}")

    show_advantages_limitations(
        [
            "Fast keyword-based check before deeper evaluation",
            "Catches completely off-topic responses",
            "Works without reference answers",
        ],
        [
            "Cannot detect semantic relevance (only keyword overlap)",
            "Paraphrased questions may score low",
            "Cannot distinguish relevant-but-wrong from relevant-and-right",
        ],
    )
    return res_good["score"]


# ===================================================================
# DIMENSION 3: HELPFULNESS
# ===================================================================
def demo_helpfulness(data: dict) -> float:
    show_dimension_header(
        3, "HELPFULNESS",
        "Is the response actually useful to the person who asked?",
        "Like getting 'go that way' vs turn-by-turn directions with landmarks.",
    )

    evaluator = HelpfulnessEvaluator()
    sample = data["sample"]
    sq = sample["science_questions"][0]
    good_resp = sample["llm_responses"]["good_responses"][0]["response"]

    # Minimal unhelpful answer
    unhelpful = "It is a concept in astronomy."

    res_good = evaluator.evaluate(sq["question"], good_resp)
    res_bad = evaluator.evaluate(sq["question"], unhelpful)

    print(f"\n  Question: {sq['question']}")
    print(f"\n  Helpful response:")
    print(f"    score={res_good['score']}, words={res_good['word_count']}, explanations={res_good['explanation_score']}, structure={res_good['structure_score']}")
    print(f"\n  Unhelpful response: '{unhelpful}'")
    print(f"    score={res_bad['score']}, words={res_bad['word_count']}, explanations={res_bad['explanation_score']}, structure={res_bad['structure_score']}")

    show_advantages_limitations(
        [
            "Captures surface signals of helpfulness (length, structure, explanations)",
            "No reference answer needed",
            "Fast heuristic pre-filter",
        ],
        [
            "Length is a poor proxy (longer != more helpful)",
            "Cannot measure whether the user's actual need was met",
            "Helpfulness is inherently subjective",
        ],
    )
    return res_good["score"]


# ===================================================================
# DIMENSION 4: COMPLETENESS
# ===================================================================
def demo_completeness(data: dict) -> float:
    show_dimension_header(
        4, "COMPLETENESS",
        "Does the response cover ALL aspects of the question?",
        "Like ordering a combo meal and only getting the burger -- no fries or drink.",
    )

    evaluator = CompletenessEvaluator()

    question = "Explain the causes AND effects of climate change, and list potential solutions."
    complete = (
        "Climate change is caused by greenhouse gas emissions from burning fossil fuels, "
        "deforestation, and industrial processes. The effects include rising sea levels, "
        "more extreme weather events, loss of biodiversity, and food insecurity. "
        "Potential solutions include transitioning to renewable energy, carbon capture, "
        "reforestation, and international policy agreements like the Paris Accord."
    )
    incomplete = "Climate change is caused by pollution from factories and cars."

    aspects = ["causes of climate change", "effects of climate change", "potential solutions"]

    res_complete = evaluator.evaluate(question, complete, aspects)
    res_incomplete = evaluator.evaluate(question, incomplete, aspects)

    print(f"\n  Question: {question}")
    print(f"\n  Complete response:")
    print(f"    score={res_complete['score']}, coverage={res_complete['aspect_coverage']}")
    if res_complete["aspects_detail"]:
        for a in res_complete["aspects_detail"]:
            print(f"      [{'+' if a['covered'] else 'X'}] {a['aspect']}")

    print(f"\n  Incomplete response: '{incomplete}'")
    print(f"    score={res_incomplete['score']}, coverage={res_incomplete['aspect_coverage']}")
    if res_incomplete["aspects_detail"]:
        for a in res_incomplete["aspects_detail"]:
            print(f"      [{'+' if a['covered'] else 'X'}] {a['aspect']}")

    show_advantages_limitations(
        [
            "Explicit aspect checking when aspects are known",
            "Catches answers that only address part of a multi-part question",
            "Length ratio heuristic catches very short answers",
        ],
        [
            "Heuristic aspect extraction misses implicit sub-questions",
            "Cannot assess depth of coverage for each aspect",
            "Some questions have unbounded scope",
        ],
    )
    return res_complete["score"]


# ===================================================================
# DIMENSION 5: CONSISTENCY
# ===================================================================
def demo_consistency(data: dict) -> float:
    show_dimension_header(
        5, "CONSISTENCY",
        "Does the model give the same answer when asked the same question multiple times?",
        "Like asking a witness the same question three times -- if the story changes, trust drops.",
    )

    evaluator = ConsistencyEvaluator()
    sample = data["sample"]

    # Consistent set
    consistent = sample["llm_responses"]["consistency_examples"][0]
    res_con = evaluator.evaluate(consistent["responses"])
    print(f"\n  Question: {consistent['question']}")
    print(f"  Expected consistent: {consistent['is_consistent']}")
    print(f"  Consistency score  : {res_con['score']}")
    print(f"  Avg pairwise sim   : {res_con['avg_pairwise_similarity']}")

    # Inconsistent set
    inconsistent = sample["llm_responses"]["consistency_examples"][1]
    res_inc = evaluator.evaluate(inconsistent["responses"])
    print(f"\n  Question: {inconsistent['question']}")
    print(f"  Expected consistent: {inconsistent['is_consistent']}")
    print(f"  Consistency score  : {res_inc['score']}")
    print(f"  Avg pairwise sim   : {res_inc['avg_pairwise_similarity']}")

    show_advantages_limitations(
        [
            "Detects unreliable models that give different answers each time",
            "Pairwise similarity captures overall agreement",
            "Numerical consistency check catches contradictory numbers",
        ],
        [
            "Consistent wrong answers still score high",
            "Some variation (paraphrasing) is healthy and expected",
            "Cannot distinguish good variation from bad contradiction",
        ],
    )
    return res_con["score"]


# ===================================================================
# DIMENSION 6: HALLUCINATION DETECTION
# ===================================================================
def demo_hallucination(data: dict) -> float:
    show_dimension_header(
        6, "HALLUCINATION DETECTION",
        "Did the model fabricate information not present in the source?",
        "Like a student making up quotes and attributing them to real authors.",
    )

    evaluator = HallucinationEvaluator()
    simulated = data["simulated"]

    entry = simulated[0]
    sub_banner(f"Topic: {entry['page_title']}")
    print(f"  Source: {entry['source_text'][:100]}...")

    # Faithful response
    res_faithful = evaluator.evaluate(entry["source_text"], entry["faithful_response"])
    print(f"\n  Faithful response:")
    print(f"    Hallucination score: {res_faithful['score']} (1.0 = no hallucination)")
    print(f"    Hallucination rate : {res_faithful['hallucination_rate']}")
    print(f"    Sentences checked  : {res_faithful['total_sentences']}")

    # Hallucinated response
    res_halluc = evaluator.evaluate(entry["source_text"], entry["hallucinated_response"])
    print(f"\n  Hallucinated response:")
    print(f"    Hallucination score: {res_halluc['score']}")
    print(f"    Hallucination rate : {res_halluc['hallucination_rate']}")
    if res_halluc["sentence_analysis"]:
        for sa in res_halluc["sentence_analysis"][:3]:
            flag = "HALLUCINATED" if sa["likely_hallucinated"] else "grounded"
            print(f"    [{flag}] {sa['sentence'][:70]}...")

    # Also test from sample_data hallucinated examples
    sub_banner("Curated Hallucination Example (Froude Number)")
    sample = data["sample"]
    hall_ex = sample["llm_responses"]["hallucinated_responses"][0]
    res_hall = evaluator.evaluate(hall_ex["context_provided"], hall_ex["response"])
    print(f"  Score: {res_hall['score']}  (rate={res_hall['hallucination_rate']})")
    print(f"  Known hallucinated claims: {hall_ex['hallucinated_claims'][:2]}")

    show_advantages_limitations(
        [
            "Catches fabricated statistics, dates, and attributions",
            "Pattern-based detection for common hallucination types",
            "Per-sentence analysis pinpoints where hallucinations occur",
        ],
        [
            "Cannot detect hallucinations without a reference source",
            "Word overlap misses paraphrased faithful content",
            "Some 'hallucinated' content might be correct common knowledge",
        ],
    )
    return res_faithful["score"]


# ===================================================================
# DIMENSION 7: FAITHFULNESS
# ===================================================================
def demo_faithfulness(data: dict) -> float:
    show_dimension_header(
        7, "FAITHFULNESS",
        "Does the response accurately represent what the source material says?",
        "Like a journalist quoting a source -- faithful journalism vs distorted quotes.",
    )

    evaluator = FaithfulnessEvaluator()
    simulated = data["simulated"]
    entry = simulated[1]

    sub_banner(f"Topic: {entry['page_title']}")
    res_faith = evaluator.evaluate(entry["source_text"], entry["faithful_response"])
    res_unfaith = evaluator.evaluate(entry["source_text"], entry["hallucinated_response"])

    print(f"\n  Faithful response:")
    print(f"    score={res_faith['score']}, token_faith={res_faith['token_faithfulness']}, bigram_faith={res_faith['bigram_faithfulness']}")
    print(f"    Faithful sentences: {res_faith['faithful_sentences']}/{res_faith['total_sentences']}")

    print(f"\n  Unfaithful response:")
    print(f"    score={res_unfaith['score']}, token_faith={res_unfaith['token_faithfulness']}, bigram_faith={res_unfaith['bigram_faithfulness']}")
    print(f"    Faithful sentences: {res_unfaith['faithful_sentences']}/{res_unfaith['total_sentences']}")

    print("\n  KEY DISTINCTION (Faithfulness vs Hallucination):")
    print("    Hallucination asks: 'Did the model make things UP?'")
    print("    Faithfulness  asks: 'Did the model stay TRUE to the source?'")

    show_advantages_limitations(
        [
            "Measures fidelity at token, bigram, and sentence levels",
            "Essential for RAG (retrieval-augmented generation) systems",
            "Multi-granularity scoring gives nuanced picture",
        ],
        [
            "Cannot detect subtle distortions (changing 'may' to 'definitely')",
            "Paraphrased faithful content may score low",
            "Cannot evaluate logical inferences drawn from source",
        ],
    )
    return res_faith["score"]


# ===================================================================
# DIMENSION 8: GROUNDEDNESS
# ===================================================================
def demo_groundedness(data: dict) -> float:
    show_dimension_header(
        8, "GROUNDEDNESS",
        "Can every claim in the response be traced back to the provided context?",
        "Like a lawyer who can only cite evidence admitted to court.",
    )

    evaluator = GroundednessEvaluator()
    simulated = data["simulated"]
    entry = simulated[2]

    sub_banner(f"Topic: {entry['page_title']}")

    res_grounded = evaluator.evaluate(entry["source_text"], entry["faithful_response"])
    res_ungrounded = evaluator.evaluate(entry["source_text"], entry["partial_response"])

    print(f"\n  Grounded response:")
    print(f"    score={res_grounded['score']}, grounded_claims={res_grounded['grounded_claims']}/{res_grounded['total_claims']}")

    print(f"\n  Partially ungrounded response:")
    print(f"    score={res_ungrounded['score']}, grounded_claims={res_ungrounded['grounded_claims']}/{res_ungrounded['total_claims']}")
    if res_ungrounded["claim_analysis"]:
        for claim in res_ungrounded["claim_analysis"][:3]:
            flag = "GROUNDED" if claim["is_grounded"] else "UNGROUNDED"
            print(f"    [{flag}] {claim['claim'][:65]}... (match={claim['best_match_score']})")

    print("\n  KEY DISTINCTION (Groundedness vs Faithfulness vs Hallucination):")
    print("    Groundedness  : Can every claim be TRACED to the context?  (strictest)")
    print("    Faithfulness  : Does the response REPRESENT the context accurately?")
    print("    Hallucination : Did the response ADD things NOT in the context?")

    show_advantages_limitations(
        [
            "Strictest source-fidelity check -- every claim must have a source",
            "Claim-level analysis pinpoints exactly which claims lack support",
            "Essential for high-stakes RAG systems (legal, medical)",
        ],
        [
            "Cannot detect valid inferences from context",
            "Misses paraphrased grounded content",
            "Too strict for responses that legitimately add common knowledge",
        ],
    )
    return res_grounded["score"]


# ===================================================================
# DIMENSION 9: INSTRUCTION FOLLOWING
# ===================================================================
def demo_instruction_following(data: dict) -> float:
    show_dimension_header(
        9, "INSTRUCTION FOLLOWING",
        "Did the model follow the specific instructions given?",
        "Like a contractor who builds a beautiful kitchen when you asked for a bathroom.",
    )

    evaluator = InstructionFollowingEvaluator()
    sample = data["sample"]
    examples = sample["llm_responses"]["instruction_following_examples"]

    scores = []
    for ex in examples:
        sub_banner(f"Instruction: {ex['instruction'][:70]}...")

        res_good = evaluator.evaluate(ex["instruction"], ex["good_response"])
        res_bad = evaluator.evaluate(ex["instruction"], ex["bad_response"])
        scores.append(res_good["score"])

        print(f"\n  Good response (follows instruction):")
        print(f"    score={res_good['score']}, passed={res_good['constraints_passed']}/{res_good['constraints_checked']}")
        for check in res_good["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            print(f"    [{status}] {check['constraint']}")

        print(f"\n  Bad response (ignores instruction):")
        print(f"    score={res_bad['score']}, passed={res_bad['constraints_passed']}/{res_bad['constraints_checked']}")
        for check in res_bad["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            print(f"    [{status}] {check['constraint']}")

    show_advantages_limitations(
        [
            "Checks verifiable constraints (length, format, bullet points)",
            "Works for structured output requirements (JSON, lists)",
            "Catches common instruction violations automatically",
        ],
        [
            "Can only check instructions with detectable patterns",
            "Cannot verify semantic compliance (e.g., 'be creative')",
            "May miss implicit instructions",
        ],
    )
    return sum(scores) / len(scores) if scores else 0.0


# ===================================================================
# DIMENSION 10: FLUENCY
# ===================================================================
def demo_fluency(data: dict) -> float:
    show_dimension_header(
        10, "FLUENCY",
        "Is the language natural, grammatical, and easy to read?",
        "Like listening to someone speak -- broken grammar reduces trust.",
    )

    evaluator = FluencyEvaluator()
    sample = data["sample"]

    # Fluent response
    fluent = sample["llm_responses"]["good_responses"][2]["response"]
    # Non-fluent response
    nonfluent = sample["llm_responses"]["bad_responses"][2]["response"]

    res_fluent = evaluator.evaluate(fluent)
    res_nonfluent = evaluator.evaluate(nonfluent)

    print(f"\n  Fluent response (first 100 chars): '{fluent[:100]}...'")
    print(f"    score={res_fluent['score']}, capitalization={res_fluent['capitalization_score']}, repetition={res_fluent['repetition_score']}, punctuation={res_fluent['punctuation_score']}")

    print(f"\n  Non-fluent response (first 100 chars): '{nonfluent[:100]}...'")
    print(f"    score={res_nonfluent['score']}, capitalization={res_nonfluent['capitalization_score']}, repetition={res_nonfluent['repetition_score']}, punctuation={res_nonfluent['punctuation_score']}")

    show_advantages_limitations(
        [
            "Catches basic fluency issues (capitalization, repetition, garbled text)",
            "No external model needed -- pure heuristic",
            "Fast pre-filter for obviously broken outputs",
        ],
        [
            "Cannot detect subtle grammar errors",
            "Rule-based approach misses many fluency issues",
            "Non-English text may score incorrectly",
        ],
    )
    return res_fluent["score"]


# ===================================================================
# DIMENSION 11: COHERENCE
# ===================================================================
def demo_coherence(data: dict) -> float:
    show_dimension_header(
        11, "COHERENCE",
        "Does the response flow logically from start to finish?",
        "Like chapters in a book -- each can be well-written, but if unrelated, the book fails.",
    )

    evaluator = CoherenceEvaluator()

    coherent = (
        "Photosynthesis is the process by which plants convert sunlight into energy. "
        "During this process, carbon dioxide and water are transformed into glucose and oxygen. "
        "The glucose provides energy for the plant's growth, while the oxygen is released into "
        "the atmosphere. Therefore, photosynthesis is essential for both plant life and the "
        "oxygen supply that animals depend on."
    )
    incoherent = (
        "Photosynthesis uses sunlight to make food. "
        "The Roman Empire fell in 476 AD. "
        "Cats are popular pets around the world. "
        "The Pythagorean theorem relates to right triangles. "
        "Coffee is the most widely consumed beverage after water."
    )

    res_coh = evaluator.evaluate(coherent)
    res_inc = evaluator.evaluate(incoherent)

    print(f"\n  Coherent response:")
    print(f"    score={res_coh['score']}, adj_similarity={res_coh['avg_adjacent_similarity']}, topic_shifts={res_coh['topic_shifts_detected']}")
    print(f"    Discourse markers: {res_coh['discourse_markers_found']}")

    print(f"\n  Incoherent response (random topics):")
    print(f"    score={res_inc['score']}, adj_similarity={res_inc['avg_adjacent_similarity']}, topic_shifts={res_inc['topic_shifts_detected']}")
    print(f"    Discourse markers: {res_inc['discourse_markers_found']}")

    show_advantages_limitations(
        [
            "Detects topic shifts and lack of logical flow",
            "Discourse marker analysis reveals structural quality",
            "Adjacent sentence similarity captures local coherence",
        ],
        [
            "Cannot detect logical contradictions within text",
            "Topic shift detection is approximate with keywords",
            "Some responses legitimately cover multiple topics",
        ],
    )
    return res_coh["score"]


# ===================================================================
# DIMENSION 12: SAFETY
# ===================================================================
def demo_safety(data: dict) -> float:
    show_dimension_header(
        12, "SAFETY",
        "Is the response free from dangerous or harmful content?",
        "Like a pharmacist who will not explain how to make drugs from prescriptions.",
    )

    evaluator = SafetyEvaluator()
    sample = data["sample"]
    safety_ex = sample["llm_responses"]["safety_examples"][0]

    res_safe = evaluator.evaluate(safety_ex["safe_response"])
    res_unsafe = evaluator.evaluate(safety_ex["unsafe_response"])

    print(f"\n  Question: {safety_ex['question']}")

    print(f"\n  Safe response:")
    print(f"    score={res_safe['score']}, is_safe={res_safe['is_safe']}, flags={res_safe['total_flags']}")

    print(f"\n  Unsafe response:")
    print(f"    score={res_unsafe['score']}, is_safe={res_unsafe['is_safe']}, flags={res_unsafe['total_flags']}")
    for cat, matches in res_unsafe["flagged_categories"].items():
        print(f"    Category '{cat}': {matches}")

    show_advantages_limitations(
        [
            "Catches explicit dangerous content (chemicals, weapons, harm)",
            "Category-level reporting shows what type of safety issue exists",
            "Fast pre-filter before deployment",
        ],
        [
            "Keyword matching produces many false positives",
            "Sophisticated harmful content evades keyword detection",
            "Cannot distinguish educational content from harmful instructions",
        ],
    )
    return res_safe["score"]


# ===================================================================
# DIMENSION 13: TOXICITY
# ===================================================================
def demo_toxicity(data: dict) -> float:
    show_dimension_header(
        13, "TOXICITY",
        "Does the response contain toxic, hateful, or offensive language?",
        "Like a content moderator reviewing posts for hostile or harmful language.",
    )

    evaluator = ToxicityEvaluator()

    clean = (
        "Machine learning is a fascinating field that combines mathematics, "
        "statistics, and computer science. It enables systems to learn from data "
        "and improve over time without being explicitly programmed."
    )
    toxic = (
        "You idiot, how dumb can you be to ask such a pathetic question? "
        "You're worthless and clearly have no understanding of basic science. "
        "I will destroy your argument with facts."
    )

    res_clean = evaluator.evaluate(clean)
    res_toxic = evaluator.evaluate(toxic)

    print(f"\n  Clean response:")
    print(f"    score={res_clean['score']}, is_toxic={res_clean['is_toxic']}, flags={res_clean['total_flags']}")

    print(f"\n  Toxic response:")
    print(f"    score={res_toxic['score']}, is_toxic={res_toxic['is_toxic']}, flags={res_toxic['total_flags']}")
    for cat, matches in res_toxic["flagged_categories"].items():
        print(f"    Category '{cat}': {matches}")

    show_advantages_limitations(
        [
            "Catches explicit insults, threats, and demeaning language",
            "Category breakdown (profanity, threats, hate speech) aids analysis",
            "Works without external APIs",
        ],
        [
            "Keyword lists are always incomplete",
            "Context determines toxicity (quoting vs using)",
            "Cannot detect coded language or dog whistles",
        ],
    )
    return res_clean["score"]


# ===================================================================
# DIMENSION 14: BIAS
# ===================================================================
def demo_bias(data: dict) -> float:
    show_dimension_header(
        14, "BIAS",
        "Does the response show unfair bias (gender, racial, cultural, elitism)?",
        "Like a hiring manager who unconsciously favors certain university graduates.",
    )

    evaluator = BiasEvaluator()
    sample = data["sample"]
    bias_examples = sample["llm_responses"]["bias_examples"]

    scores = []
    for ex in bias_examples:
        sub_banner(f"Question: {ex['question']}")

        res_biased = evaluator.evaluate(ex["biased_response"])
        res_unbiased = evaluator.evaluate(ex["unbiased_response"])
        scores.append(res_unbiased["score"])

        print(f"\n  Biased response ({ex['bias_type']}):")
        print(f"    score={res_biased['score']}")
        gb = res_biased["gender_balance"]
        print(f"    Gender: male={gb['male_terms']}, female={gb['female_terms']}, ratio={gb['ratio']}")
        print(f"    Stereotypes: {res_biased['stereotypes_found']}")
        print(f"    Inclusive markers: {res_biased['inclusive_markers']}")
        print(f"    Elitism flags: {res_biased['elitism_flags']}")

        print(f"\n  Unbiased response:")
        print(f"    score={res_unbiased['score']}")
        gb2 = res_unbiased["gender_balance"]
        print(f"    Gender: male={gb2['male_terms']}, female={gb2['female_terms']}, ratio={gb2['ratio']}")
        print(f"    Inclusive markers: {res_unbiased['inclusive_markers']}")

    show_advantages_limitations(
        [
            "Detects gender-skewed language and stereotypical patterns",
            "Checks for inclusive language signals",
            "Catches elitism bias (top-tier, prestigious, innate talent)",
        ],
        [
            "Keyword detection cannot measure implicit bias",
            "Context matters enormously -- some topics legitimately focus on specific groups",
            "'Balanced' does not always mean '50/50'",
        ],
    )
    return sum(scores) / len(scores) if scores else 0.0


# ===================================================================
# DIMENSION 15: CREATIVITY
# ===================================================================
def demo_creativity(data: dict) -> float:
    show_dimension_header(
        15, "CREATIVITY",
        "Does the response use creative elements where appropriate?",
        "Like the difference between a dry lecture and a TED talk with stories and analogies.",
    )

    evaluator = CreativityEvaluator()
    sample = data["sample"]
    creativity_ex = sample["llm_responses"]["creativity_examples"][0]

    res_creative = evaluator.evaluate(creativity_ex["creative_response"])
    res_dry = evaluator.evaluate(creativity_ex["uncreative_response"])

    print(f"\n  Instruction: {creativity_ex['instruction']}")

    print(f"\n  Creative response (first 120 chars): '{creativity_ex['creative_response'][:120]}...'")
    print(f"    score={res_creative['score']}, analogies={res_creative['analogies_found']}, storytelling={res_creative['storytelling_elements_found']}")
    print(f"    vocab_richness={res_creative['vocabulary_richness']}, sentence_variety={res_creative['sentence_variety']}")

    print(f"\n  Uncreative response: '{creativity_ex['uncreative_response']}'")
    print(f"    score={res_dry['score']}, analogies={res_dry['analogies_found']}, storytelling={res_dry['storytelling_elements_found']}")

    show_advantages_limitations(
        [
            "Detects analogy/metaphor usage and storytelling elements",
            "Vocabulary richness (type-token ratio) measures lexical diversity",
            "Sentence variety score captures writing dynamism",
        ],
        [
            "Cannot judge quality of creativity (bad analogies still score high)",
            "Creativity is inherently subjective",
            "What is creative in one context is inappropriate in another",
        ],
    )
    return res_creative["score"]


# ===================================================================
# DIMENSION 16: READABILITY
# ===================================================================
def demo_readability(data: dict) -> float:
    show_dimension_header(
        16, "READABILITY",
        "How easy is the response to understand for the target audience?",
        "Like the difference between a research paper and a Wikipedia article.",
    )

    evaluator = ReadabilityEvaluator()
    sample = data["sample"]
    read_ex = sample["llm_responses"]["readability_examples"][0]

    res_readable = evaluator.evaluate(read_ex["readable_response"])
    res_unreadable = evaluator.evaluate(read_ex["unreadable_response"])

    print(f"\n  Question: {read_ex['question']}")

    print(f"\n  Readable response (first 120 chars): '{read_ex['readable_response'][:120]}...'")
    print(f"    score={res_readable['score']}")
    print(f"    Flesch Reading Ease : {res_readable['flesch_reading_ease']}")
    print(f"    Grade level        : {res_readable['flesch_kincaid_grade']} ({res_readable['reading_level']})")
    print(f"    Avg words/sentence : {res_readable['avg_words_per_sentence']}")
    print(f"    Complex word ratio  : {res_readable['complex_word_ratio']}")

    print(f"\n  Unreadable response (first 120 chars): '{read_ex['unreadable_response'][:120]}...'")
    print(f"    score={res_unreadable['score']}")
    print(f"    Flesch Reading Ease : {res_unreadable['flesch_reading_ease']}")
    print(f"    Grade level        : {res_unreadable['flesch_kincaid_grade']} ({res_unreadable['reading_level']})")
    print(f"    Complex word ratio  : {res_unreadable['complex_word_ratio']}")

    show_advantages_limitations(
        [
            "Uses established readability formulas (Flesch, Flesch-Kincaid)",
            "Provides grade-level interpretation",
            "Objective, reproducible metric",
        ],
        [
            "Readability formulas are crude approximations",
            "Technical terms may be necessary and appropriate",
            "Cannot assess conceptual difficulty, only surface features",
        ],
    )
    return res_readable["score"]


# ===================================================================
# DIMENSION 17: REASONING QUALITY
# ===================================================================
def demo_reasoning(data: dict) -> float:
    show_dimension_header(
        17, "REASONING QUALITY",
        "Does the response demonstrate sound logical reasoning?",
        "Like a math teacher checking not just the answer but the work shown.",
    )

    evaluator = ReasoningEvaluator()

    good_reasoning = (
        "The ultraviolet catastrophe was a critical problem because classical physics "
        "predicted infinite energy at short wavelengths. This is because the Rayleigh-Jeans "
        "law, derived from the equipartition theorem, states that energy density increases "
        "with the square of frequency. Therefore, as frequency increases toward ultraviolet "
        "and beyond, the predicted energy diverges to infinity. However, experimental "
        "observations showed that energy actually decreases at high frequencies. "
        "Planck resolved this by proposing that energy is quantized -- emitted in discrete "
        "packets proportional to frequency. As a result, higher-frequency modes contribute "
        "less energy because each quantum requires more energy to excite, thus fewer are "
        "populated at any given temperature. Hence, Planck's quantization naturally prevents "
        "the ultraviolet divergence."
    )
    poor_reasoning = (
        "The ultraviolet catastrophe is about light. It was a problem because it was wrong. "
        "The answer is quantum mechanics because quantum mechanics is the correct answer. "
        "Obviously everyone knows that classical physics does not work for small things."
    )

    res_good = evaluator.evaluate(good_reasoning)
    res_poor = evaluator.evaluate(poor_reasoning)

    print(f"\n  Good reasoning (first 120 chars): '{good_reasoning[:120]}...'")
    print(f"    score={res_good['score']}")
    print(f"    Causal reasoning : count={res_good['causal_reasoning']['count']}, score={res_good['causal_reasoning']['score']}")
    print(f"    Evidence usage   : count={res_good['evidence_usage']['count']}, score={res_good['evidence_usage']['score']}")
    print(f"    Counter-arguments: count={res_good['counter_arguments']['count']}, score={res_good['counter_arguments']['score']}")
    print(f"    Reasoning depth  : {res_good['reasoning_depth']}")
    print(f"    Logical structure: {res_good['logical_structure']}")

    print(f"\n  Poor reasoning: '{poor_reasoning}'")
    print(f"    score={res_poor['score']}")
    print(f"    Causal reasoning : count={res_poor['causal_reasoning']['count']}")
    print(f"    Anti-patterns    : {res_poor['antipatterns_found']}")

    show_advantages_limitations(
        [
            "Detects causal connectives, evidence usage, and counter-arguments",
            "Catches reasoning anti-patterns (circular reasoning, absolute claims)",
            "Multi-level assessment: depth, structure, and evidence",
        ],
        [
            "Cannot verify logical validity of arguments",
            "Presence of reasoning words does not guarantee good reasoning",
            "Cannot detect subtle logical fallacies",
        ],
    )
    return res_good["score"]


# ===================================================================
# MULTI-DIMENSION EVALUATION (combined demo)
# ===================================================================
def demo_multi_dimension(data: dict) -> dict:
    banner("MULTI-DIMENSION EVALUATION (All 17 Combined)")
    print("\n  Running all 17 dimensions on a single question + response pair...")

    evaluator = MultiDimensionEvaluator()
    sample = data["sample"]
    sq = sample["science_questions"][0]
    good_resp = sample["llm_responses"]["good_responses"][0]["response"]
    bad_resp = sample["llm_responses"]["bad_responses"][0]["response"]

    result_good = evaluator.evaluate_all(
        question=sq["question"],
        response=good_resp,
        reference=sq["reference_answer"],
        context=sq["context"],
        instruction="Explain in clear, detailed language.",
        key_facts=["tidal forces", "disintegrate", "Roche", "1848"],
        required_aspects=["definition", "tidal forces", "historical context"],
    )

    result_bad = evaluator.evaluate_all(
        question=sq["question"],
        response=bad_resp,
        reference=sq["reference_answer"],
        context=sq["context"],
        instruction="Explain in clear, detailed language.",
        key_facts=["tidal forces", "disintegrate", "Roche", "1848"],
        required_aspects=["definition", "tidal forces", "historical context"],
    )

    sub_banner("Good Response - All Dimension Scores")
    for dim, score in sorted(result_good["summary"]["individual_scores"].items()):
        bar = "#" * int(score * 30)
        print(f"    {dim:25s} : {score:.4f}  |{bar}")
    print(f"\n    {'AVERAGE':25s} : {result_good['summary']['average_score']:.4f}")
    print(f"    Best  dimension: {result_good['summary']['highest_dimension']}")
    print(f"    Worst dimension: {result_good['summary']['lowest_dimension']}")

    sub_banner("Bad Response - All Dimension Scores")
    for dim, score in sorted(result_bad["summary"]["individual_scores"].items()):
        bar = "#" * int(score * 30)
        print(f"    {dim:25s} : {score:.4f}  |{bar}")
    print(f"\n    {'AVERAGE':25s} : {result_bad['summary']['average_score']:.4f}")

    # --- Head-to-head comparison ---
    sub_banner("Head-to-Head Comparison")
    comparison = evaluator.evaluate_comparison(
        question=sq["question"],
        response_a=good_resp,
        response_b=bad_resp,
        reference=sq["reference_answer"],
        context=sq["context"],
    )
    print(f"\n  Overall winner: Response {comparison['overall_winner']}")
    print(f"  A wins: {comparison['a_wins']}, B wins: {comparison['b_wins']}, Ties: {comparison['ties']}")
    print(f"  Response A avg: {comparison['response_a_avg']:.4f}")
    print(f"  Response B avg: {comparison['response_b_avg']:.4f}")
    print()
    for dim, detail in sorted(comparison["comparison"].items()):
        winner_indicator = f"<-- {detail['winner']}" if detail["winner"] != "tie" else "   tie"
        print(f"    {dim:25s} : A={detail['response_a']:.4f}  B={detail['response_b']:.4f}  {winner_indicator}")

    return result_good["summary"]["individual_scores"]


# ===================================================================
# SUMMARY TABLE
# ===================================================================
def print_summary_table(scores: dict) -> None:
    banner("SUMMARY TABLE: ALL 17 EVALUATION DIMENSIONS")

    dimensions_info = [
        ("Correctness",          "Is the answer right?",               "MCQ exact-match / keyword overlap"),
        ("Relevance",            "Does it answer the question asked?", "Keyword + cosine similarity"),
        ("Helpfulness",          "Is it useful to the user?",          "Length + explanations + structure"),
        ("Completeness",         "Does it cover all aspects?",         "Aspect coverage + length ratio"),
        ("Consistency",          "Same answer each time?",             "Pairwise cosine similarity"),
        ("Hallucination",        "Did it make things up?",             "Source overlap + pattern matching"),
        ("Faithfulness",         "True to the source?",                "Token/bigram/sentence overlap"),
        ("Groundedness",         "Every claim traceable?",             "Claim-to-context matching"),
        ("Instruction Following","Did it follow instructions?",       "Constraint pattern detection"),
        ("Fluency",              "Natural language?",                  "Capitalization + repetition + punctuation"),
        ("Coherence",            "Logical flow?",                      "Adjacent similarity + discourse markers"),
        ("Safety",               "Free from harm?",                    "Keyword category matching"),
        ("Toxicity",             "Free from toxic language?",          "Pattern-based toxicity flags"),
        ("Bias",                 "Fair and unbiased?",                 "Gender balance + stereotype detection"),
        ("Creativity",           "Uses creative elements?",            "Analogy/metaphor + vocab richness"),
        ("Readability",          "Easy to understand?",                "Flesch-Kincaid readability metrics"),
        ("Reasoning Quality",    "Sound logical reasoning?",           "Causal markers + evidence + structure"),
    ]

    print(f"\n  {'#':>3}  {'Dimension':<24} {'Core Question':<34} {'Heuristic Method':<38} {'Score':>6}")
    print(f"  {'---':>3}  {'---':<24} {'---':<34} {'---':<38} {'-----':>6}")

    dim_keys = list(scores.keys())
    for i, (name, question, method) in enumerate(dimensions_info, 1):
        # Find matching score key
        key_match = None
        for k in dim_keys:
            if name.lower().replace(" ", "_").startswith(k.lower().replace("_", "")[:6]):
                key_match = k
                break
        # Fallback: try simpler matching
        if key_match is None:
            name_lower = name.lower().replace(" ", "")
            for k in dim_keys:
                if k.lower().replace("_", "").startswith(name_lower[:5]):
                    key_match = k
                    break
        score_val = scores.get(key_match, "-") if key_match else "-"
        if isinstance(score_val, float):
            score_str = f"{score_val:.4f}"
        else:
            score_str = str(score_val)
        print(f"  {i:>3}  {name:<24} {question:<34} {method:<38} {score_str:>6}")


# ===================================================================
# INTERVIEW QUESTIONS
# ===================================================================
def print_interview_questions() -> None:
    banner("INTERVIEW QUESTIONS: MODERN LLM EVALUATION")

    questions = [
        (
            "What is the difference between hallucination, faithfulness, and groundedness?",
            "Hallucination asks 'did the model invent facts?'. Faithfulness asks "
            "'does the response accurately represent the source?'. Groundedness asks "
            "'can every claim be traced to the context?'. Groundedness is the strictest; "
            "hallucination detection focuses on fabrication; faithfulness focuses on "
            "accurate representation.",
        ),
        (
            "Why is correctness not sufficient as the only evaluation dimension?",
            "A response can be correct but unhelpful (too brief), irrelevant (off-topic), "
            "incomplete (misses aspects), biased, unsafe, or poorly written. Modern LLM "
            "evaluation requires multiple dimensions because LLMs are used for open-ended "
            "tasks where quality is multi-faceted.",
        ),
        (
            "How would you evaluate an LLM in a RAG (retrieval-augmented generation) pipeline?",
            "Key dimensions: faithfulness (does it stick to retrieved context?), groundedness "
            "(can every claim be traced?), hallucination (does it add fabricated info?), "
            "relevance (does it answer the question?), and completeness (does it use all "
            "relevant retrieved information?). LLM-as-Judge (Chapter 4) is often used for "
            "these evaluations.",
        ),
        (
            "What are the limitations of heuristic-based evaluation vs LLM-as-Judge?",
            "Heuristic methods (keyword matching, readability formulas) are fast and "
            "reproducible but shallow -- they miss semantic understanding, paraphrases, "
            "and nuanced quality. LLM-as-Judge can assess semantics and reasoning but is "
            "expensive, potentially biased, and less reproducible. The best approach combines both.",
        ),
        (
            "How do you evaluate LLM safety beyond keyword matching?",
            "Production systems use: (1) dedicated safety classifiers (e.g., Perspective API, "
            "LlamaGuard), (2) red-teaming with adversarial prompts, (3) LLM-as-Judge with "
            "safety rubrics, (4) human evaluation with content policy guidelines, and "
            "(5) multi-turn conversation testing for jailbreak resistance.",
        ),
        (
            "What is the difference between fluency and coherence?",
            "Fluency measures whether individual sentences are grammatical and natural. "
            "Coherence measures whether the response flows logically as a whole. A response "
            "can have perfectly fluent sentences that are incoherent together (random facts "
            "on different topics).",
        ),
        (
            "How would you detect bias in LLM outputs at scale?",
            "Approaches include: (1) counterfactual testing (swap demographic terms, check if "
            "output changes), (2) representation audits across large output corpora, "
            "(3) stereotype association tests, (4) disaggregated evaluation across demographic "
            "groups, and (5) human evaluation with diverse annotator pools.",
        ),
        (
            "When should you NOT use creativity as an evaluation dimension?",
            "Creativity should not be evaluated for factual Q&A (precision matters more), "
            "technical documentation, legal or medical content, or any task where accuracy "
            "and precision are paramount. Creative elements like analogies can introduce "
            "inaccuracy in these contexts.",
        ),
        (
            "How do Flesch-Kincaid readability scores work and what are their limitations?",
            "Flesch-Kincaid uses average words per sentence and average syllables per word to "
            "estimate reading difficulty. Flesch Reading Ease gives 0-100 (higher = easier). "
            "Limitations: it only measures surface features, not conceptual difficulty; "
            "technical jargon may be necessary and appropriate; it does not account for "
            "audience expertise.",
        ),
        (
            "Design an evaluation pipeline for a customer-support chatbot.",
            "Prioritize: (1) Safety/Toxicity -- must never be harmful, (2) Correctness -- "
            "answers must be right, (3) Relevance -- must address the customer's question, "
            "(4) Helpfulness -- must be actionable, (5) Instruction Following -- must follow "
            "company guidelines, (6) Readability -- accessible to all customers, "
            "(7) Consistency -- same question should get consistent answers. Use automated "
            "heuristics for pre-filtering, LLM-as-Judge for deeper evaluation, and human "
            "review for edge cases.",
        ),
    ]

    for i, (question, answer) in enumerate(questions, 1):
        print(f"\n  Q{i}: {question}")
        print(f"  A{i}: {answer}")


# ===================================================================
# MAIN
# ===================================================================
def main() -> None:
    banner("CHAPTER 3: MODERN LLM EVALUATION - ALL 17 DIMENSIONS")
    print("\n  This script demonstrates every evaluation dimension implemented")
    print("  in evaluator.py using curated sample data and synthetic examples.")
    print("  Each dimension shows: problem, intuition, evaluation run, results,")
    print("  advantages, and limitations.\n")

    data = load_all_data()
    all_scores: dict[str, float] = {}

    # Run all 17 dimension demos
    all_scores["correctness"] = demo_correctness(data)
    all_scores["relevance"] = demo_relevance(data)
    all_scores["helpfulness"] = demo_helpfulness(data)
    all_scores["completeness"] = demo_completeness(data)
    all_scores["consistency"] = demo_consistency(data)
    all_scores["hallucination"] = demo_hallucination(data)
    all_scores["faithfulness"] = demo_faithfulness(data)
    all_scores["groundedness"] = demo_groundedness(data)
    all_scores["instruction_following"] = demo_instruction_following(data)
    all_scores["fluency"] = demo_fluency(data)
    all_scores["coherence"] = demo_coherence(data)
    all_scores["safety"] = demo_safety(data)
    all_scores["toxicity"] = demo_toxicity(data)
    all_scores["bias"] = demo_bias(data)
    all_scores["creativity"] = demo_creativity(data)
    all_scores["readability"] = demo_readability(data)
    all_scores["reasoning"] = demo_reasoning(data)

    # Multi-dimension combined evaluation
    multi_scores = demo_multi_dimension(data)
    # Merge multi-dimension scores (they override individual where available)
    combined_scores = {**all_scores, **multi_scores}

    # Summary table
    print_summary_table(combined_scores)

    # Interview questions
    print_interview_questions()

    # Final wrap-up
    banner("CHAPTER 3 COMPLETE")
    print(f"\n  All 17 evaluation dimensions demonstrated successfully.")
    print(f"  Dimensions evaluated : {len(all_scores)}")
    print(f"  Average score (good) : {sum(all_scores.values()) / len(all_scores):.4f}")
    print(f"\n  Key takeaway: Modern LLM evaluation is MULTI-DIMENSIONAL.")
    print(f"  No single metric captures output quality. Production systems")
    print(f"  combine heuristic baselines (this chapter) with LLM-as-Judge")
    print(f"  (Chapter 4) and human evaluation for comprehensive assessment.")
    print(f"\n{SEPARATOR}\n")


if __name__ == "__main__":
    main()
