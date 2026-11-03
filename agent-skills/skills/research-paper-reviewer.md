---
name: research-paper-reviewer
description: >
  Use this skill whenever the user asks to review, analyze, or evaluate a research paper in Markdown format. 
  Trigger for requests like "review this paper", "analyze the methodology", "evaluate the novelty", 
  "summarize the findings", or "provide feedback on this research". 
  This skill validates that the input is Markdown format (rejects PDFs), then performs a comprehensive 
  12-step analysis producing a structured 15-section review covering methodology, novelty, strengths, 
  weaknesses, technical assessment, and recommendations.
---

# Research Paper Reviewer Skill

## Purpose
Analyze and review academic/research papers provided in Markdown format, extracting key information, evaluating methodology, assessing novelty, and providing structured feedback on strengths, weaknesses, and recommendations.

## When to Use This Skill
Use this skill when:
- You need to quickly understand a research paper
- You want to assess the novelty and quality of research
- You need to extract technical details (methodology, datasets, metrics)
- You want to evaluate a paper for relevance to your work
- You need to identify potential applications or improvements
- You're conducting literature review

Do NOT use this skill for:
- Non-research documents (blog posts, news articles)
- Papers in PDF format (request markdown version instead)
- Documents without structured content
- Non-academic writing

## Expected Input Format

**Input Type:** Markdown file (.md) containing the research paper content

**Required:**
- Paper text in markdown format
- At minimum: abstract or summary section
- Preferably: methodology, results, conclusion sections

**Example valid inputs:**
- Research paper exported to markdown
- ArXiv paper converted to markdown
- Conference paper in markdown format
- Technical report in markdown

**Invalid inputs:**
- PDF files (request conversion to markdown)
- Blog posts or news articles
- Incomplete fragments
- Non-English papers (unless explicitly stated)

## Workflow Steps

### Step 0: Algorithm Identification & Preparation (NEW in v1.1)
- Scan the paper for all algorithms, techniques, and methods mentioned
- Create a list of algorithms to explain
- Identify which are core contributions vs supporting techniques
- Prioritize algorithms by importance and complexity
- Prepare to explain each in simple terms with examples

### Step 1: Input Validation
- Check if input is markdown format (.md file)
- If PDF or binary format detected:
  - **Stop execution**
  - **Ask user:** "I can only review research papers in Markdown format. Could you please share the paper as a .md file? You can copy-paste the content or export it from your PDF reader."
  - Provide guidance on how to convert PDF to markdown if helpful
- Verify content appears to be a research paper (contains academic structure)
- Check for minimum viable content (at least abstract + some sections)

### Step 2: Paper Structure Analysis
Identify and extract:
1. **Title** - Paper title
2. **Abstract** - Summary of the work
3. **Introduction** - Problem statement and context
4. **Methodology/Method** - Research approach and techniques
5. **Experiments/Results** - Data, experiments, findings
6. **Related Work** - Comparison with prior research
7. **Conclusion** - Summary and impact
8. **References** - Citations

### Step 3: Technical Content Extraction
Extract and analyze:
- **Problem Statement** - What problem does it solve?
- **Dataset(s) Used** - Names, sizes, characteristics
- **Models/Algorithms** - Techniques employed
- **Metrics** - Evaluation metrics used
- **Baselines** - What methods does it compare against?
- **Key Results** - Main findings and numbers
- **Hyperparameters** - Important configuration details (if mentioned)

### Step 3.5: Algorithm Explanation (NEW in v1.1)
For each key algorithm identified:

**A. Simple Concept Explanation**
- Explain what the algorithm does in one sentence
- Use everyday language (avoid jargon)
- Use analogies to common real-world scenarios
- Example: "Genetic algorithm is like breeding - keep the best, combine them, add random changes"

**B. Why Use This Algorithm**
- What problem does it solve?
- Why is this approach better than alternatives?
- When would you NOT use this algorithm?
- Example: "Genetic algorithms are good for exploring large spaces where finding the perfect answer is hard"

