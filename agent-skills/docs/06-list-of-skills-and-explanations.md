# List of Agent Skills for Data Scientists

This document lists practical agent skills that can save time in daily work and serve as reusable building blocks for AI agents.

---

## 1. Research Paper Reviewer

**Purpose:** Summarize papers, extract methodology, datasets, metrics, strengths, weaknesses, novelty, limitations, and production ideas.

**Typical Inputs:**
- PDF
- CSV
- Code
- SQL
- Metrics
- Logs
- Documents

**Typical Outputs:**
- Structured report
- Recommendations
- Risks
- Next actions

**Use When:**
- You need to quickly understand a research paper
- You want to assess novelty or applicability to your work
- You need to extract specific technical details

---

## 2. Dataset Quality Analyzer

**Purpose:** Check missing values, duplicates, outliers, leakage, imbalance, correlations, and recommend fixes.

**Typical Inputs:**
- CSV
- Database table
- Parquet file
- SQL query results

**Typical Outputs:**
- Data quality report
- Identified issues (missing values, outliers, leakage)
- Recommendations for remediation
- Risk assessment

**Use When:**
- Starting a new ML project
- Investigating data quality issues
- Preparing data for model training

---

## 3. Experiment Reviewer

**Purpose:** Review ML experiments for validity, overfitting, metrics, leakage, and suggest next experiments.

**Typical Inputs:**
- MLflow experiment logs
- Model artifacts
- Metrics and parameters
- Training/test data splits

**Typical Outputs:**
- Experiment quality assessment
- Overfitting analysis
- Leakage detection
- Recommendations for improvement
- Suggested next experiments

**Use When:**
- You want to validate experimental methodology
- You need to assess model quality
- You're stuck and want fresh perspective on next steps

---

## 4. RAG Evaluator

**Purpose:** Evaluate retrieval quality, hallucination, groundedness, context precision/recall, and recommend improvements.

**Typical Inputs:**
- RAG pipeline outputs
- Retrieved documents
- Generated answers
- Ground truth references

**Typical Outputs:**
- Retrieval quality metrics
- Hallucination score
- Groundedness assessment
- Precision and recall analysis
- Improvement recommendations

**Use When:**
- Building or improving RAG systems
- Debugging poor retrieval or generation
- Evaluating RAG quality at scale

---

## 5. Agent Design Reviewer

**Purpose:** Review agent architectures for planning, memory, retries, guardrails, tool selection, and scalability.

**Typical Inputs:**
- Agent architecture design
- Tool definitions
- Skill descriptions
- System prompts
- Example logs

**Typical Outputs:**
- Architecture assessment
- Identified risks
- Best practice recommendations
- Scalability analysis
- Improvement suggestions

**Use When:**
- Designing new agent systems
- Reviewing agent architectures for production
- Troubleshooting agent behavior

---

## 6. Code Reviewer

**Purpose:** Review code quality, bugs, performance, maintainability, testing, and security.

**Typical Inputs:**
- Python code
- SQL queries
- Configuration files
- Test code

**Typical Outputs:**
- Code quality assessment
- Bug identification
- Performance recommendations
- Security issues
- Testing recommendations

**Use When:**
- Want to review code before deployment
- Need to assess code quality
- Looking for security vulnerabilities

---

## 7. Prompt Reviewer

**Purpose:** Evaluate prompts for ambiguity, missing constraints, output format, hallucination risk, and token efficiency.

**Typical Inputs:**
- Prompt text
- Example outputs
- Usage context

**Typical Outputs:**
- Clarity assessment
- Missing constraint identification
- Output format suggestions
- Hallucination risk analysis
- Token efficiency improvements

**Use When:**
- Designing system prompts
- Improving prompt quality
- Debugging unexpected LLM outputs

---

## 8. LLM Evaluation Skill

**Purpose:** Score model outputs using rubrics, reasoning, and failure categorization.

**Typical Inputs:**
- Model outputs
- Evaluation rubric
- Reference answers (optional)

