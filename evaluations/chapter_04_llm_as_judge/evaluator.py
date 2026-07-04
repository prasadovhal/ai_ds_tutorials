"""
Chapter 4 - LLM-as-a-Judge
Evaluator module: All judge implementations, prompt templates, and evaluation logic.

Every technique uses simulated judge responses by default so the code runs
without any external dependencies. Each class includes commented-out code
showing how to connect to Ollama + Mistral for real LLM judging.
"""

import json
import math
import random
import re
import statistics
import time
from collections import Counter, defaultdict
from typing import Optional


# ============================================================================
# UTILITY: Simulated LLM Call
# ============================================================================

def simulate_llm_call(prompt: str, seed: int = 0) -> str:
    """
    Simulate an LLM response for judging. In production, replace this
    with a real LLM call to Ollama/Mistral.

    This function deterministically generates plausible judge responses
    based on the content of the prompt.
    """
    # Use prompt hash for deterministic but varied responses
    rng = random.Random(hash(prompt) + seed)
    time.sleep(0.001)  # Simulate minimal latency
    return f"[simulated_llm_response_seed_{rng.randint(0, 9999)}]"


# --------------------------------------------------------------------------
# UNCOMMENT BELOW to use real Ollama + Mistral as the judge LLM.
# Make sure Ollama is running: `ollama serve`
# And pull the model: `ollama pull mistral`
#
# import requests
#
# def call_ollama(prompt: str, model: str = "mistral") -> str:
#     """Call Ollama API with the given prompt and return the response text."""
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": model,
#             "prompt": prompt,
#             "stream": False,
#             "options": {
#                 "temperature": 0.1,  # Low temperature for consistent judging
#                 "num_predict": 512,
#             },
#         },
#         timeout=120,
#     )
#     response.raise_for_status()
#     return response.json()["response"]
#
# # To enable real LLM judging, replace simulate_llm_call references with:
# # result = call_ollama(prompt, model="mistral")
# --------------------------------------------------------------------------


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

POINTWISE_PROMPT = """You are an expert evaluator. Rate the following response on a scale of 1 to 5.

Question: {question}

Reference Answer: {reference}

Model Response: {response}

Scoring Criteria:
1 = Completely wrong, irrelevant, or harmful
2 = Mostly wrong with minor correct elements
3 = Partially correct but missing key information
4 = Mostly correct with minor omissions or imprecisions
5 = Fully correct, comprehensive, and well-explained

Provide your evaluation in this exact format:
Score: [1-5]
Reasoning: [Your detailed reasoning]"""

PAIRWISE_PROMPT = """You are an expert evaluator. Compare these two responses and choose the better one.

Question: {question}

Reference Answer: {reference}

Response A: {response_a}

Response B: {response_b}

Evaluate based on: accuracy, completeness, clarity, and relevance.
You MUST choose one. Do not say they are equal.

Provide your evaluation in this exact format:
Winner: [A or B]
Reasoning: [Your detailed reasoning]"""

PASS_FAIL_PROMPT = """You are a quality assurance evaluator. Determine if this response meets minimum quality standards.

Question: {question}

Response: {response}

A response PASSES if it:
- Addresses the question directly
- Contains no factual errors
- Provides sufficient detail
- Is coherent and well-organized

A response FAILS if it:
- Does not address the question
- Contains significant factual errors
- Is too vague or incomplete
- Is incoherent or poorly organized

Provide your evaluation in this exact format:
Verdict: [PASS or FAIL]
Reasoning: [Your detailed reasoning]"""

LIKERT_PROMPT = """You are an expert evaluator. Rate this response on multiple dimensions using a Likert scale.

Question: {question}

Reference Answer: {reference}

Model Response: {response}

Rate each dimension from 1 (Strongly Disagree) to 5 (Strongly Agree):

1. The response is factually accurate.
2. The response is complete and comprehensive.
3. The response is clearly written and well-organized.
4. The response demonstrates deep understanding.
5. The response would be helpful to someone learning this topic.

Provide your evaluation in this exact format:
Accuracy: [1-5]
Completeness: [1-5]
Clarity: [1-5]
Depth: [1-5]
Helpfulness: [1-5]
Overall_Reasoning: [Your summary reasoning]"""

RUBRIC_PROMPT = """You are an expert evaluator. Score this response using the detailed rubric below.

Question: {question}

Reference Answer: {reference}

Model Response: {response}

RUBRIC:
Factual Accuracy (0-3):
  0 = Major factual errors
  1 = Some factual errors
  2 = Mostly accurate with minor issues
  3 = Fully accurate

Completeness (0-3):
  0 = Missing most key points
  1 = Covers some key points
  2 = Covers most key points
  3 = Covers all key points with additional insight

Explanation Quality (0-2):
  0 = No meaningful explanation
  1 = Basic explanation
  2 = Clear, intuitive explanation with examples

Technical Precision (0-2):
  0 = Imprecise or incorrect terminology
  1 = Generally correct terminology
  2 = Precise technical language throughout

Total possible: 10

Provide your evaluation in this exact format:
Factual_Accuracy: [0-3]
Completeness: [0-3]
Explanation_Quality: [0-2]
Technical_Precision: [0-2]
Total: [0-10]
Reasoning: [Your detailed reasoning]"""

GEVAL_PROMPT = """You are evaluating the quality of a model response. Follow these steps carefully.

Question: {question}

Reference Answer: {reference}

Model Response: {response}

EVALUATION STEPS:
Step 1: Read the question and understand what is being asked.
Step 2: Read the reference answer to understand the expected content.
Step 3: Read the model response carefully.
Step 4: Check factual accuracy - does the response contain errors?
Step 5: Check completeness - does it cover the key points from the reference?
Step 6: Check clarity - is the explanation clear and well-structured?
Step 7: Check for any hallucinations or fabricated information.
Step 8: Assign a score from 1-5 based on overall quality.

Show your chain-of-thought reasoning for each step, then provide a final score.

Format:
Step_1_Analysis: [your analysis]
Step_2_Analysis: [your analysis]
Step_3_Analysis: [your analysis]
Step_4_Accuracy: [your analysis]
Step_5_Completeness: [your analysis]
Step_6_Clarity: [your analysis]
Step_7_Hallucination: [your analysis]
Step_8_Score: [1-5]
Final_Reasoning: [summary]"""

