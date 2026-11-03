"""
Chapter 3: Modern LLM Evaluation

Covers evaluation dimensions specific to LLM outputs:
- Correctness: does answer match expected result
- Relevance: is answer related to the question
- Helpfulness: is answer useful and complete
- Completeness: does answer cover required points
- Consistency: do multiple runs produce similar outputs
- Hallucination: does answer contain ungrounded claims
- Faithfulness: is answer grounded in provided context
- Groundedness: factual consistency with evidence
- Instruction following: compliance with given instructions
- Fluency: grammatical correctness and naturalness
- Coherence: logical flow and connectivity
- Safety: absence of harmful content
- Toxicity: absence of toxic language
- Bias: fairness and neutrality
- Creativity: originality and novelty
- Readability: clarity and accessibility
- Reasoning quality: quality of logical steps

Each dimension shown with simple heuristic function and examples.
"""

from statistics import mean


QUESTION = "Explain why the Roche limit matters in astronomy."
REFERENCE = "The Roche limit is the distance where tidal forces can break apart a moon or ring object."
GOOD_RESPONSE = (
    "The Roche limit matters because tidal forces from a planet can pull apart a nearby moon. "
    "It helps explain why rings form and why some bodies cannot stay intact."
)
BAD_RESPONSE = "Astronomy is interesting. Planets are big. The answer is probably gravity or something."
CONTEXT = "A moon that gets too close can be disrupted by tidal forces caused by the planet."


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def words(text):
    return set(text.lower().replace(".", "").split())


def overlap_score(a, b):
    left = words(a)
    right = words(b)
    if not left:
        return 0.0
    return len(left & right) / len(left)


def length_score(text):
    return min(len(text.split()) / 25, 1.0)


def correctness(response):
    return overlap_score(REFERENCE, response)


def relevance(question, response):
    return overlap_score(question, response)


def helpfulness(response):
    return mean([length_score(response), 1.0 if "because" in response.lower() else 0.3])


def completeness(response):
    required_phrases = ["tidal", "moon", "rings"]
    hits = 0
    for phrase in required_phrases:
        if phrase in response.lower():
            hits += 1
    return hits / len(required_phrases)


def consistency(responses):
    pair_scores = []
    for response in responses[1:]:
        pair_scores.append(overlap_score(responses[0], response))
    return mean(pair_scores)


def hallucination(context, response):
    grounded = overlap_score(response, context)
    return 1 - grounded


def faithfulness(context, response):
    return overlap_score(response, context)


def groundedness(context, response):
    return overlap_score(response, context)


def instruction_following(instruction, response):
    passed = 0
    if "explain" in instruction.lower() and len(response.split()) > 10:
        passed += 1
    if "clear" in instruction.lower() and "." in response:
        passed += 1
    return passed / 2


def fluency(response):
    has_capital = 1.0 if response[:1].isupper() else 0.0
    has_punctuation = 1.0 if response.strip().endswith(".") else 0.0
    return mean([has_capital, has_punctuation])


def coherence(response):
    return 1.0 if "because" in response.lower() or "helps explain" in response.lower() else 0.4


def safety(response):
    banned = ["attack", "kill", "harm"]
    for word in banned:
        if word in response.lower():
            return 0.0
    return 1.0


def toxicity(response):
    toxic_words = ["idiot", "stupid", "worthless"]
    found = 0
    for word in toxic_words:
        if word in response.lower():
            found += 1
    return 1 - min(found / len(toxic_words), 1.0)


def bias(response):
    biased_phrases = ["only men", "only women", "naturally better"]
    for phrase in biased_phrases:
        if phrase in response.lower():
            return 0.2
    return 1.0


def creativity(response):
    bonus = 1.0 if "like" in response.lower() or "imagine" in response.lower() else 0.4
    return mean([length_score(response), bonus])


def readability(response):
    average_word_length = mean(len(word) for word in response.split())
    if average_word_length <= 6:
        return 1.0
    if average_word_length <= 8:
        return 0.7
    return 0.4


def reasoning_quality(response):
    markers = ["because", "therefore", "so", "helps explain"]
    hits = 0
    for marker in markers:
        if marker in response.lower():
            hits += 1
    return min(hits / 3, 1.0)


def evaluate_all(name, response):
    section(name)
    scores = {
        "correctness": correctness(response),
        "relevance": relevance(QUESTION, response),
        "helpfulness": helpfulness(response),
        "completeness": completeness(response),
        "consistency": consistency([response, response]),
        "hallucination": hallucination(CONTEXT, response),
        "faithfulness": faithfulness(CONTEXT, response),
        "groundedness": groundedness(CONTEXT, response),
        "instruction_following": instruction_following("Explain in clear language.", response),
        "fluency": fluency(response),
        "coherence": coherence(response),
        "safety": safety(response),
        "toxicity": toxicity(response),
        "bias": bias(response),
        "creativity": creativity(response),
        "readability": readability(response),
        "reasoning_quality": reasoning_quality(response),
    }
    for key, value in scores.items():
        print(f"{key}: {value:.2f}")
    print(f"average: {mean(scores.values()):.2f}")


def main():
    section("Chapter 3: Modern LLM Evaluation")
    print(f"Question: {QUESTION}")
    print(f"Reference: {REFERENCE}")
    evaluate_all("Good Response", GOOD_RESPONSE)
    evaluate_all("Bad Response", BAD_RESPONSE)


if __name__ == "__main__":
    main()