**C. Step-by-Step Example Walkthrough**
- Take a small, concrete example
- Show each step of the algorithm
- Use numbers/values that are easy to follow
- Show intermediate results
- Example walkthrough with actual numbers

**D. Visual Representation**
- Create ASCII diagram or describe flow
- Show inputs and outputs
- Illustrate the transformation at each step
- Example: Show how documents change through mutations

**E. Simple Pseudocode**
- Write algorithm in plain pseudocode
- Not language-specific
- Easy to understand logic
- Show key operations

**F. Real-World Analogy**
- Compare to something familiar
- Help reader build intuition
- Explain why the analogy works
- Explain where analogy breaks down

**G. Common Questions About Algorithm**
- "How does it know when to stop?"
- "What if it gets stuck?"
- "How fast is it?"
- "Why use this instead of [simpler method]?"

### Step 4: Novelty Assessment
Evaluate:
- **Conceptual Novelty** - New ideas or approaches?
- **Technical Novelty** - New methods or algorithms?
- **Application Novelty** - New application domain?
- **Comparison to Related Work** - How does it advance the field?
- **Significance** - Potential impact on the field?

### Step 5: Methodology Evaluation
Assess:
- **Research Design** - Is the approach sound?
- **Experimental Design** - Are experiments well-designed?
- **Data Quality** - Is data appropriate for the claims?
- **Baselines** - Are comparisons fair and comprehensive?
- **Statistical Rigor** - Confidence intervals, significance testing?
- **Reproducibility** - Enough detail to reproduce results?

### Step 6: Strengths Identification
Identify:
- Clear and compelling contributions
- Solid experimental methodology
- Strong empirical results
- Good writing and presentation
- Novel insights or perspectives
- Practical applicability
- Thorough literature review

### Step 7: Weaknesses Identification
Identify:
- Limited scope or generalizability
- Unfair or incomplete baselines
- Missing ablation studies
- Overclaimed results
- Methodology issues
- Writing clarity problems
- Limited discussion of limitations
- Potential data leakage or bias

### Step 8: Logical Consistency Check
- Verify claims are supported by results
- Check for unsupported assertions
- Identify contradictions
- Validate reasoning chain
- Flag overclaimed conclusions

### Step 9: Citation and Reference Quality
Assess:
- Appropriate citations of prior work
- Missing important related work?
- Citation accuracy
- Balance of recent vs foundational work
- Any suspicious patterns in citations

### Step 10: Practical Value Assessment
Consider:
- Can this work be applied to real problems?
- What are implementation challenges?
- What are computational/resource requirements?
- Would this advance your specific area?
- Are there obvious next steps?

### Step 11: Structured Report Generation
Compile findings into sections (see Output Format below)

### Step 12: Recommendations and Next Steps
- What could improve the work?
- What questions remain unanswered?
- What are logical next experiments?
- How could this be extended?
- Are there potential applications?

## Tools to Use

**For Basic Review (v1.0):**
- None required - Pure reasoning and analysis

**For Algorithm Explanation (v1.1 NEW):**
- **Python** (optional) - For running algorithm examples with actual numbers
- **Visual ASCII diagrams** - To show algorithm flow (text-based)
- **Web search** (optional) - For external algorithm resources/references
- **Code examples** (optional) - To show pseudocode or actual implementations

**For Enhancement:**
- Web search for cited methods or datasets
- SQL/database queries if comparing with known benchmarks
- Python for analyzing reported metrics or running examples

## Rules and Constraints

### Must Follow
1. **Only review markdown files** - Reject PDFs immediately with user guidance
2. **Be honest and balanced** - Acknowledge both strengths and weaknesses
3. **Support claims with evidence** - Reference specific parts of the paper
4. **Avoid personal bias** - Judge by scientific merit, not author reputation
5. **Respect complexity** - Understand the context and domain
6. **Be constructive** - Provide actionable feedback

### Should Avoid
1. ❌ Don't assume you know the paper without reading carefully
2. ❌ Don't compare against unstated benchmarks
3. ❌ Don't judge harshly without understanding the research domain
4. ❌ Don't make claims about AI detection in paper authorship (note: this is not reliable)
5. ❌ Don't provide generic feedback - be specific
6. ❌ Don't ignore context or constraints the authors faced
7. ❌ Don't leak sensitive information if paper is pre-print/confidential

