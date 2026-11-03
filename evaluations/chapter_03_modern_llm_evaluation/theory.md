# Chapter 3: Modern LLM Evaluation -- All 17 Dimensions

Modern LLM evaluation is **multi-dimensional**. No single metric captures output quality. Production systems combine heuristic baselines (this chapter) with LLM-as-Judge (Chapter 4) and human evaluation.

## Overview

```
  1. Correctness           10. Fluency
  2. Relevance             11. Coherence
  3. Helpfulness           12. Safety
  4. Completeness          13. Toxicity
  5. Consistency           14. Bias
  6. Hallucination         15. Creativity
  7. Faithfulness          16. Readability
  8. Groundedness          17. Reasoning Quality
  9. Instruction Following
```

### Note on Approach

These evaluators use **heuristic methods** (keyword matching, pattern detection, statistical measures) without external models. In production, most dimensions use **LLM-as-a-Judge** (Chapter 4). Heuristic methods serve as: (1) baselines, (2) fast pre-filters, (3) fallbacks when APIs are unavailable.

---

## Dimension 1: Correctness

**Measures:** Whether the model's answer is factually correct.
**Intuition:** Like grading a test -- compare the student's answer to the answer key.

**How it works:** Exact match for MCQ/classification; keyword overlap + cosine similarity for open-ended.

```
score = 0.4 * word_overlap + 0.3 * cosine_similarity + 0.3 * fact_coverage
```
- `word_overlap` = Jaccard similarity of tokenized reference and response
- `cosine_similarity` = cosine similarity of word frequency vectors
- `fact_coverage` = fraction of key facts found (a fact is found if >= 50% of its tokens appear)

**Pros/Cons:**
- + Simple, interpretable, no dependencies -- pure string comparison
- - Exact match too strict for open-ended; misses paraphrases and synonyms; cannot evaluate novel correct answers

**When NOT to use:** Creative writing or opinion questions where multiple answers are valid.

---

## Dimension 2: Relevance

**Measures:** Whether the response addresses the question that was actually asked.
**Intuition:** Like asking a waiter for the dessert menu and getting a wine list -- valid but not what you asked for.

**How it works:** Word overlap between question and answer (after removing stop words), checking if key question terms appear in the response.

```
score = 0.5 * question_coverage + 0.3 * cosine_similarity + 0.2 * bidirectional_overlap
```
- `question_coverage` = fraction of question's content words in response
- `cosine_similarity` = cosine similarity between question and response word vectors
- `bidirectional_overlap` = Jaccard similarity of content words

**Pros/Cons:**
- + Fast keyword check; catches completely off-topic responses; works without reference answers
- - Cannot detect semantic relevance; paraphrased questions may score low

**When NOT to use:** Tasks where the response should introduce new topics or creative brainstorming.

---

## Dimension 3: Helpfulness

**Measures:** Whether the response is actually useful to the person who asked.
**Intuition:** Like getting "go that way" vs turn-by-turn directions with landmarks.

**How it works:** Heuristic signals: sufficient length, explanatory markers ("because", "for example"), structure (lists, steps), specificity (numbers, proper nouns).

```
score = 0.25 * length_score + 0.30 * explanation_score + 0.20 * structure_score + 0.25 * specificity_score
```
- `length_score` = scaled by word count (< 5 = 0.1, < 20 = 0.3, < 50 = 0.6, < 150 = 0.9, >= 150 = 1.0)
- `explanation_score` = min(explanation_markers / 3, 1.0)
- `structure_score` = min(structure_markers / 2, 1.0)
- `specificity_score` = 0.5 * has_numbers + 0.5 * has_proper_nouns

**Pros/Cons:**
- + Captures surface signals; no reference answer needed; fast pre-filter
- - Length is a poor proxy; cannot measure if the user's actual need was met; inherently subjective

**When NOT to use:** When user feedback is available (use that instead), or tasks where brevity IS helpfulness.

---

## Dimension 4: Completeness

**Measures:** Whether the response covers ALL aspects of the question.
**Intuition:** Like ordering a combo meal and only getting the burger -- no fries or drink.

**How it works:** Extract key aspects from the question (AND/OR clauses, sub-questions), check each in the response, score by coverage ratio.

```
score = 0.6 * aspect_coverage + 0.4 * length_score
```
- `aspect_coverage` = fraction of required aspects covered (covered if >= 40% of its tokens appear)
- `length_score` = based on response-to-question length ratio (< 0.5x = 0.2, < 1x = 0.4, < 3x = 0.7, < 10x = 1.0, >= 10x = 0.9)

