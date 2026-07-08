import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 3 - Modern LLM Evaluation: All 17 Dimensions Demonstrated
=================================================================

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
    banner("DIMENSION 1: CORRECTNESS")

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

    return res_good["score"]


# ===================================================================
# DIMENSION 2: RELEVANCE
# ===================================================================
def demo_relevance(data: dict) -> float:
    banner("DIMENSION 2: RELEVANCE")

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

    return res_good["score"]


# ===================================================================
# DIMENSION 3: HELPFULNESS
# ===================================================================
def demo_helpfulness(data: dict) -> float:
    banner("DIMENSION 3: HELPFULNESS")

    evaluator = HelpfulnessEvaluator()
    sample = data["sample"]
    sq = sample["science_questions"][0]
    good_resp = sample["llm_responses"]["good_responses"][0]["response"]
    unhelpful = "It is a concept in astronomy."

    res_good = evaluator.evaluate(sq["question"], good_resp)
    res_bad = evaluator.evaluate(sq["question"], unhelpful)

    print(f"\n  Question: {sq['question']}")
    print(f"\n  Helpful response:")
    print(f"    score={res_good['score']}, words={res_good['word_count']}, explanations={res_good['explanation_score']}, structure={res_good['structure_score']}")
    print(f"\n  Unhelpful response: '{unhelpful}'")
    print(f"    score={res_bad['score']}, words={res_bad['word_count']}, explanations={res_bad['explanation_score']}, structure={res_bad['structure_score']}")

    return res_good["score"]


# ===================================================================
# DIMENSION 4: COMPLETENESS
# ===================================================================
def demo_completeness(data: dict) -> float:
    banner("DIMENSION 4: COMPLETENESS")

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

    return res_complete["score"]


# ===================================================================
# DIMENSION 5: CONSISTENCY
# ===================================================================
def demo_consistency(data: dict) -> float:
    banner("DIMENSION 5: CONSISTENCY")

    evaluator = ConsistencyEvaluator()
    sample = data["sample"]

    consistent = sample["llm_responses"]["consistency_examples"][0]
    res_con = evaluator.evaluate(consistent["responses"])
    print(f"\n  Question: {consistent['question']}")
    print(f"  Expected consistent: {consistent['is_consistent']}")
    print(f"  Consistency score  : {res_con['score']}")
    print(f"  Avg pairwise sim   : {res_con['avg_pairwise_similarity']}")

    inconsistent = sample["llm_responses"]["consistency_examples"][1]
    res_inc = evaluator.evaluate(inconsistent["responses"])
    print(f"\n  Question: {inconsistent['question']}")
    print(f"  Expected consistent: {inconsistent['is_consistent']}")
    print(f"  Consistency score  : {res_inc['score']}")
    print(f"  Avg pairwise sim   : {res_inc['avg_pairwise_similarity']}")

    return res_con["score"]


# ===================================================================
# DIMENSION 6: HALLUCINATION DETECTION
# ===================================================================
def demo_hallucination(data: dict) -> float:
    banner("DIMENSION 6: HALLUCINATION DETECTION")

    evaluator = HallucinationEvaluator()
    simulated = data["simulated"]

    entry = simulated[0]
    sub_banner(f"Topic: {entry['page_title']}")
    print(f"  Source: {entry['source_text'][:100]}...")

    res_faithful = evaluator.evaluate(entry["source_text"], entry["faithful_response"])
    print(f"\n  Faithful response:")
    print(f"    Hallucination score: {res_faithful['score']} (1.0 = no hallucination)")
    print(f"    Hallucination rate : {res_faithful['hallucination_rate']}")
    print(f"    Sentences checked  : {res_faithful['total_sentences']}")

    res_halluc = evaluator.evaluate(entry["source_text"], entry["hallucinated_response"])
    print(f"\n  Hallucinated response:")
    print(f"    Hallucination score: {res_halluc['score']}")
    print(f"    Hallucination rate : {res_halluc['hallucination_rate']}")
    if res_halluc["sentence_analysis"]:
        for sa in res_halluc["sentence_analysis"][:3]:
            flag = "HALLUCINATED" if sa["likely_hallucinated"] else "grounded"
            print(f"    [{flag}] {sa['sentence'][:70]}...")

    sub_banner("Curated Hallucination Example (Froude Number)")
    sample = data["sample"]
    hall_ex = sample["llm_responses"]["hallucinated_responses"][0]
    res_hall = evaluator.evaluate(hall_ex["context_provided"], hall_ex["response"])
    print(f"  Score: {res_hall['score']}  (rate={res_hall['hallucination_rate']})")
    print(f"  Known hallucinated claims: {hall_ex['hallucinated_claims'][:2]}")

    return res_faithful["score"]