## Output Format

Return a structured review with these sections:

### 1. Overview
```
Title: [Paper title]
Research Area: [Domain/field]
Type: [Conference paper/Journal/Preprint/etc]
Confidence in Review: [High/Medium/Low] - based on your familiarity with the domain
```

### 2. Summary (1 paragraph)
Brief, clear summary of what the paper does and its main contribution

### 3. Strengths (Bullet points)
- ✅ [Specific strength with evidence]
- ✅ [Specific strength with evidence]
- ✅ [Specific strength with evidence]

### 4. Weaknesses (Bullet points)
- ⚠️ [Specific weakness with evidence]
- ⚠️ [Specific weakness with evidence]
- ⚠️ [Specific weakness with evidence]

### 5. Technical Assessment
| Aspect | Rating | Comment |
|--------|--------|---------|
| Novelty | High/Medium/Low | [Specific comment] |
| Methodology | High/Medium/Low | [Specific comment] |
| Experimental Design | High/Medium/Low | [Specific comment] |
| Results Validity | High/Medium/Low | [Specific comment] |
| Reproducibility | High/Medium/Low | [Specific comment] |
| Writing Quality | High/Medium/Low | [Specific comment] |
| Practical Impact | High/Medium/Low | [Specific comment] |

### 5.5. Algorithm Explanations (NEW in v1.1)

For each key algorithm in the paper, provide:

#### Algorithm Name
**[Algorithm Name]**

**A. What Does It Do? (Simple Explanation)**
- One-sentence explanation in plain English
- No jargon or technical terms
- Focus on the goal, not the mechanics

**B. Why Use This Algorithm?**
- Problem it solves
- Advantages over alternatives
- When to use it / when NOT to use it

**C. Real-World Analogy**
- Compare to something familiar
- Explain why the analogy works
- Show where analogy breaks down

**D. Step-by-Step Example Walkthrough**
```
Starting Input: [concrete example with actual numbers]

Step 1: [What happens]
  Input: [numbers]
  Action: [explain in simple words]
  Output: [numbers]

Step 2: [What happens]
  Input: [numbers from step 1]
  Action: [explain in simple words]
  Output: [numbers]

Step N: [Final step]
  Input: [numbers]
  Output: [final result]
```

**E. Visual Flow Diagram**
```
[ASCII diagram showing algorithm flow]
Input → Processing → Output
```

**F. Simple Pseudocode**
```
Algorithm: [Name]
Input: [what goes in]
Output: [what comes out]

Steps:
1. [Do this]
2. [Do this]
3. [Do this]
...repeat if needed...
Return [the answer]
```

**G. Common Questions About This Algorithm**
- Q: How does it know when to stop?
  A: [plain English explanation]
- Q: What if [common concern]?
  A: [how algorithm handles it]
- Q: Why [algorithm choice]?
  A: [justification]

---

### 6. Key Findings
- Dataset(s): [Names and size if available]
- Models/Methods: [Key techniques]
- Main Results: [Key metrics and performance]
- Baselines: [What it compares against]

### 7. Logical Consistency
- ✅ Claims well-supported by results?
- ⚠️ Any unsupported assertions?
- ⚠️ Any contradictions?
- 🔍 Level of overclaiming (if any)?

### 8. Related Work Assessment
- Comprehensiveness: [Good/Adequate/Lacking]
- Fairness to prior work: [Fair/Somewhat fair/Unfair]
- Missing important references: [List if any]

### 9. Novelty Assessment
**Conceptual:** [Novel/Somewhat novel/Incremental]
**Technical:** [Novel/Somewhat novel/Incremental]
**Application:** [Novel/Somewhat novel/Incremental]
**Overall Impact:** [High/Medium/Low]

### 10. Questions and Concerns
- [Specific question about methodology/results]
- [Specific concern about claims]
- [Specific ambiguity that needs clarification]