**Pros/Cons:**
- + Explicit aspect checking; catches partial answers to multi-part questions
- - Misses implicit sub-questions; cannot assess depth of coverage

**When NOT to use:** Simple factoid questions or tasks where partial answers are acceptable.

---

## Dimension 5: Consistency

**Measures:** Whether the model gives the same answer when asked the same question multiple times.
**Intuition:** Like asking a witness the same question three times -- if the story changes, trust drops.

**How it works:** Collect multiple responses, measure pairwise cosine similarity.

```
score = 0.7 * avg_pairwise_similarity + 0.3 * min_pairwise_similarity
```
Also checks numerical consistency (whether numbers agree across responses).

**Pros/Cons:**
- + Detects unreliable models; catches contradictory numbers
- - Consistent wrong answers still score high; some variation (paraphrasing) is healthy

**When NOT to use:** Creative tasks or brainstorming where varied responses are desired.

---

## Dimension 6: Hallucination Detection

**Measures:** Whether the model fabricated information not present in the source.
**Intuition:** Like a student making up quotes and attributing them to real authors.

**How it works:** Compare response claims against the source. Sentences with low overlap to source may be hallucinated. Also detects hallucination patterns (fabricated citations, statistics, attributions).

**Hallucination patterns detected:** fabricated study citations, researcher attributions, journal references, approximate statistics, discovery claims, institutional confirmations.

```
score = 1.0 - hallucination_rate
```
- `hallucination_rate` = hallucinated_sentences / total_sentences
- A sentence is hallucinated if: grounded_ratio < 0.3 OR hallucination patterns found that do not exist in source

**Pros/Cons:**
- + Catches fabricated statistics, dates, attributions; per-sentence pinpointing
- - Requires a reference source; word overlap misses paraphrased faithful content

**When NOT to use:** Open-ended creative tasks or tasks where the model should use its parametric knowledge.

---

## Dimension 7: Faithfulness

**Measures:** Whether the response accurately represents what the source material says.
**Intuition:** Like a journalist quoting a source -- faithful journalism vs distorted quotes.

**How it works:** Extract claims from response, check each against source at multiple granularity levels.

```
score = 0.3 * token_faithfulness + 0.3 * bigram_faithfulness + 0.4 * (faithful_sentences / total_sentences)
```
- `token_faithfulness` = fraction of response tokens in source
- `bigram_faithfulness` = fraction of response bigrams in source
- `faithful_sentences` = sentences with >= 40% token overlap with source

### Faithfulness vs Hallucination

```
Hallucination asks: "Did the model make things UP?"
Faithfulness  asks: "Did the model stay TRUE to the source?"
```
Both measure source fidelity, but from different angles.

**Pros/Cons:**
- + Multi-granularity scoring (token, bigram, sentence); essential for RAG
- - Cannot detect subtle distortions ("may" -> "definitely"); paraphrased content may score low

**When NOT to use:** Tasks where the model should use its own knowledge or open-domain QA without context.

---

## Dimension 8: Groundedness

**Measures:** Whether every claim in the response can be traced back to the provided context.
**Intuition:** Like a lawyer who can only cite evidence admitted to court.

**How it works:** Split response into claims/sentences. For each, find best-matching context sentence by cosine similarity. A claim is grounded if best match >= 0.3.

```
score = 0.6 * groundedness_ratio + 0.4 * token_grounding
```
- `groundedness_ratio` = grounded_claims / total_claims
- `token_grounding` = fraction of response tokens found in context

### Groundedness vs Faithfulness vs Hallucination

```
Groundedness  : Can every claim be TRACED to the context?  (strictest)
Faithfulness  : Does the response REPRESENT the context accurately?
Hallucination : Did the response ADD things NOT in the context?
```
Groundedness is the strictest: every sentence must have a clear source.

**Pros/Cons:**
- + Strictest source-fidelity check; claim-level pinpointing; essential for high-stakes RAG
- - Cannot detect valid inferences; too strict for responses that add common knowledge

**When NOT to use:** Open-domain generation or tasks where adding external knowledge is expected.

---

## Dimension 9: Instruction Following

**Measures:** Whether the model followed the specific instructions given.
**Intuition:** Like a contractor who builds a beautiful kitchen when you asked for a bathroom.

**How it works:** Check for common instruction patterns: length constraints ("in one sentence"), format constraints ("as JSON", "as a list"), style constraints ("simple language"), content constraints.

```
score = constraints_passed / constraints_checked
```
If no specific constraints detected, neutral score of 0.5.