CONSTITUTIONAL_PROMPT = """You are a constitutional evaluator. Evaluate this response against a set of principles.

Question: {question}

Response: {response}

PRINCIPLES:
1. Accuracy: The response must be factually correct.
2. Helpfulness: The response should genuinely help the user.
3. Harmlessness: The response should not contain harmful content.
4. Honesty: The response should acknowledge uncertainty when present.
5. Completeness: The response should address the full question.

For each principle, indicate if the response ADHERES or VIOLATES, with reasoning.

Format:
Accuracy: [ADHERES or VIOLATES] - [reason]
Helpfulness: [ADHERES or VIOLATES] - [reason]
Harmlessness: [ADHERES or VIOLATES] - [reason]
Honesty: [ADHERES or VIOLATES] - [reason]
Completeness: [ADHERES or VIOLATES] - [reason]
Overall_Verdict: [PASS or FAIL]"""

SELF_EVAL_PROMPT = """You previously generated the following response. Now evaluate your own work.

Question: {question}

Your Response: {response}

Evaluate yourself honestly:
1. What did you get right?
2. What did you miss or get wrong?
3. How could you improve this response?
4. Overall self-score (1-5)?

Format:
Strengths: [what was done well]
Weaknesses: [what was missed or wrong]
Improvements: [specific suggestions]
Self_Score: [1-5]"""

REFLEXION_PROMPT = """You are improving a response through reflection.

Question: {question}

Original Response: {original_response}

Evaluation Feedback: {feedback}

Based on the feedback, generate an improved response that addresses the identified weaknesses.

Improved Response:"""

MULTI_JUDGE_PROMPT = """You are Judge #{judge_id}, an expert evaluator with focus on {expertise}.

Question: {question}

Reference Answer: {reference}

Model Response: {response}

As a specialist in {expertise}, evaluate this response.
Score: [1-5]
Reasoning: [Your expert perspective]"""


# ============================================================================
# JUDGE IMPLEMENTATIONS
# ============================================================================

class PointwiseJudge:
    """
    Pointwise evaluation: Score one response at a time on a 1-5 scale.

    Problem: How do you rate a single model response objectively?
    Intuition: Like a teacher grading one student's essay — assign a score
               based on how well it answers the question.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = POINTWISE_PROMPT

    def build_prompt(self, question: str, response: str, reference: str = "") -> str:
        return self.prompt_template.format(
            question=question,
            reference=reference if reference else "[No reference provided]",
            response=response,
        )

    def simulate_judgment(
        self, question: str, response: str, reference: str = ""
    ) -> dict:
        """Simulate a pointwise score based on response quality heuristics."""
        prompt = self.build_prompt(question, response, reference)

        # Heuristic scoring based on response properties
        score = 3  # Base score
        response_lower = response.lower()
        ref_lower = reference.lower() if reference else ""

        # Length heuristic: very short = weak, reasonable length = decent
        word_count = len(response.split())
        if word_count > 80:
            score += 1
        if word_count > 150:
            score += 1
        if word_count < 30:
            score -= 1

        # Overlap heuristic: check keyword overlap with reference
        if reference:
            ref_words = set(ref_lower.split())
            resp_words = set(response_lower.split())
            # Filter short common words
            ref_keywords = {w for w in ref_words if len(w) > 4}
            if ref_keywords:
                overlap = len(resp_words & ref_keywords) / len(ref_keywords)
                if overlap > 0.5:
                    score += 1
                elif overlap < 0.2:
                    score -= 1

        # Add some randomness for realism
        score += self.rng.choice([-1, 0, 0, 0, 1])
        score = max(1, min(5, score))

        reasonings = {
            1: "The response is largely incorrect or irrelevant to the question asked.",
            2: "The response touches on the topic but contains significant errors or omissions.",
            3: "The response is partially correct and addresses the main point but lacks depth.",
            4: "The response is mostly correct and well-explained with minor gaps.",
            5: "The response is comprehensive, accurate, and demonstrates strong understanding.",
        }

        return {
            "method": "pointwise",
            "score": score,
            "max_score": 5,
            "reasoning": reasonings[score],
            "prompt_used": prompt[:200] + "...",
        }

    # ------------------------------------------------------------------
    # UNCOMMENT for real LLM judging:
    #
    # def judge_with_llm(self, question, response, reference=""):
    #     prompt = self.build_prompt(question, response, reference)
    #     llm_output = call_ollama(prompt, model="mistral")
    #     score = int(re.search(r"Score:\s*(\d)", llm_output).group(1))
    #     reasoning = re.search(r"Reasoning:\s*(.*)", llm_output, re.DOTALL)
    #     return {
    #         "method": "pointwise",
    #         "score": score,
    #         "max_score": 5,
    #         "reasoning": reasoning.group(1).strip() if reasoning else "",
    #         "raw_output": llm_output,
    #     }
    # ------------------------------------------------------------------


class PairwiseJudge:
    """
    Pairwise evaluation: Compare two responses head-to-head.

    Problem: Which of two model responses is better?
    Intuition: Like a taste test — you don't score each dish alone,
               you compare them directly and pick the winner.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = PAIRWISE_PROMPT

    def build_prompt(
        self, question: str, response_a: str, response_b: str, reference: str = ""
    ) -> str:
        return self.prompt_template.format(
            question=question,
            reference=reference if reference else "[No reference provided]",
            response_a=response_a,
            response_b=response_b,
        )

    def simulate_judgment(
        self,
        question: str,
        response_a: str,
        response_b: str,
        reference: str = "",
    ) -> dict:
        """Simulate pairwise comparison based on response quality heuristics."""
        prompt = self.build_prompt(question, response_a, response_b, reference)

        # Heuristic: compare depth and keyword coverage
        score_a = 0
        score_b = 0

        # Length comparison (slight advantage to more detailed responses)
        len_a = len(response_a.split())
        len_b = len(response_b.split())
        if len_a > len_b * 1.3:
            score_a += 1
        elif len_b > len_a * 1.3:
            score_b += 1

        # Reference keyword overlap
        if reference:
            ref_keywords = {
                w.lower() for w in reference.split() if len(w) > 4
            }
            overlap_a = len(
                {w.lower() for w in response_a.split()} & ref_keywords
            )
            overlap_b = len(
                {w.lower() for w in response_b.split()} & ref_keywords
            )
            if overlap_a > overlap_b:
                score_a += 2
            elif overlap_b > overlap_a:
                score_b += 2

        # Technical depth: look for numbers, equations, specific terms
        tech_markers = [
            "=", "formula", "equation", "theorem", "approximately",
            "specifically", "quantit", "exponent", "coefficient",
        ]
        tech_a = sum(1 for m in tech_markers if m in response_a.lower())
        tech_b = sum(1 for m in tech_markers if m in response_b.lower())
        if tech_a > tech_b:
            score_a += 1
        elif tech_b > tech_a:
            score_b += 1

        winner = "A" if score_a >= score_b else "B"
        # Small random upset chance
        if self.rng.random() < 0.1:
            winner = "B" if winner == "A" else "A"

        return {
            "method": "pairwise",
            "winner": winner,
            "score_a": score_a,
            "score_b": score_b,
            "reasoning": (
                f"Response {winner} is better because it provides more "
                f"{'detailed technical coverage' if winner == 'A' and score_a > score_b else 'accurate and focused content'}."
            ),
            "prompt_used": prompt[:200] + "...",
        }

    # ------------------------------------------------------------------
    # UNCOMMENT for real LLM judging:
    #
    # def judge_with_llm(self, question, response_a, response_b, reference=""):
    #     prompt = self.build_prompt(question, response_a, response_b, reference)
    #     llm_output = call_ollama(prompt, model="mistral")
    #     winner_match = re.search(r"Winner:\s*([AB])", llm_output)
    #     winner = winner_match.group(1) if winner_match else "A"
    #     reasoning = re.search(r"Reasoning:\s*(.*)", llm_output, re.DOTALL)
    #     return {
    #         "method": "pairwise",
    #         "winner": winner,
    #         "reasoning": reasoning.group(1).strip() if reasoning else "",
    #         "raw_output": llm_output,
    #     }
    # ------------------------------------------------------------------