### 11. Recommendations for Improvement
1. [Specific, actionable improvement]
2. [Specific, actionable improvement]
3. [Specific, actionable improvement]

### 12. Suggested Next Steps/Extensions
- What experiments would strengthen the work?
- What are logical follow-up studies?
- How could this be extended or applied?
- What questions remain unanswered?

### 13. Potential Applications
- Where could this be practically applied?
- What problems could it solve?
- What industries/domains could benefit?
- What are implementation considerations?

### 14. Overall Assessment
**Rating:** [Score: e.g., 7/10]
**Recommendation:** [Accept/Borderline/Reject/Strong Accept] - with brief justification

### 15. Personal Insights
- What did you find most interesting?
- What surprised you?
- How does this relate to current trends in the field?
- Would you recommend this paper to others? Why?

## Error Handling

### Error: PDF or Binary File Detected
**Response:**
```
❌ PDF Format Detected

I can only review research papers in Markdown format (.md files).

Could you please share the paper in one of these formats:
1. Copy-paste the text as markdown
2. Export the PDF content to markdown
3. Use a PDF-to-markdown converter
4. Share a pre-existing markdown version

Once you have the markdown file, you can share it and I'll review it!
```

### Error: Non-Academic Content
**Response:**
```
⚠️ Content Analysis

This doesn't appear to be a research paper. It looks like [blog post/news article/etc].

I'm designed to review academic research papers. Please share:
- A peer-reviewed research paper
- A conference paper
- An academic preprint
- A technical research report

If you have a research paper in markdown format, I'm ready to review it!
```

### Error: Insufficient Content
**Response:**
```
⚠️ Insufficient Content

The provided content is too brief for a comprehensive review. 

I need at least:
- A title or heading
- An abstract or introduction
- Methodology or methods section
- Some results or findings
- Conclusion

Please provide the complete paper or a more complete excerpt.
```

### Error: Unclear Structure
**Response:**
```
⚠️ Structure Unclear

I'm having difficulty identifying the paper's structure. This could mean:
1. The content is fragmented
2. The markdown formatting is missing
3. It's not a research paper

Please ensure you're sharing:
- A complete research paper
- In markdown format
- With clear sections (title, abstract, introduction, etc.)
```

## Example Usage

**User Input:**
```
Please review this research paper:

[...markdown content of the paper...]
```

**Skill Execution:**
1. Validate markdown format ✅
2. Identify paper structure
3. Extract key information
4. Analyze novelty and methodology
5. Assess strengths and weaknesses
6. Generate structured review

**Output:** Detailed structured review following the Output Format above

## Success Criteria

This skill is working well when:
- ✅ Reviews are completed in reasonable time
- ✅ Feedback is specific and actionable
- ✅ Both strengths and weaknesses are identified
- ✅ Claims reference specific parts of the paper
- ✅ Recommendations are constructive
- ✅ Review helps the user understand the paper better
- ✅ PDF inputs are properly rejected with guidance

## Limitations

- Works best with well-structured papers
- Requires papers in markdown format
- Cannot verify claims against external benchmarks without web search
- May miss domain-specific nuances for unfamiliar fields
- Cannot detect AI-generated content with certainty (note: AI detection has high false positive rate)
- Works best with papers in English or translated content

## Model Recommendation

- **Recommended:** Claude Opus or Claude Sonnet (requires deep reasoning and critical analysis)
- **Fallback:** Claude Haiku (for quick summaries only, may miss nuances)

## Version History & Changelog

### v1.1 (2026-08-03) - Algorithm Explanation Enhancement

**Release Type:** Minor Version Update
**Status:** ✅ ACTIVE & RECOMMENDED
**Backward Compatible:** ✅ YES (100% compatible with v1.0)
**Breaking Changes:** ❌ NONE

#### New in v1.1

**New Workflow Steps:**
- **Step 0: Algorithm Identification & Preparation** (NEW)
  - Scans paper for all algorithms, techniques, methods
  - Creates comprehensive list of algorithms
  - Identifies core contributions vs supporting techniques
  - Prioritizes by importance and complexity
  - Prepares detailed explanations for each