**Pros/Cons:**
- + Checks verifiable constraints (length, format, bullet points); works for structured output
- - Can only check detectable patterns; cannot verify semantic compliance ("be creative")

**When NOT to use:** Open-ended conversations without specific instructions.

---

## Dimension 10: Fluency

**Measures:** Whether the language is natural, grammatical, and easy to read.
**Intuition:** Like listening to someone speak -- broken grammar reduces trust.

**How it works:** Heuristic signals: proper capitalization, no excessive repetition, reasonable sentence length, proper punctuation, no garbled/malformed text.

```
score = 0.25 * capitalization + 0.20 * repetition + 0.20 * sentence_length + 0.20 * punctuation + 0.15 * garbled_text
```

**Pros/Cons:**
- + Catches basic fluency issues; no external model needed; fast pre-filter
- - Cannot detect subtle grammar errors; non-English text may score incorrectly

**When NOT to use:** Evaluating code/structured data, or when you have a grammar checker or LLM judge.

---

## Dimension 11: Coherence

**Measures:** Whether the response flows logically from start to finish.
**Intuition:** Like chapters in a book -- each can be well-written, but if unrelated, the book fails.

**How it works:** Topic continuity between consecutive sentences (adjacent cosine similarity), discourse markers ("however", "therefore"), consistent topic thread, abrupt shift detection.

```
score = 0.35 * min(avg_adjacent_similarity * 2, 1.0)
      + 0.25 * marker_score
      + 0.15 * min(first_last_similarity * 2, 1.0)
      + 0.25 * shift_score
```
- `marker_score` = based on discourse marker density (ideal: 0.3-0.8 per sentence)
- `shift_score` = max(1.0 - shift_ratio * 2, 0.0)

**Pros/Cons:**
- + Detects topic shifts; discourse marker analysis reveals structure quality
- - Cannot detect logical contradictions; some responses legitimately cover multiple topics

**When NOT to use:** Multi-topic responses where topic shifts are expected, or very short (one sentence) responses.

---

## Dimension 12: Safety

**Measures:** Whether the response is free from dangerous or harmful content.
**Intuition:** Like a pharmacist who will not explain how to make drugs from prescriptions.

**How it works:** Keyword/pattern detection across categories: dangerous instructions, harmful substances, violence, self-harm, illegal activity.

```
score = max(1.0 - total_flags * 0.2, 0.0)
```

**Pros/Cons:**
- + Catches explicit dangerous content; category-level reporting; fast pre-filter
- - Many false positives; sophisticated content evades detection; cannot distinguish educational from harmful

**When NOT to use:** Medical/legal/security contexts where flagged terms are normal, or when you have a dedicated safety model.

---

## Dimension 13: Toxicity

**Measures:** Whether the response contains toxic, hateful, or offensive language.
**Intuition:** Like a content moderator reviewing posts for hostile language.

**How it works:** Pattern matching: profanity, threatening language, demeaning language, hate speech indicators.

```
toxicity_score = min(total_flags * 0.25, 1.0)    # 0 = not toxic, 1 = very toxic
safety_score   = 1.0 - toxicity_score              # Inverted: 1 = safe
```

**Pros/Cons:**
- + Catches explicit insults, threats, hate speech; category breakdown aids analysis
- - Keyword lists always incomplete; context determines toxicity; cannot detect coded language

**When NOT to use:** Content moderation research (need Perspective API), or when context makes terms appropriate.

---

## Dimension 14: Bias

**Measures:** Whether the response shows unfair bias (gender, racial, cultural, elitism).
**Intuition:** Like a hiring manager who unconsciously favors certain university graduates.

**How it works:** Check for gender-skewed language, stereotypical associations, exclusionary language, balanced representation, elitism, and inclusivity markers.

```
score = 0.30 * gender_balance + 0.30 * stereotype_score + 0.20 * inclusivity + 0.20 * elitism_score
```
- `gender_balance` = min(male, female) / max(male, female); 1.0 if no gendered language
- `stereotype_score` = max(1.0 - stereotypes * 0.3, 0.0)
- `inclusivity` = min(inclusive_markers / 3, 1.0)
- `elitism_score` = max(1.0 - elitism_flags * 0.25, 0.0)

**Pros/Cons:**
- + Detects gender-skewed language, stereotypes, elitism
- - Cannot measure implicit bias; context matters; "balanced" is not always "50/50"

**When NOT to use:** Historical content, discussions about specific individuals, or topics inherently about specific groups.

---

## Dimension 15: Creativity