class PassFailJudge:
    """
    Pass/Fail evaluation: Binary acceptable/not judgment.

    Problem: Is this response good enough to show to users?
    Intuition: Like a quality inspection on a factory line — pass or reject.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = PASS_FAIL_PROMPT

    def build_prompt(self, question: str, response: str) -> str:
        return self.prompt_template.format(question=question, response=response)

    def simulate_judgment(self, question: str, response: str) -> dict:
        """Simulate pass/fail based on quality heuristics."""
        prompt = self.build_prompt(question, response)

        word_count = len(response.split())
        has_structure = any(
            marker in response for marker in ["\n", ". ", ":", "1.", "-"]
        )

        # Pass criteria
        passes = True
        reasons = []

        if word_count < 15:
            passes = False
            reasons.append("Response is too short to be informative")
        if not has_structure and word_count > 50:
            reasons.append("Response lacks clear structure")
        if word_count > 10:
            question_words = {w.lower() for w in question.split() if len(w) > 4}
            response_words = {w.lower() for w in response.split()}
            relevance = len(question_words & response_words) / max(len(question_words), 1)
            if relevance < 0.1:
                passes = False
                reasons.append("Response does not address the question")

        if not reasons:
            reasons.append("Response adequately addresses the question with sufficient detail")

        return {
            "method": "pass_fail",
            "verdict": "PASS" if passes else "FAIL",
            "reasons": reasons,
            "word_count": word_count,
            "prompt_used": prompt[:200] + "...",
        }


class LikertJudge:
    """
    Likert scale evaluation: Rate on multiple dimensions.

    Problem: A single score doesn't tell you WHY a response is good or bad.
    Intuition: Like a restaurant review with separate ratings for food,
               service, ambiance — each dimension tells you something different.
    """

    DIMENSIONS = ["accuracy", "completeness", "clarity", "depth", "helpfulness"]

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = LIKERT_PROMPT

    def build_prompt(self, question: str, response: str, reference: str = "") -> str:
        return self.prompt_template.format(
            question=question,
            reference=reference if reference else "[No reference provided]",
            response=response,
        )

    def simulate_judgment(
        self, question: str, response: str, reference: str = ""
    ) -> dict:
        """Simulate multi-dimensional Likert scoring."""
        prompt = self.build_prompt(question, response, reference)

        word_count = len(response.split())
        base = 3

        # Quality heuristics per dimension
        if word_count > 100:
            base = 4
        if word_count > 200:
            base = 4

        scores = {}
        for dim in self.DIMENSIONS:
            s = base + self.rng.choice([-1, 0, 0, 1])
            # Depth and completeness benefit from length
            if dim in ("depth", "completeness") and word_count > 150:
                s += 1
            # Clarity penalized for excessive length
            if dim == "clarity" and word_count > 300:
                s -= 1
            scores[dim] = max(1, min(5, s))

        scores["average"] = round(
            sum(scores[d] for d in self.DIMENSIONS) / len(self.DIMENSIONS), 2
        )

        return {
            "method": "likert",
            "scores": scores,
            "dimensions": self.DIMENSIONS,
            "reasoning": f"Multi-dimensional assessment across {len(self.DIMENSIONS)} criteria.",
            "prompt_used": prompt[:200] + "...",
        }


class RubricJudge:
    """
    Rubric-based evaluation: Score against specific criteria with defined levels.

    Problem: Judges are inconsistent without clear scoring guidelines.
    Intuition: Like a standardized test rubric — each score level has a
               precise definition, reducing subjectivity.
    """

    RUBRIC = {
        "factual_accuracy": {"max": 3, "weight": 1.0},
        "completeness": {"max": 3, "weight": 1.0},
        "explanation_quality": {"max": 2, "weight": 1.0},
        "technical_precision": {"max": 2, "weight": 1.0},
    }

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = RUBRIC_PROMPT

    def build_prompt(self, question: str, response: str, reference: str = "") -> str:
        return self.prompt_template.format(
            question=question,
            reference=reference if reference else "[No reference provided]",
            response=response,
        )

    def simulate_judgment(
        self, question: str, response: str, reference: str = ""
    ) -> dict:
        """Simulate rubric-based scoring."""
        prompt = self.build_prompt(question, response, reference)

        word_count = len(response.split())
        scores = {}

        for criterion, config in self.RUBRIC.items():
            max_score = config["max"]
            # Base on response quality heuristics
            if word_count > 100:
                base = max_score - 1
            elif word_count > 50:
                base = max(1, max_score - 2)
            else:
                base = max(0, max_score - 2)

            # Add noise
            noise = self.rng.choice([-1, 0, 0, 1])
            scores[criterion] = max(0, min(max_score, base + noise))

        total = sum(scores.values())
        max_total = sum(c["max"] for c in self.RUBRIC.values())

        return {
            "method": "rubric",
            "scores": scores,
            "total": total,
            "max_total": max_total,
            "percentage": round(total / max_total * 100, 1),
            "rubric_definition": {
                k: f"0-{v['max']}" for k, v in self.RUBRIC.items()
            },
            "prompt_used": prompt[:200] + "...",
        }


class GEvalJudge:
    """
    G-Eval: Chain-of-thought evaluation framework.

    Problem: Single-step scoring is shallow and unreliable.
    Intuition: Make the judge "think out loud" through structured steps
               before assigning a score, just like a teacher writing
               comments before giving a grade.

    Based on: "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment"
    Key idea: Use chain-of-thought prompting to break evaluation into steps,
              then have the LLM reason through each step before scoring.
    """

    EVAL_STEPS = [
        "understand_question",
        "identify_reference_points",
        "analyze_response",
        "check_accuracy",
        "check_completeness",
        "check_clarity",
        "check_hallucination",
        "assign_score",
    ]

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = GEVAL_PROMPT

    def build_prompt(self, question: str, response: str, reference: str = "") -> str:
        return self.prompt_template.format(
            question=question,
            reference=reference if reference else "[No reference provided]",
            response=response,
        )

    def simulate_step_analysis(self, step: str, response: str, reference: str) -> dict:
        """Simulate analysis for one G-Eval step."""
        word_count = len(response.split())
        analyses = {
            "understand_question": "The question asks for an explanation of a specific scientific concept.",
            "identify_reference_points": f"Key points from reference: {len(reference.split())} words covering core concepts.",
            "analyze_response": f"Response contains {word_count} words with {'detailed' if word_count > 100 else 'brief'} coverage.",
            "check_accuracy": "Response appears factually consistent with established scientific understanding.",
            "check_completeness": f"Response covers {'most' if word_count > 80 else 'some'} of the key points from the reference.",
            "check_clarity": f"Response is {'well-structured and clear' if word_count > 50 else 'concise but may lack detail'}.",
            "check_hallucination": "No obvious fabricated claims detected.",
            "assign_score": "Based on the above analysis, assigning score.",
        }
        return {
            "step": step,
            "analysis": analyses.get(step, "Analysis completed."),
            "confidence": round(0.7 + self.rng.random() * 0.3, 2),
        }

    def simulate_judgment(
        self, question: str, response: str, reference: str = ""
    ) -> dict:
        """Simulate full G-Eval chain-of-thought evaluation."""
        prompt = self.build_prompt(question, response, reference)

        # Step-by-step reasoning
        step_results = []
        for step in self.EVAL_STEPS:
            result = self.simulate_step_analysis(step, response, reference)
            step_results.append(result)

        # Compute final score based on step analyses
        word_count = len(response.split())
        base_score = 3
        if word_count > 100:
            base_score = 4
        if word_count > 200:
            base_score = 5

        # Average confidence across steps influences score
        avg_confidence = statistics.mean(s["confidence"] for s in step_results)
        if avg_confidence > 0.85:
            base_score = min(5, base_score + 1)

        noise = self.rng.choice([-1, 0, 0, 0, 1])
        final_score = max(1, min(5, base_score + noise))

        return {
            "method": "g_eval",
            "chain_of_thought": step_results,
            "num_steps": len(self.EVAL_STEPS),
            "final_score": final_score,
            "max_score": 5,
            "avg_confidence": round(avg_confidence, 3),
            "reasoning": (
                f"After {len(self.EVAL_STEPS)}-step chain-of-thought analysis, "
                f"the response scores {final_score}/5 with {avg_confidence:.0%} average confidence."
            ),
            "prompt_used": prompt[:200] + "...",
        }


class ConstitutionalJudge:
    """
    Constitutional evaluation: Evaluate against a set of principles.

    Problem: How do you ensure responses are safe, honest, and helpful?
    Intuition: Like a constitutional court checking if a law aligns with
               the constitution — check the response against core principles.

    Based on: Anthropic's Constitutional AI paper.
    """

    PRINCIPLES = [
        {"name": "accuracy", "description": "The response must be factually correct."},
        {"name": "helpfulness", "description": "The response should genuinely help the user."},
        {"name": "harmlessness", "description": "The response should not contain harmful content."},
        {"name": "honesty", "description": "The response should acknowledge uncertainty."},
        {"name": "completeness", "description": "The response should address the full question."},
    ]

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = CONSTITUTIONAL_PROMPT

    def build_prompt(self, question: str, response: str) -> str:
        return self.prompt_template.format(question=question, response=response)

    def simulate_judgment(self, question: str, response: str) -> dict:
        """Simulate constitutional evaluation against principles."""
        prompt = self.build_prompt(question, response)

        word_count = len(response.split())
        results = {}

        for principle in self.PRINCIPLES:
            name = principle["name"]
            # Most responses adhere to most principles
            adheres = True
            reason = f"Response {principle['description'].lower().replace('the response ', '').rstrip('.')}"

            # Simulate occasional violations
            if name == "completeness" and word_count < 30:
                adheres = False
                reason = "Response is too brief to fully address the question"
            elif name == "accuracy" and self.rng.random() < 0.1:
                adheres = False
                reason = "Response contains a potentially inaccurate claim"

            results[name] = {
                "adheres": adheres,
                "verdict": "ADHERES" if adheres else "VIOLATES",
                "reason": reason,
            }

        all_adhere = all(r["adheres"] for r in results.values())
        violations = [
            name for name, r in results.items() if not r["adheres"]
        ]

        return {
            "method": "constitutional",
            "principles_checked": len(self.PRINCIPLES),
            "results": results,
            "overall_verdict": "PASS" if all_adhere else "FAIL",
            "violations": violations,
            "prompt_used": prompt[:200] + "...",
        }


class SelfEvaluator:
    """
    Self-evaluation: Model evaluates its own output.

    Problem: Can a model identify its own mistakes?
    Intuition: Like self-grading a test — the model reviews what it wrote
               and identifies strengths and weaknesses.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.prompt_template = SELF_EVAL_PROMPT

    def build_prompt(self, question: str, response: str) -> str:
        return self.prompt_template.format(question=question, response=response)

    def simulate_judgment(self, question: str, response: str) -> dict:
        """Simulate self-evaluation."""
        prompt = self.build_prompt(question, response)

        word_count = len(response.split())
        base_score = 3

        # Self-evaluation tends to be slightly generous (known bias)
        if word_count > 100:
            base_score = 4
        base_score += self.rng.choice([0, 0, 1])  # Slight positive bias
        self_score = max(1, min(5, base_score))

        strengths = []
        weaknesses = []
        improvements = []

        if word_count > 80:
            strengths.append("Provides detailed explanation with good coverage")
        else:
            weaknesses.append("Could be more detailed")
            improvements.append("Add more specific examples and explanations")

        if any(c in response for c in [".", ",", ";", ":"]):
            strengths.append("Uses proper sentence structure")
        else:
            weaknesses.append("Sentence structure could be improved")

        if "\n" in response or "1." in response or "-" in response:
            strengths.append("Well-organized with clear structure")
        else:
            improvements.append("Add better structural organization (lists, paragraphs)")

        if not weaknesses:
            weaknesses.append("Minor areas could benefit from additional examples")
        if not improvements:
            improvements.append("Could add real-world applications or analogies")

        return {
            "method": "self_evaluation",
            "self_score": self_score,
            "max_score": 5,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvements": improvements,
            "bias_warning": "Self-evaluation tends to be generous (positive bias)",
            "prompt_used": prompt[:200] + "...",
        }