**Typical Outputs:**
- Numerical scores
- Qualitative assessment
- Failure categorization
- Reasoning for scores

**Use When:**
- Evaluating LLM performance
- Categorizing failure modes
- Running evaluation benchmarks

---

## 9. SQL Optimization Reviewer

**Purpose:** Suggest indexing, join improvements, query simplification, and performance optimizations.

**Typical Inputs:**
- SQL queries
- Query execution plans
- Table schemas
- Performance metrics

**Typical Outputs:**
- Optimization recommendations
- Suggested indexes
- Join strategy improvements
- Performance projections

**Use When:**
- Slow database queries
- High infrastructure costs
- Need to optimize large datasets

---

## 10. Meeting Notes Summarizer

**Purpose:** Convert transcripts into summaries, decisions, action items, owners, and risks.

**Typical Inputs:**
- Meeting transcript
- Audio recording transcription
- Meeting notes

**Typical Outputs:**
- Executive summary
- Key decisions
- Action items with owners
- Risks identified
- Follow-up topics

**Use When:**
- Documenting important meetings
- Creating shareable summaries
- Tracking decisions and action items

---

## 11. GitHub Pull Request Reviewer

**Purpose:** Review pull requests for architecture, correctness, tests, documentation, and breaking changes.

**Typical Inputs:**
- Pull request diff
- Changed files
- Test results
- CI/CD logs

**Typical Outputs:**
- Architecture assessment
- Code quality issues
- Test coverage analysis
- Documentation gaps
- Breaking change identification

**Use When:**
- Code review workflow
- Ensuring code quality before merge
- Validating architectural changes

---

## 12. Feature Engineering Advisor

**Purpose:** Recommend feature engineering, preprocessing, encoding, scaling, and leakage prevention.

**Typical Inputs:**
- Dataset/schema
- Current features
- Target variable
- Business context

**Typical Outputs:**
- Feature engineering recommendations
- Preprocessing suggestions
- Encoding strategies
- Scaling recommendations
- Leakage prevention advice

**Use When:**
- Starting feature engineering
- Improving model performance
- Need guidance on feature strategy

---

## 13. Model Selection Advisor

**Purpose:** Recommend suitable ML algorithms based on data characteristics and business constraints.

**Typical Inputs:**
- Dataset characteristics
- Problem type (classification, regression, etc.)
- Business constraints (latency, interpretability, etc.)
- Performance requirements

**Typical Outputs:**
- Recommended algorithms
- Justification for each
- Tradeoffs analysis
- Implementation tips

**Use When:**
- Starting a new ML project
- Considering different model approaches
- Need to justify model choices

---

## 14. Production Readiness Reviewer

**Purpose:** Review monitoring, drift detection, logging, versioning, latency, scaling, rollback, and deployment readiness.

**Typical Inputs:**
- Model artifacts
- Monitoring setup
- Infrastructure configuration
- Deployment plan

**Typical Outputs:**
- Production readiness assessment
- Identified gaps
- Recommendations
- Risk assessment
- Deployment checklist

**Use When:**
- Preparing models for production
- Auditing production systems
- Planning model deployments

---

## 15. Conference Paper Reviewer

**Purpose:** Evaluate novelty, methodology, writing quality, experiments, ablations, citations, and reviewer concerns.

**Typical Inputs:**
- Paper PDF
- Supplementary materials
- Author response (if available)

**Typical Outputs:**
- Novelty assessment
- Methodology evaluation
- Experiment quality analysis
- Writing quality feedback
- Reviewer recommendations
- Concern summary

**Use When:**
- Peer review work
- Evaluating research for relevance
- Assessing paper quality

---

## 16. Research Paper Integrity Reviewer

**Purpose:** Review scientific quality and flag possible AI-assisted writing indicators without claiming definitive AI authorship.

**Typical Inputs:**
- Research paper PDF
- Writing samples from author (optional)