**Measures:** Whether the response uses creative elements where appropriate.
**Intuition:** Like the difference between a dry lecture and a TED talk with stories and analogies.

**How it works:** Heuristic signals: analogy/metaphor usage, vocabulary richness (type-token ratio), sentence structure variety, storytelling elements, vocabulary sophistication (avg word length).

```
score = 0.30 * analogy + 0.20 * vocab_richness + 0.15 * sentence_variety + 0.20 * storytelling + 0.15 * sophistication
```

**Pros/Cons:**
- + Detects analogies, storytelling, lexical diversity
- - Cannot judge quality of creativity; inherently subjective

**When NOT to use:** Factual Q&A, technical documentation, legal or medical content.

---

## Dimension 16: Readability

**Measures:** How easy the response is to understand for the target audience.
**Intuition:** Like the difference between a research paper and a Wikipedia article.

**How it works:** Flesch-Kincaid readability metrics.

**Flesch Reading Ease:** `FRE = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)` (higher = easier, target 60-70)

**Flesch-Kincaid Grade:** `FK = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59`

| Grade | Level |
|-------|-------|
| <= 5 | Elementary |
| 6-8 | Middle School |
| 9-12 | High School |
| 13-16 | College |
| > 16 | Graduate |

Also measures complex word ratio (3+ syllables) and average words per sentence.

**Pros/Cons:**
- + Established formulas; grade-level interpretation; objective and reproducible
- - Crude approximation; cannot assess conceptual difficulty

**When NOT to use:** Technical writing for domain experts where jargon is required.

---

## Dimension 17: Reasoning Quality

**Measures:** Whether the response demonstrates sound logical reasoning.
**Intuition:** Like a math teacher checking the work, not just the answer.

**How it works:**

*Reasoning indicators:* causal connectives ("because", "therefore"), evidence presentation ("studies show", "data suggests"), counter-argument acknowledgment ("however", "although").

*Reasoning anti-patterns:* circular reasoning, appeal to common sense ("obviously"), absolute claims ("always/never").

```
raw = 0.25 * causal + 0.20 * evidence + 0.15 * counter_argument + 0.20 * depth + 0.20 * structure
score = max(raw - antipattern_penalty, 0.0)
```
- `depth` = based on chain_length (>= 4 = 1.0, >= 2 = 0.7, >= 1 = 0.4, 0 = 0.1)
- `structure` = 0.5 * has_premise + 0.5 * has_conclusion
- `antipattern_penalty` = antipatterns * 0.2

**Pros/Cons:**
- + Detects causal reasoning, evidence, counter-arguments; catches anti-patterns
- - Cannot verify logical validity; reasoning words do not guarantee good reasoning

**When NOT to use:** Simple factoid answers or creative writing where logic is not the point.

---

## Multi-Dimension Evaluation

The `MultiDimensionEvaluator` runs all 17 dimensions on a single question + response pair and supports **head-to-head comparison** (winner = response winning more dimensions, threshold > 0.05).

### Conditional Dimensions

- **Always evaluated** (question + response only): Relevance, Helpfulness, Completeness, Fluency, Coherence, Safety, Toxicity, Bias, Creativity, Readability, Reasoning
- **Requires reference answer**: Correctness
- **Requires context/source**: Hallucination, Faithfulness, Groundedness
- **Requires instruction**: Instruction Following
- **Requires multiple responses**: Consistency

---

## Summary Table

```
  #   Dimension                Core Question                          Heuristic Method
  --- ---                      ---                                    ---
   1  Correctness              Is the answer right?                   MCQ exact-match / keyword overlap
   2  Relevance                Does it answer the question asked?     Keyword + cosine similarity
   3  Helpfulness              Is it useful to the user?              Length + explanations + structure
   4  Completeness             Does it cover all aspects?             Aspect coverage + length ratio
   5  Consistency              Same answer each time?                 Pairwise cosine similarity
   6  Hallucination            Did it make things up?                 Source overlap + pattern matching
   7  Faithfulness             True to the source?                    Token/bigram/sentence overlap
   8  Groundedness             Every claim traceable?                 Claim-to-context matching
   9  Instruction Following    Did it follow instructions?            Constraint pattern detection
  10  Fluency                  Natural language?                      Capitalization + repetition + punctuation
  11  Coherence                Logical flow?                          Adjacent similarity + discourse markers
  12  Safety                   Free from harm?                        Keyword category matching
  13  Toxicity                 Free from toxic language?              Pattern-based toxicity flags
  14  Bias                     Fair and unbiased?                     Gender balance + stereotype detection
  15  Creativity               Uses creative elements?                Analogy/metaphor + vocab richness
  16  Readability              Easy to understand?                    Flesch-Kincaid readability metrics
  17  Reasoning Quality        Sound logical reasoning?               Causal markers + evidence + structure
```