class ReflexionEvaluator:
    """
    Reflexion: Iterative self-improvement through evaluation.

    Problem: How do you make a model improve its own response?
    Intuition: Like revising a draft — write, get feedback, revise, repeat.
               Each iteration should produce a better response.

    Based on: "Reflexion: Language Agents with Verbal Reinforcement Learning"
    """

    def __init__(self, max_iterations: int = 3, seed: int = 42):
        self.max_iterations = max_iterations
        self.rng = random.Random(seed)

    def simulate_iteration(
        self, question: str, response: str, iteration: int
    ) -> dict:
        """Simulate one reflexion iteration: evaluate then improve."""
        word_count = len(response.split())

        # Simulate feedback
        feedback_templates = [
            "The response could be more specific about key mechanisms.",
            "Consider adding quantitative details or examples.",
            "The explanation would benefit from mentioning historical context.",
            "Add more precise technical terminology.",
            "Include practical implications or real-world applications.",
        ]
        feedback = feedback_templates[iteration % len(feedback_templates)]

        # Simulate improvement: add a sentence
        improvement_additions = [
            " This mechanism is fundamental to our understanding of the topic.",
            " Quantitatively, the effect has been measured to high precision in experiments.",
            " Historically, this concept transformed our understanding of the field.",
            " In practical applications, this principle is widely used in engineering.",
            " Recent research has further validated and extended these findings.",
        ]
        improved_response = response + improvement_additions[
            iteration % len(improvement_additions)
        ]

        # Score should generally improve with each iteration
        score_base = min(5, 3 + iteration)
        score = max(1, min(5, score_base + self.rng.choice([-1, 0, 0, 1])))

        return {
            "iteration": iteration + 1,
            "feedback": feedback,
            "improved_response": improved_response[:300] + "..." if len(improved_response) > 300 else improved_response,
            "score": score,
            "improvement_delta": f"+{max(0, score - (score_base - 1))}",
        }

    def simulate_full_reflexion(self, question: str, initial_response: str) -> dict:
        """Run full reflexion loop: evaluate -> feedback -> improve -> repeat."""
        iterations = []
        current_response = initial_response

        for i in range(self.max_iterations):
            result = self.simulate_iteration(question, current_response, i)
            iterations.append(result)
            current_response = result["improved_response"]

        return {
            "method": "reflexion",
            "total_iterations": self.max_iterations,
            "iterations": iterations,
            "initial_score": iterations[0]["score"] - 1 if iterations else 0,
            "final_score": iterations[-1]["score"] if iterations else 0,
            "score_trajectory": [it["score"] for it in iterations],
        }