# ===================================================================
# DIMENSION 7: FAITHFULNESS
# ===================================================================
def demo_faithfulness(data: dict) -> float:
    banner("DIMENSION 7: FAITHFULNESS")

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

    return res_faith["score"]


# ===================================================================
# DIMENSION 8: GROUNDEDNESS
# ===================================================================
def demo_groundedness(data: dict) -> float:
    banner("DIMENSION 8: GROUNDEDNESS")

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

    return res_grounded["score"]


# ===================================================================
# DIMENSION 9: INSTRUCTION FOLLOWING
# ===================================================================
def demo_instruction_following(data: dict) -> float:
    banner("DIMENSION 9: INSTRUCTION FOLLOWING")

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

    return sum(scores) / len(scores) if scores else 0.0


# ===================================================================
# DIMENSION 10: FLUENCY
# ===================================================================
def demo_fluency(data: dict) -> float:
    banner("DIMENSION 10: FLUENCY")

    evaluator = FluencyEvaluator()
    sample = data["sample"]

    fluent = sample["llm_responses"]["good_responses"][2]["response"]
    nonfluent = sample["llm_responses"]["bad_responses"][2]["response"]

    res_fluent = evaluator.evaluate(fluent)
    res_nonfluent = evaluator.evaluate(nonfluent)

    print(f"\n  Fluent response (first 100 chars): '{fluent[:100]}...'")
    print(f"    score={res_fluent['score']}, capitalization={res_fluent['capitalization_score']}, repetition={res_fluent['repetition_score']}, punctuation={res_fluent['punctuation_score']}")

    print(f"\n  Non-fluent response (first 100 chars): '{nonfluent[:100]}...'")
    print(f"    score={res_nonfluent['score']}, capitalization={res_nonfluent['capitalization_score']}, repetition={res_nonfluent['repetition_score']}, punctuation={res_nonfluent['punctuation_score']}")

    return res_fluent["score"]


# ===================================================================
# DIMENSION 11: COHERENCE
# ===================================================================
def demo_coherence(data: dict) -> float:
    banner("DIMENSION 11: COHERENCE")

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

    return res_coh["score"]


# ===================================================================
# DIMENSION 12: SAFETY
# ===================================================================
def demo_safety(data: dict) -> float:
    banner("DIMENSION 12: SAFETY")

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

    return res_safe["score"]


# ===================================================================
# DIMENSION 13: TOXICITY
# ===================================================================
def demo_toxicity(data: dict) -> float:
    banner("DIMENSION 13: TOXICITY")

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

    return res_clean["score"]


# ===================================================================
# DIMENSION 14: BIAS
# ===================================================================
def demo_bias(data: dict) -> float:
    banner("DIMENSION 14: BIAS")

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

    return sum(scores) / len(scores) if scores else 0.0


# ===================================================================
# DIMENSION 15: CREATIVITY
# ===================================================================
def demo_creativity(data: dict) -> float:
    banner("DIMENSION 15: CREATIVITY")

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

    return res_creative["score"]


# ===================================================================
# DIMENSION 16: READABILITY
# ===================================================================
def demo_readability(data: dict) -> float:
    banner("DIMENSION 16: READABILITY")

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

    return res_readable["score"]


# ===================================================================
# DIMENSION 17: REASONING QUALITY
# ===================================================================
def demo_reasoning(data: dict) -> float:
    banner("DIMENSION 17: REASONING QUALITY")

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
        key_match = None
        for k in dim_keys:
            if name.lower().replace(" ", "_").startswith(k.lower().replace("_", "")[:6]):
                key_match = k
                break
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
# MAIN
# ===================================================================
def main() -> None:
    banner("CHAPTER 3: MODERN LLM EVALUATION - ALL 17 DIMENSIONS")

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
    combined_scores = {**all_scores, **multi_scores}

    # Summary table
    print_summary_table(combined_scores)

    # Final wrap-up
    banner("CHAPTER 3 COMPLETE")
    print(f"\n  All 17 evaluation dimensions demonstrated successfully.")
    print(f"  Dimensions evaluated : {len(all_scores)}")
    print(f"  Average score (good) : {sum(all_scores.values()) / len(all_scores):.4f}")
    print(f"\n  Key takeaway: Modern LLM evaluation is MULTI-DIMENSIONAL.")
    print(f"  No single metric captures output quality.")
    print(f"\n{SEPARATOR}\n")


if __name__ == "__main__":
    main()