**Typical Outputs:**
- Overall paper quality assessment
- Writing quality analysis
- Technical depth evaluation
- Novelty assessment
- Logical consistency check
- Citation quality analysis
- Possible AI-assisted writing indicators (with confidence level)
- Recommendations

**Use When:**
- Evaluating research paper authenticity
- Assessing paper quality for acceptance
- Need to identify potential writing assistance

**Important Note:** This skill identifies indicators and patterns, not definitive proof of AI authorship. No current method reliably determines whether content was AI-generated.

---

## Recommended First Five Skills

If you're just starting with agent skills, prioritize these:

1. **Research Paper Reviewer** - Essential for research-heavy work
2. **RAG Evaluator** - Critical for GenAI applications
3. **Agent Design Reviewer** - Important for building agents
4. **Experiment Reviewer** - Core for ML workflows
5. **Production Readiness Reviewer** - Essential before deployment

---

## How to Use This Skills Library

### Step 1: Assess Your Needs
What are your most time-consuming tasks?
- Research and literature review? → Paper Reviewer
- Data preparation? → Dataset Quality Analyzer
- ML experimentation? → Experiment Reviewer
- Code quality? → Code Reviewer + Security Review

### Step 2: Start with High-ROI Skills
Skills that save the most time first:
1. Research Paper Reviewer (saves hours on literature)
2. RAG Evaluator (improves system quality)
3. Experiment Reviewer (prevents bad experiments)

### Step 3: Build Your Skill Library
As you become comfortable, expand to:
- Domain-specific skills (e.g., Feature Engineering Advisor for ML projects)
- Quality assurance skills (e.g., Production Readiness Reviewer)
- Collaborative skills (e.g., Meeting Notes Summarizer)

### Step 4: Customize
Adapt these skills for your specific:
- Domain expertise
- Team processes
- Tool stack
- Output preferences

---

## Integration Patterns

### With Tools
Each skill typically uses these tools:
- **Python** - For analysis, calculations, visualizations
- **SQL** - For database queries and data exploration
- **Web Search** - For gathering external information
- **PDF Reader** - For document analysis
- **APIs** - For accessing specialized services

### With MCP Servers
Skills can leverage MCP servers for:
- **GitHub** - Pull request and repository access
- **Slack** - Messaging and notifications
- **Database** - Snowflake, PostgreSQL, etc.
- **MLflow** - Experiment tracking
- **Jira** - Issue and project management

### With Models
Model recommendations:
- **Simple skills** (summarization) → Claude Haiku
- **Medium skills** (analysis) → Claude Sonnet
- **Complex skills** (review, design) → Claude Opus

---

## Summary Table

| Skill | Time Saved | Complexity | Key Tools |
|-------|-----------|-----------|-----------|
| Research Paper Reviewer | High | Medium | PDF Parser, Summarization |
| Dataset Quality Analyzer | High | Medium | Python, SQL |
| Experiment Reviewer | High | Medium | MLflow, Python |
| RAG Evaluator | High | High | LLM APIs, Metrics |
| Agent Design Reviewer | Medium | High | Architecture Analysis |
| Code Reviewer | Medium | Medium | Code Parser |
| Prompt Reviewer | Medium | Low | Prompt Analysis |
| LLM Evaluation Skill | Medium | Medium | Scoring Rubrics |
| SQL Optimizer | Medium | Medium | SQL Parser |
| Meeting Notes Summarizer | Medium | Low | Transcription |
| PR Reviewer | High | Medium | GitHub API |
| Feature Engineering | High | High | Data Analysis |
| Model Selection | Medium | High | Analysis |
| Production Readiness | High | High | Monitoring Tools |
| Conference Paper Reviewer | Low | High | Academic Analysis |
| Paper Integrity Reviewer | Medium | High | Writing Analysis |

---

## Next Steps

1. **Identify** which 2-3 skills would have the highest impact in your work
2. **Create** those skills using the patterns and best practices from this documentation
3. **Test** with sample inputs to ensure quality output
4. **Document** your skill configuration for team reuse
5. **Iterate** based on feedback and usage patterns