class MultiJudgePanel:
    """
    Multi-agent judging: Multiple judges evaluate for consensus.

    Problem: One judge can be biased or wrong. How to increase reliability?
    Intuition: Like a panel of reviewers — aggregate multiple expert opinions
               to get a more robust assessment.
    """

    EXPERT_PROFILES = [
        {"id": 1, "expertise": "factual accuracy and scientific rigor"},
        {"id": 2, "expertise": "clarity and pedagogical quality"},
        {"id": 3, "expertise": "completeness and depth of coverage"},
    ]

    def __init__(self, num_judges: int = 3, seed: int = 42):
        self.num_judges = min(num_judges, len(self.EXPERT_PROFILES))
        self.rng = random.Random(seed)
        self.prompt_template = MULTI_JUDGE_PROMPT

    def build_prompt(
        self, judge_id: int, expertise: str, question: str,
        response: str, reference: str = ""
    ) -> str:
        return self.prompt_template.format(
            judge_id=judge_id,
            expertise=expertise,
            question=question,
            reference=reference if reference else "[No reference provided]",
            response=response,
        )

    def simulate_judgment(
        self, question: str, response: str, reference: str = ""
    ) -> dict:
        """Simulate multi-judge evaluation with consensus."""
        word_count = len(response.split())
        base_score = 3
        if word_count > 100:
            base_score = 4

        judge_results = []
        for profile in self.EXPERT_PROFILES[:self.num_judges]:
            prompt = self.build_prompt(
                profile["id"], profile["expertise"],
                question, response, reference,
            )
            # Each judge has slightly different standards
            noise = self.rng.choice([-1, 0, 0, 1, 1])
            score = max(1, min(5, base_score + noise))
            judge_results.append({
                "judge_id": profile["id"],
                "expertise": profile["expertise"],
                "score": score,
                "reasoning": f"From the perspective of {profile['expertise']}, this response scores {score}/5.",
            })

        scores = [j["score"] for j in judge_results]
        mean_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0

        return {
            "method": "multi_judge",
            "num_judges": self.num_judges,
            "individual_scores": judge_results,
            "consensus_score": round(mean_score, 2),
            "median_score": statistics.median(scores),
            "std_dev": round(std_dev, 2),
            "agreement": "high" if std_dev < 0.8 else "moderate" if std_dev < 1.5 else "low",
            "score_range": f"{min(scores)}-{max(scores)}",
        }