- **Step 3.5: Algorithm Explanation** (NEW)
  - Comprehensive 7-part algorithm breakdown per algorithm
  - Part A: Simple Concept Explanation (plain English, no jargon)
  - Part B: Why Use This Algorithm (problem & advantages)
  - Part C: Real-World Analogy (familiar comparison)
  - Part D: Step-by-Step Example Walkthrough (with actual numbers)
  - Part E: Visual Flow Diagram (ASCII representation)
  - Part F: Simple Pseudocode (logic-focused, language-agnostic)
  - Part G: Common Questions About Algorithm (Q&A format)

**New Output Section:**
- **Section 5.5: Algorithm Explanations** (NEW)
  - Added between Technical Assessment and Key Findings
  - One comprehensive entry per algorithm in paper
  - All 7-part structure applied to each algorithm
  - Examples with actual numerical values
  - Visual diagrams showing data flow and transformation

**Enhanced Tools Support:**
- **Python** (optional) - For running algorithm examples with real data
- **ASCII diagrams** - For visualizing algorithm flow
- **Web search** (optional) - For external algorithm references
- **Code examples** (optional) - For pseudocode implementation

**Documentation Updates:**
- Updated tools section with new capabilities
- Enhanced version history (this section)
- Complete upgrade guide: `docs/09-skill-upgrade-v1.1.md`

#### v1.1 Feature Matrix

| Category | Feature | Status |
|----------|---------|--------|
| **Core Review** | Paper analysis | ✅ Unchanged |
| | Structure analysis | ✅ Unchanged |
| | Content extraction | ✅ Unchanged |
| | Novelty assessment | ✅ Unchanged |
| | Methodology review | ✅ Unchanged |
| **Strengths & Weaknesses** | Identification | ✅ Unchanged |
| | Evidence gathering | ✅ Unchanged |
| **Algorithm Features** | Identification | 🔵 Enhanced |
| | Simple explanation | ✅ NEW |
| | Real-world analogy | ✅ NEW |
| | Step-by-step example | ✅ NEW |
| | Visual diagram | ✅ NEW |
| | Pseudocode | ✅ NEW |
| | Common Q&A | ✅ NEW |
| **Output Format** | Sections 1-5 | ✅ Unchanged |
| | Section 5.5 | ✅ NEW |
| | Sections 6-15 | ✅ Unchanged |
| **Error Handling** | PDF rejection | ✅ Unchanged |
| | Invalid content | ✅ Unchanged |
| | Input validation | ✅ Unchanged |

#### v1.1 vs v1.0 Comparison

**Workflow Changes:**
```
v1.0: 12 steps total
v1.1: 13 steps total (+1 Step 0)
      + 1 new algorithm step (Step 3.5)
```

**Output Changes:**
```
v1.0: 15 output sections
v1.1: 16 output sections (+Section 5.5)
```

**Algorithm Handling:**
```
v1.0: Basic identification only
v1.1: Comprehensive 7-part explanation per algorithm
```

**Files Modified for v1.1:**
- `C:\Users\prasad_ovhal\.claude\skills\research-paper-reviewer\SKILL.md`
- `D:\Study\Git_repo\agent-skills\skills\research-paper-reviewer.md` (this file)

**Upgrade Instructions:**
- No action needed
- Automatic upgrade available
- Can use v1.0 and v1.1 simultaneously
- No breaking changes

---

### v1.0 (2026-08-03) - Initial Release

**Release Type:** Initial Release
**Status:** ✅ ACTIVE (Stable & Supported)
**Backward Compatible:** N/A (First version)
**Breaking Changes:** N/A

#### Features in v1.0

**Workflow (12 Steps):**
1. Input Validation - Markdown format checking
2. Paper Structure Analysis - Title, abstract, sections
3. Technical Content Extraction - Datasets, models, metrics
4. Novelty Assessment - Conceptual/technical/application novelty
5. Methodology Evaluation - Research design quality
6. Strengths Identification - Strong points with evidence
7. Weaknesses Identification - Issues and limitations
8. Logical Consistency Check - Claims validation
9. Citation Quality Assessment - Reference quality
10. Practical Value Assessment - Real-world applicability
11. Structured Report Generation - Output compilation
12. Recommendations & Next Steps - Future work suggestions