---

## Interview Questions

**Q1: What is the difference between hallucination, faithfulness, and groundedness?**
Hallucination = "did the model invent facts?". Faithfulness = "does the response accurately represent the source?". Groundedness = "can every claim be traced to context?" (strictest).

**Q2: Why is correctness not sufficient as the only evaluation dimension?**
A response can be correct but unhelpful, irrelevant, incomplete, biased, unsafe, or poorly written. LLMs serve open-ended tasks where quality is multi-faceted.

**Q3: How would you evaluate an LLM in a RAG pipeline?**
Faithfulness, groundedness, hallucination detection, relevance, and completeness. LLM-as-Judge (Chapter 4) is typically used for these.

**Q4: Limitations of heuristic evaluation vs LLM-as-Judge?**
Heuristics are fast and reproducible but shallow (miss paraphrases, semantics). LLM-as-Judge handles semantics but is expensive, potentially biased, less reproducible. Best approach combines both.

**Q5: How do you evaluate LLM safety beyond keyword matching?**
Dedicated safety classifiers (LlamaGuard), red-teaming, LLM-as-Judge with safety rubrics, human evaluation with content policies, multi-turn jailbreak testing.

**Q6: Difference between fluency and coherence?**
Fluency = individual sentences are grammatical. Coherence = the response flows logically as a whole. Fluent sentences can be incoherent together.

**Q7: How would you detect bias in LLM outputs at scale?**
Counterfactual testing (swap demographics), representation audits, stereotype association tests, disaggregated evaluation, diverse annotator pools.

**Q8: When should you NOT use creativity as an evaluation dimension?**
Factual Q&A, technical docs, legal/medical content -- anywhere accuracy matters more than creative expression.

**Q9: How do Flesch-Kincaid scores work and what are their limitations?**
Uses avg words/sentence and avg syllables/word to estimate difficulty. FRE 0-100 (higher = easier). Limitation: only surface features, not conceptual difficulty.

**Q10: Design an evaluation pipeline for a customer-support chatbot.**
Priority: (1) Safety/Toxicity, (2) Correctness, (3) Relevance, (4) Helpfulness, (5) Instruction Following, (6) Readability, (7) Consistency. Use heuristics for pre-filtering, LLM-as-Judge for depth, human review for edge cases.

---

## Common Mistakes

1. **Relying on a single dimension**: Correctness alone misses helpfulness, safety, and bias.
2. **Treating heuristic scores as ground truth**: These are approximations.
3. **Ignoring context**: Same word can be safe in one context and harmful in another.
4. **Over-weighting length**: Longer is not always better.
5. **Applying creativity metrics to factual tasks**: Analogies can introduce inaccuracy.
6. **Using exact match for open-ended evaluation**: Too strict, misses correct paraphrases.
7. **Evaluating consistency without checking correctness**: Consistently wrong still scores high.
8. **Applying groundedness to open-domain tasks**: Only meaningful with specific context.

---

## Best Practices

1. **Use multiple dimensions** -- at least 5-7 relevant ones for holistic assessment.
2. **Weight dimensions by task** -- Safety for chatbots; faithfulness for RAG.
3. **Use heuristics as pre-filters** before expensive LLM-as-Judge.
4. **Calibrate thresholds** per application and domain.
5. **Include positive and negative examples** to validate evaluators.
6. **Combine with LLM-as-Judge** -- heuristics for surface, LLM for semantics.
7. **Track dimension-level scores** -- the worst dimension reveals the most important issue.
8. **Version your evaluation pipeline** as your application evolves.

---

## Key Takeaways

- Modern LLM evaluation is **multi-dimensional** -- no single metric captures quality.
- The 17 dimensions group into: **Accuracy** (Correctness, Hallucination, Faithfulness, Groundedness), **Relevance & Usefulness** (Relevance, Helpfulness, Completeness), **Reliability** (Consistency, Instruction Following), **Language Quality** (Fluency, Coherence, Readability), **Safety & Ethics** (Safety, Toxicity, Bias), **Advanced** (Creativity, Reasoning).
- Heuristic methods are fast and interpretable but shallow.
- Production systems combine heuristics + LLM-as-Judge + human evaluation.
- Which dimensions to evaluate depends on the specific application.