class ArenaEvaluator:
    """
    Arena-style evaluation: Tournament bracket approach.

    Problem: How do you rank many models fairly?
    Intuition: Like a sports tournament — models play matches, winners
               advance, and a ranking emerges through head-to-head competition.

    Based on: LMSYS Chatbot Arena concept.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.match_results = []

    def simulate_match(
        self, model_a: str, model_b: str, question_id: int,
        response_a: str, response_b: str,
    ) -> dict:
        """Simulate a single head-to-head match."""
        pairwise = PairwiseJudge(seed=hash(f"{model_a}{model_b}{question_id}"))
        result = pairwise.simulate_judgment(
            f"Question {question_id}", response_a, response_b,
        )

        match = {
            "question_id": question_id,
            "model_a": model_a,
            "model_b": model_b,
            "winner": model_a if result["winner"] == "A" else model_b,
            "loser": model_b if result["winner"] == "A" else model_a,
        }
        self.match_results.append(match)
        return match

    def get_win_rates(self) -> dict:
        """Calculate win rates for all models."""
        wins = Counter()
        total = Counter()

        for match in self.match_results:
            wins[match["winner"]] += 1
            total[match["model_a"]] += 1
            total[match["model_b"]] += 1

        rates = {}
        for model in total:
            rates[model] = {
                "wins": wins[model],
                "total": total[model],
                "win_rate": round(wins[model] / total[model], 3) if total[model] > 0 else 0,
            }

        return dict(sorted(rates.items(), key=lambda x: x[1]["win_rate"], reverse=True))

    def get_leaderboard(self) -> list[dict]:
        """Return sorted leaderboard."""
        rates = self.get_win_rates()
        board = []
        for rank, (model, stats) in enumerate(rates.items(), 1):
            board.append({
                "rank": rank,
                "model": model,
                "wins": stats["wins"],
                "total": stats["total"],
                "win_rate": stats["win_rate"],
            })
        return board


class EloRatingSystem:
    """
    Tournament evaluation with Elo ratings.

    Problem: Win rates don't account for opponent strength.
    Intuition: Like chess Elo ratings — beating a strong player earns
               more points than beating a weak player. The rating converges
               to a model's true skill level over many matches.

    Formula:
      Expected score: E_a = 1 / (1 + 10^((R_b - R_a) / 400))
      Updated rating: R_a' = R_a + K * (S_a - E_a)
      where K is the update factor (typically 32), S_a is the actual
      score (1 for win, 0.5 for draw, 0 for loss).
    """

    def __init__(self, k_factor: int = 32, initial_rating: int = 1500):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings = {}
        self.history = []

    def get_rating(self, model: str) -> float:
        if model not in self.ratings:
            self.ratings[model] = float(self.initial_rating)
        return self.ratings[model]

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for player A against player B."""
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))

    def update_ratings(self, winner: str, loser: str, draw: bool = False):
        """Update Elo ratings after a match."""
        r_a = self.get_rating(winner)
        r_b = self.get_rating(loser)

        e_a = self.expected_score(r_a, r_b)
        e_b = self.expected_score(r_b, r_a)

        if draw:
            s_a, s_b = 0.5, 0.5
        else:
            s_a, s_b = 1.0, 0.0

        self.ratings[winner] = r_a + self.k_factor * (s_a - e_a)
        self.ratings[loser] = r_b + self.k_factor * (s_b - e_b)

        self.history.append({
            "winner": winner,
            "loser": loser,
            "draw": draw,
            "winner_rating_before": round(r_a, 1),
            "winner_rating_after": round(self.ratings[winner], 1),
            "loser_rating_before": round(r_b, 1),
            "loser_rating_after": round(self.ratings[loser], 1),
            "expected_win_prob": round(e_a, 3),
        })

    def get_leaderboard(self) -> list[dict]:
        """Return models sorted by Elo rating."""
        board = []
        for rank, (model, rating) in enumerate(
            sorted(self.ratings.items(), key=lambda x: x[1], reverse=True), 1
        ):
            board.append({
                "rank": rank,
                "model": model,
                "elo_rating": round(rating, 1),
                "matches": sum(
                    1 for h in self.history
                    if h["winner"] == model or h["loser"] == model
                ),
            })
        return board


# ============================================================================
# JUDGE AGREEMENT & RELIABILITY
# ============================================================================

class JudgeAgreement:
    """
    Measure inter-judge reliability using various agreement metrics.

    Problem: How consistent are different judges when evaluating the same response?
    Intuition: If two judges always agree, the evaluation is reliable.
               If they disagree often, the rubric may be ambiguous.
    """

    @staticmethod
    def percent_agreement(scores_a: list[int], scores_b: list[int]) -> float:
        """Simple percent agreement between two judges."""
        if len(scores_a) != len(scores_b):
            raise ValueError("Score lists must have the same length")
        agreements = sum(1 for a, b in zip(scores_a, scores_b) if a == b)
        return round(agreements / len(scores_a), 4)

    @staticmethod
    def cohens_kappa(scores_a: list[int], scores_b: list[int]) -> float:
        """
        Cohen's Kappa: Agreement corrected for chance.
        kappa = (p_o - p_e) / (1 - p_e)
        where p_o = observed agreement, p_e = expected agreement by chance.
        """
        n = len(scores_a)
        if n == 0:
            return 0.0

        # Observed agreement
        p_o = sum(1 for a, b in zip(scores_a, scores_b) if a == b) / n

        # Expected agreement by chance
        labels = sorted(set(scores_a) | set(scores_b))
        p_e = 0.0
        for label in labels:
            p_a = scores_a.count(label) / n
            p_b = scores_b.count(label) / n
            p_e += p_a * p_b

        if p_e == 1.0:
            return 1.0
        return round((p_o - p_e) / (1 - p_e), 4)

    @staticmethod
    def correlation(scores_a: list[float], scores_b: list[float]) -> float:
        """Pearson correlation between two score lists."""
        n = len(scores_a)
        if n < 2:
            return 0.0

        mean_a = statistics.mean(scores_a)
        mean_b = statistics.mean(scores_b)

        cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(scores_a, scores_b)) / n
        std_a = statistics.pstdev(scores_a)
        std_b = statistics.pstdev(scores_b)

        if std_a == 0 or std_b == 0:
            return 0.0
        return round(cov / (std_a * std_b), 4)

    @staticmethod
    def mean_absolute_difference(scores_a: list[float], scores_b: list[float]) -> float:
        """Average absolute difference between two judges' scores."""
        diffs = [abs(a - b) for a, b in zip(scores_a, scores_b)]
        return round(statistics.mean(diffs), 4)