**Output Format (15 Sections):**
1. Overview - Metadata (title, area, type, confidence)
2. Summary - 1-paragraph summary
3. Strengths - Bulleted list with evidence
4. Weaknesses - Bulleted list with evidence
5. Technical Assessment - Table with ratings
6. Key Findings - Datasets, models, results, baselines
7. Logical Consistency - Claims analysis
8. Related Work Assessment - Literature review quality
9. Novelty Assessment - Novelty levels and impact
10. Questions and Concerns - Open issues
11. Recommendations - Actionable improvements
12. Suggested Extensions - Future work
13. Potential Applications - Practical uses
14. Overall Assessment - Rating (0-10) and recommendation
15. Personal Insights - Subjective observations

**Core Capabilities:**
- ✅ Markdown file validation
- ✅ Academic paper format recognition
- ✅ PDF rejection with user guidance
- ✅ Paper structure analysis
- ✅ Technical content extraction
- ✅ Methodology evaluation
- ✅ Quality assessment
- ✅ Strength/weakness identification
- ✅ Comprehensive structured output
- ✅ Error handling and validation

**Error Handling (4 Types):**
- PDF/Binary format detection
- Non-academic content detection
- Insufficient content detection
- Unclear structure detection
- User guidance provided for each error

**Input Requirements:**
- Markdown format (.md files only)
- Academic structure (title, abstract, sections)
- Minimum content: abstract + at least 3 main sections
- Preferably: introduction, methodology, results, conclusion

**Model Recommendations:**
- Recommended: Claude Opus or Claude Sonnet
- Fallback: Claude Haiku (summaries only, may miss nuances)

**Limitations:**
- Works best with well-structured papers
- Requires markdown format (not PDF)
- Cannot verify claims without web search
- May miss domain-specific nuances for unfamiliar fields
- Cannot reliably detect AI-generated content
- Best with English or translated content

#### v1.0 Feature Matrix

| Feature | Included | Details |
|---------|----------|---------|
| Paper validation | ✅ | Markdown only |
| Structure analysis | ✅ | Comprehensive |
| Content extraction | ✅ | Technical details |
| Novelty assessment | ✅ | 3-level scoring |
| Methodology review | ✅ | Detailed evaluation |
| Strengths/Weaknesses | ✅ | With evidence |
| Structured output | ✅ | 15 sections |
| Recommendations | ✅ | Actionable items |
| Error handling | ✅ | 4 error types |
| Algorithm explanation | ❌ | Added in v1.1 |
| Step-by-step examples | ❌ | Added in v1.1 |
| Real-world analogies | ❌ | Added in v1.1 |
| Visual diagrams | ❌ | Added in v1.1 |

---

## Version Comparison Matrix

| Aspect | v1.0 | v1.1 | Change |
|--------|------|------|--------|
| **Release Date** | 2026-08-03 | 2026-08-03 | Same day release |
| **Workflow Steps** | 12 | 13 | +1 algorithm identification |
| **Output Sections** | 15 | 16 | +1 algorithm explanations |
| **Paper Analysis** | ✅ | ✅ | Unchanged |
| **Methodology Review** | ✅ | ✅ | Unchanged |
| **Algorithm Explanation** | ❌ | ✅ | NEW feature |
| **Simple Examples** | ❌ | ✅ | NEW feature |
| **Visual Diagrams** | ❌ | ✅ | NEW feature |
| **Analogies** | ❌ | ✅ | NEW feature |
| **Pseudocode** | ❌ | ✅ | NEW feature |
| **Status** | ✅ Active | ✅ Active | Both supported |
| **Backward Compat** | N/A | ✅ Full | Safe upgrade |
| **Breaking Changes** | N/A | ❌ None | Non-breaking |

---

## Changelog Summary

### What Changed Between Versions

**v1.0 → v1.1 Changes:**