class JudgeReliability:
    """
    Measure judge consistency and calibration.

    Problem: Is a single judge consistent with itself over time?
    Intuition: Show the judge the same response twice — does it give
               the same score? If not, the judge is unreliable.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def test_retest_reliability(
        self, judge, question: str, response: str, reference: str = "",
        num_trials: int = 5,
    ) -> dict:
        """Run the same judgment multiple times and measure consistency."""
        scores = []
        for trial in range(num_trials):
            # Vary the seed slightly to simulate judge variability
            judge_copy = type(judge)(seed=42 + trial)
            result = judge_copy.simulate_judgment(question, response, reference)
            if "score" in result:
                scores.append(result["score"])
            elif "final_score" in result:
                scores.append(result["final_score"])
            elif "scores" in result and "average" in result["scores"]:
                scores.append(result["scores"]["average"])

        if not scores:
            return {"error": "Could not extract scores from judge"}

        return {
            "num_trials": num_trials,
            "scores": scores,
            "mean": round(statistics.mean(scores), 2),
            "std_dev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            "range": max(scores) - min(scores),
            "is_consistent": (max(scores) - min(scores)) <= 1,
            "consistency_rating": (
                "high" if (max(scores) - min(scores)) <= 1 else
                "moderate" if (max(scores) - min(scores)) <= 2 else "low"
            ),
        }

    def calibration_test(
        self, judge, items: list[dict], expected_order: list[str]
    ) -> dict:
        """
        Test if judge scores align with expected quality ordering.
        Items should be ordered from best to worst in expected_order.
        """
        scores = {}
        for item in items:
            label = item["label"]
            result = judge.simulate_judgment(
                item["question"], item["response"],
                item.get("reference", ""),
            )
            if "score" in result:
                scores[label] = result["score"]
            elif "final_score" in result:
                scores[label] = result["final_score"]

        # Check if scoring matches expected order
        expected_scores = [scores.get(label, 0) for label in expected_order]
        is_monotonic = all(
            expected_scores[i] >= expected_scores[i + 1]
            for i in range(len(expected_scores) - 1)
        )

        return {
            "scores": scores,
            "expected_order": expected_order,
            "actual_order": sorted(scores.keys(), key=lambda x: scores[x], reverse=True),
            "is_correctly_ordered": is_monotonic,
            "calibration": "good" if is_monotonic else "needs_improvement",
        }


# ============================================================================
# BIAS DETECTION
# ============================================================================

class BiasDetector:
    """
    Detect common biases in LLM judges.

    Biases tested:
    1. Verbosity bias: Preferring longer responses regardless of quality
    2. Position bias: Preferring whichever response appears first (or second)
    3. Self-favoritism: Preferring responses from the same model family
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def test_verbosity_bias(
        self, judge, question: str, concise: str, verbose: str,
        reference: str = "",
    ) -> dict:
        """
        Test if the judge prefers verbose responses over concise ones
        that contain the same information.
        """
        # Score concise response
        score_concise = judge.simulate_judgment(question, concise, reference)
        # Score verbose response
        score_verbose = judge.simulate_judgment(question, verbose, reference)

        sc = score_concise.get("score", score_concise.get("final_score", 0))
        sv = score_verbose.get("score", score_verbose.get("final_score", 0))

        return {
            "bias_type": "verbosity",
            "concise_score": sc,
            "verbose_score": sv,
            "concise_word_count": len(concise.split()),
            "verbose_word_count": len(verbose.split()),
            "prefers_verbose": sv > sc,
            "bias_detected": sv > sc,
            "bias_magnitude": sv - sc,
            "recommendation": (
                "Judge shows verbosity bias - consider normalizing for length"
                if sv > sc else
                "No significant verbosity bias detected"
            ),
        }

    def test_position_bias(
        self, judge, question: str, response_a: str, response_b: str,
        reference: str = "", num_swaps: int = 5,
    ) -> dict:
        """
        Test if the judge prefers the first or second position by
        swapping response order and checking consistency.
        """
        first_wins = 0
        total = 0

        for i in range(num_swaps):
            if isinstance(judge, PairwiseJudge):
                # Original order
                r1 = judge.simulate_judgment(question, response_a, response_b, reference)
                a_wins_original = r1["winner"] == "A"

                # Swapped order
                judge_swapped = PairwiseJudge(seed=42 + i + 100)
                r2 = judge_swapped.simulate_judgment(question, response_b, response_a, reference)
                a_wins_swapped = r2["winner"] == "B"  # B in swapped = A in original

                if a_wins_original:
                    first_wins += 1
                total += 1

                if a_wins_swapped:
                    pass  # Consistent
                else:
                    first_wins += 1
                total += 1

        position_rate = first_wins / total if total > 0 else 0.5
        bias_detected = abs(position_rate - 0.5) > 0.2

        return {
            "bias_type": "position",
            "first_position_win_rate": round(position_rate, 3),
            "expected_fair_rate": 0.5,
            "num_trials": total,
            "bias_detected": bias_detected,
            "bias_direction": (
                "first_position" if position_rate > 0.6 else
                "second_position" if position_rate < 0.4 else "none"
            ),
            "recommendation": (
                "Swap response positions and average to mitigate position bias"
                if bias_detected else "Position bias within acceptable range"
            ),
        }

    def test_length_bias(
        self, judge, question: str, reference: str = "",
        num_lengths: int = 5,
    ) -> dict:
        """
        Test if scores correlate with response length regardless of content.
        Generate responses of increasing length and check score trend.
        """
        base = "This concept is important in physics."
        padding = " It has wide-ranging implications for our understanding of the natural world."

        results = []
        for i in range(num_lengths):
            response = base + padding * i
            result = judge.simulate_judgment(question, response, reference)
            score = result.get("score", result.get("final_score", 0))
            results.append({
                "word_count": len(response.split()),
                "score": score,
            })

        scores = [r["score"] for r in results]
        lengths = [r["word_count"] for r in results]

        # Check correlation between length and score
        if len(scores) > 1:
            corr = JudgeAgreement.correlation(
                [float(l) for l in lengths],
                [float(s) for s in scores],
            )
        else:
            corr = 0.0

        return {
            "bias_type": "length",
            "results": results,
            "length_score_correlation": corr,
            "bias_detected": abs(corr) > 0.5,
            "recommendation": (
                "Strong length-score correlation detected - judge favors longer responses"
                if corr > 0.5 else
                "Judge penalizes longer responses"
                if corr < -0.5 else
                "No significant length bias detected"
            ),
        }

    def test_self_favoritism(
        self, judge, question: str, own_response: str,
        other_response: str, reference: str = "",
    ) -> dict:
        """
        Test if a model-as-judge favors its own outputs over others.
        (Simulated: in practice, you'd use the same model for judging
        that produced one of the responses.)
        """
        score_own = judge.simulate_judgment(question, own_response, reference)
        score_other = judge.simulate_judgment(question, other_response, reference)

        s_own = score_own.get("score", score_own.get("final_score", 0))
        s_other = score_other.get("score", score_other.get("final_score", 0))

        return {
            "bias_type": "self_favoritism",
            "own_model_score": s_own,
            "other_model_score": s_other,
            "prefers_own": s_own > s_other,
            "bias_detected": s_own > s_other,
            "bias_magnitude": s_own - s_other,
            "recommendation": (
                "Judge shows self-favoritism bias - use a different model as judge"
                if s_own > s_other else
                "No significant self-favoritism detected"
            ),
        }


# ============================================================================
# META-EVALUATION
# ============================================================================

class MetaEvaluator:
    """
    Meta-evaluation: Evaluating the evaluator.

    Problem: How do you know your judge is good?
    Intuition: Compare judge scores with human scores. A good judge
               should agree with humans most of the time.
    """

    def __init__(self):
        self.judge_scores = []
        self.human_scores = []

    def add_evaluation(self, judge_score: float, human_score: float):
        """Record a paired judge-human evaluation."""
        self.judge_scores.append(judge_score)
        self.human_scores.append(human_score)

    def compute_agreement(self) -> dict:
        """Compute agreement between judge and human evaluations."""
        n = len(self.judge_scores)
        if n == 0:
            return {"error": "No evaluations recorded"}

        # Exact agreement
        exact = sum(
            1 for j, h in zip(self.judge_scores, self.human_scores) if j == h
        ) / n

        # Within-1 agreement
        within_1 = sum(
            1 for j, h in zip(self.judge_scores, self.human_scores)
            if abs(j - h) <= 1
        ) / n

        # Correlation
        corr = JudgeAgreement.correlation(self.judge_scores, self.human_scores)

        # Mean absolute error
        mae = statistics.mean(
            abs(j - h) for j, h in zip(self.judge_scores, self.human_scores)
        )

        # Direction agreement (both say good/bad)
        threshold = 3.0
        direction_agree = sum(
            1 for j, h in zip(self.judge_scores, self.human_scores)
            if (j >= threshold) == (h >= threshold)
        ) / n

        return {
            "num_evaluations": n,
            "exact_agreement": round(exact, 4),
            "within_1_agreement": round(within_1, 4),
            "correlation": corr,
            "mean_absolute_error": round(mae, 4),
            "direction_agreement": round(direction_agree, 4),
            "judge_mean": round(statistics.mean(self.judge_scores), 2),
            "human_mean": round(statistics.mean(self.human_scores), 2),
            "judge_tends": (
                "generous" if statistics.mean(self.judge_scores) > statistics.mean(self.human_scores) + 0.3
                else "strict" if statistics.mean(self.judge_scores) < statistics.mean(self.human_scores) - 0.3
                else "well-calibrated"
            ),
        }


# ============================================================================
# BLEU / ROUGE INSUFFICIENCY DEMO
# ============================================================================

class ClassicalMetricsDemonstrator:
    """
    Demonstrates why BLEU and ROUGE are insufficient for LLM evaluation.
    Shows cases where these metrics fail to capture response quality.
    """

    @staticmethod
    def compute_simple_bleu(reference: str, candidate: str, n: int = 1) -> float:
        """
        Simplified BLEU score (unigram precision).
        BLEU = (matching n-grams in candidate) / (total n-grams in candidate)
        """
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()

        if not cand_tokens:
            return 0.0

        ref_ngrams = Counter()
        for i in range(len(ref_tokens) - n + 1):
            ngram = tuple(ref_tokens[i:i + n])
            ref_ngrams[ngram] += 1

        cand_ngrams = Counter()
        for i in range(len(cand_tokens) - n + 1):
            ngram = tuple(cand_tokens[i:i + n])
            cand_ngrams[ngram] += 1

        matches = 0
        for ngram, count in cand_ngrams.items():
            matches += min(count, ref_ngrams.get(ngram, 0))

        total_cand_ngrams = max(1, len(cand_tokens) - n + 1)
        return round(matches / total_cand_ngrams, 4)

    @staticmethod
    def compute_simple_rouge_l(reference: str, candidate: str) -> float:
        """
        Simplified ROUGE-L (longest common subsequence F1).
        """
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()

        if not ref_tokens or not cand_tokens:
            return 0.0

        # LCS via dynamic programming
        m, n = len(ref_tokens), len(cand_tokens)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref_tokens[i - 1] == cand_tokens[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        lcs_length = dp[m][n]

        precision = lcs_length / n if n > 0 else 0
        recall = lcs_length / m if m > 0 else 0

        if precision + recall == 0:
            return 0.0
        f1 = 2 * precision * recall / (precision + recall)
        return round(f1, 4)

    def demonstrate_failures(self) -> list[dict]:
        """Show cases where BLEU/ROUGE fail to capture quality."""
        cases = [
            {
                "name": "Paraphrase (same meaning, different words)",
                "question": "What is the Roche limit?",
                "reference": "The Roche limit is the distance within which a celestial body will disintegrate due to tidal forces.",
                "good_answer": "The Roche limit defines the critical orbital radius where tidal stresses from a massive object overcome the gravitational self-binding of a smaller body, tearing it apart.",
                "bad_answer": "The Roche limit is the distance within which a celestial body will disintegrate due to tidal forces. Yes, tidal forces.",
                "expected": "Good answer should score higher (it adds insight), but BLEU rewards word overlap.",
            },
            {
                "name": "Correct but different structure",
                "question": "Explain the butterfly effect.",
                "reference": "Small changes in initial conditions lead to large differences in outcomes in chaotic systems.",
                "good_answer": "In chaos theory, even tiny perturbations to a system's starting state can amplify exponentially, making long-term prediction fundamentally impossible despite deterministic governing equations.",
                "bad_answer": "Small changes in initial conditions can sometimes lead to large differences. Changes are small. Conditions are initial. Large differences in outcomes happen.",
                "expected": "Good answer captures the concept deeply; bad answer just repeats words.",
            },
            {
                "name": "Hallucination with correct words",
                "question": "What causes tides?",
                "reference": "Tides are caused by the gravitational pull of the Moon and Sun on Earth's oceans.",
                "good_answer": "Ocean tides result from the differential gravitational attraction exerted by the Moon (primarily) and the Sun on different parts of Earth.",
                "bad_answer": "Tides are caused by the gravitational pull of Jupiter and Mars on Earth's oceans. The Moon plays no significant role in tidal forces.",
                "expected": "Bad answer has high word overlap but is factually WRONG.",
            },
        ]

        results = []
        for case in cases:
            bleu_good = self.compute_simple_bleu(case["reference"], case["good_answer"])
            bleu_bad = self.compute_simple_bleu(case["reference"], case["bad_answer"])
            rouge_good = self.compute_simple_rouge_l(case["reference"], case["good_answer"])
            rouge_bad = self.compute_simple_rouge_l(case["reference"], case["bad_answer"])

            results.append({
                "name": case["name"],
                "question": case["question"],
                "expected": case["expected"],
                "good_answer_bleu": bleu_good,
                "bad_answer_bleu": bleu_bad,
                "good_answer_rouge_l": rouge_good,
                "bad_answer_rouge_l": rouge_bad,
                "bleu_correct": bleu_good > bleu_bad,
                "rouge_correct": rouge_good > rouge_bad,
            })

        return results