**Additions (NEW Features):**
- ✅ Step 0: Algorithm identification workflow
- ✅ Step 3.5: Algorithm explanation (7-part)
- ✅ Section 5.5: Algorithm explanations in output
- ✅ Simple word explanations (no jargon)
- ✅ Real-world analogies
- ✅ Step-by-step examples with numbers
- ✅ Visual ASCII diagrams
- ✅ Pseudocode generation
- ✅ Common questions answered

**Enhancements (IMPROVED Features):**
- 🔵 Algorithm identification (now comprehensive)
- 🔵 Tools support (added Python, diagrams, web search)
- 🔵 Output format (added Section 5.5)

**Unchanged Features (PRESERVED from v1.0):**
- ✅ Paper validation
- ✅ Structure analysis
- ✅ Content extraction
- ✅ Novelty assessment
- ✅ Methodology evaluation
- ✅ Strength/weakness identification
- ✅ Logical consistency checking
- ✅ Citation quality assessment
- ✅ Practical value assessment
- ✅ Recommendations generation
- ✅ Error handling
- ✅ 15 core output sections

**No Breaking Changes:**
- ❌ Zero breaking changes
- ✅ Full backward compatibility
- ✅ v1.0 and v1.1 can coexist
- ✅ Automatic upgrade available
- ✅ No action needed to upgrade

### Feature Timeline

```
2026-08-03
├── v1.0 RELEASE
│   ├─ 12-step workflow
│   ├─ 15-section output
│   ├─ Core review features
│   └─ Full paper analysis
│
└── v1.1 RELEASE (same day)
    ├─ +1 step (Step 0)
    ├─ +1 step (Step 3.5)
    ├─ +1 section (5.5)
    ├─ Algorithm explanations
    ├─ Real-world analogies
    ├─ Step-by-step examples
    ├─ Visual diagrams
    └─ Pseudocode generation
```

### Upgrade Guide

**From v1.0 to v1.1:**
- ✅ Automatic (no manual steps)
- ✅ No breaking changes
- ✅ Backward compatible
- ✅ Can upgrade anytime
- ✅ Zero risk

**How to use v1.1:**
```
/research-paper-reviewer review paper
```

**Expected output:**
- v1.0 output (15 sections) + v1.1 new features (Section 5.5)

---

## Future Versions (Planned)

### v1.2 (Planned)
- [ ] Support for PDF links
- [ ] Auto-conversion to markdown
- [ ] Code implementation examples
- [ ] Algorithm complexity analysis
- [ ] Comparison with alternatives

### v2.0+ (Long-term)
- [ ] Interactive visualizations
- [ ] Multi-format input support
- [ ] Advanced code generation
- [ ] Integration with external resources

---

## How to Check Current Version

**In this file:**
- Look for "## Version History & Changelog" (this section)
- Check "### v1.1" or "### v1.0" for current version details

**In system-wide skill:**
- `C:\Users\prasad_ovhal\.claude\skills\research-paper-reviewer\SKILL.md`
- Same version history section

**In documentation:**
- `docs/09-skill-upgrade-v1.1.md` - Detailed upgrade guide
- `skills/CHANGELOG.md` - Comprehensive changelog

---

## Support & Documentation

- **Complete Guide:** `docs/00-index.md`
- **Basics:** `docs/01-introduction.md` and `docs/02-basics-about-skills.md`
- **Upgrade Details:** `docs/09-skill-upgrade-v1.1.md`
- **Full Changelog:** `skills/CHANGELOG.md`
- **Quick Reference:** `docs/03-dos-and-donts.md`

## Related Skills

- **Code Reviewer** - For reviewing research code/implementation
- **RAG Evaluator** - If the paper describes retrieval systems
- **Experiment Reviewer** - For detailed analysis of experiments
- **Conference Paper Reviewer** - For academic venue submission reviews
- **Research Paper Integrity Reviewer** - For assessing paper authenticity

## Notes for Future Versions

- Could add support for inline comments/annotations
- Could generate visual summary charts
- Could integrate with bibliography tools
- Could compare papers side-by-side
- Could track paper reading progress
