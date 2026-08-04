# Agent Skills Project

This repository contains a collection of reusable agent skills for analyzing, reviewing, and working with research papers and data science tasks.

## 📁 Project Structure

```
agent-skills/
├── docs/                          # Comprehensive documentation
│   ├── 00-index.md               # Navigation and quick start
│   ├── 01-introduction.md        # Foundations
│   ├── 02-basics-about-skills.md # Best practices
│   ├── 03-dos-and-donts.md       # Quick reference
│   ├── 04-skills-with-tools.md   # Skill-tool interaction
│   ├── 05-skills-with-mcp.md     # MCP architecture
│   ├── 06-list-of-skills-and-explanations.md # 16 ready-to-use skills
│   ├── 07-advanced-topics.md     # Production systems
│   └── 08-40-questions-coverage-map.md # Question mapping
│
├── skills/                        # Registered skills
│   ├── research-paper-reviewer.md # v1.0 - Main skill
│   └── Gen2IR.md                 # Sample paper for testing
│
├── theory/                        # Source materials
│   ├── chatgpt_convo             # Original ChatGPT conversation
│   ├── Agent_Skills_Handbook_40_Questions.docx
│   └── Agent_Skills_List_for_Data_Scientists.docx
│
└── CLAUDE.md                      # This file
```

---

## 🎯 Available Skills

### Research Paper Reviewer (v1.0)
**Location:** `skills/research-paper-reviewer.md`

**Purpose:** Analyze and review academic research papers in Markdown format

**How to Invoke:**
```
Please use the research-paper-reviewer skill to review [paper name/content]
```

**What It Does:**
- Validates markdown format (rejects PDFs)
- Extracts paper structure and key information
- Assesses novelty and methodology
- Identifies strengths and weaknesses
- Generates comprehensive structured review

**Input:** Markdown (.md) file containing research paper

**Output:** Detailed review with 15 sections:
1. Overview
2. Summary
3. Strengths
4. Weaknesses
5. Technical Assessment (table)
6. Key Findings
7. Logical Consistency
8. Related Work Assessment
9. Novelty Assessment
10. Questions & Concerns
11. Recommendations
12. Suggested Extensions
13. Potential Applications
14. Overall Assessment
15. Personal Insights

**Model Recommendation:** Claude Opus (deep reasoning required)

**Limitations:**
- Works only with markdown files
- Requires well-structured papers
- Cannot detect AI-generated content with certainty
- May miss domain-specific nuances

**Example Usage:**
```
I have a research paper on genetic algorithms for information retrieval.
Can you use the research-paper-reviewer skill to analyze it?

Here's the paper content:
[paper in markdown format]
```

### Article Summarizer (v1.0)
**Location:** `skills/article-summarizer.md`

**Purpose:** Summarize articles from any website, find similar articles, and compare content

**How to Invoke:**
```
Please use the article-summarizer skill to analyze [article URL(s)]
```

**What It Does:**
- Validates article URLs and checks accessibility
- Detects and alerts on paywalled content
- Extracts article content, title, author, and metadata
- Creates 1-2 paragraph summaries
- Searches for top 5 similar articles (only if single article provided)
- Extracts comprehensive bullet-point key points
- Generates comparison matrices (for multi-article input)
- Creates master notes with synthesized insights
- Formats study notes for easy reference

**Input:** One or more article URLs (from Medium, news sites, blogs, etc.)

**Output:** Structured analysis with multiple sections:
1. Article Summary (metadata and 1-2 paragraph overview)
2. Key Points - Main Article (bullet-point notes)
3. Similar Articles Analysis (if single article)
4. Comparison Matrix (what's included in each article)
5. Comprehensive Master Notes (synthesized insights)
6. Study Notes Format (organized reference material)

**Conditional Behavior:**
- Single article → Searches web for top 5 similar articles
- Multiple articles (2+) → Skips web search, focuses on comparison

**Model Recommendation:** Claude Opus (comparison depth) or Claude Sonnet (balanced)

**Limitations:**
- Cannot bypass paywalls automatically
- Cannot access content after user login
- Workaround: User can copy-paste article text for full analysis

**Example Usage:**
```
Summarize this article:
https://medium.com/article-about-ai

Compare these 3 articles:
https://example.com/article-1
https://example.com/article-2
https://example.com/article-3
```

---

## 📚 Documentation

All documentation is in the `docs/` folder. Start with:

1. **[docs/00-index.md](docs/00-index.md)** - Navigation hub with quick-start guides
2. **[docs/01-introduction.md](docs/01-introduction.md)** - Understand skills fundamentals
3. **[docs/02-basics-about-skills.md](docs/02-basics-about-skills.md)** - Learn best practices
4. **[docs/03-dos-and-donts.md](docs/03-dos-and-donts.md)** - Quick reference checklist
5. **[docs/06-list-of-skills-and-explanations.md](docs/06-list-of-skills-and-explanations.md)** - Catalog of 16 skills to build

For comprehensive coverage of 40 advanced questions:
- **[docs/07-advanced-topics.md](docs/07-advanced-topics.md)** - Production systems
- **[docs/08-40-questions-coverage-map.md](docs/08-40-questions-coverage-map.md)** - Question mapping

---

## 🚀 Quick Start

### Try the Research Paper Reviewer Skill

1. **Sample paper included:** `skills/Gen2IR.md`
2. **Invoke the skill:**
   ```
   Use the research-paper-reviewer skill to analyze Gen2IR.md
   ```
3. **Review output:** Get a comprehensive 15-section analysis

### Understand Skills Theory

1. Start: `docs/01-introduction.md` (10 min read)
2. Learn: `docs/02-basics-about-skills.md` (15 min read)
3. Reference: `docs/03-dos-and-donts.md` (quick check)

### Build More Skills

Use `docs/06-list-of-skills-and-explanations.md` as template for:
- Dataset Quality Analyzer
- Experiment Reviewer
- RAG Evaluator
- Code Reviewer
- And 11 more...

---

## 📖 Skill Development Guide

### How to Create a New Skill

Reference the research-paper-reviewer.md structure:

```markdown
# [Skill Name]

## Purpose
[One sentence on what it does]

## When to Use This Skill
[Situations where it should be chosen]

## Expected Input Format
[Type of input and requirements]

## Workflow Steps
[Numbered steps 1-N describing how to solve the problem]

## Tools to Use
[Python, SQL, Web search, etc.]

## Rules and Constraints
[Must follow and Should avoid]

## Output Format
[Exact format of the result]

## Error Handling
[How to handle common errors]

## Model Recommendation
[Recommended Claude model]

## Limitations
[What it can't do]

## Related Skills
[Links to complementary skills]
```

### Checklist Before Publishing a Skill

- [ ] One clear responsibility
- [ ] Clear inputs/outputs
- [ ] Workflow broken into ordered steps
- [ ] Error handling defined
- [ ] Output format specified
- [ ] Reusable (no hardcoded values)
- [ ] Can work independently
- [ ] Model recommendation included

---

## 🔗 How Skills Relate to Tools and MCP

### The Hierarchy
```
User Request
    ↓
Agent
    ↓
Skill (workflow orchestration)
    ↓
Tool (atomic action: Python, SQL, Web Search)
    ↓
MCP Server (optional: manages tools)
```

### Research Paper Reviewer Skill Example
```
User: "Review this research paper"
    ↓
Skill: research-paper-reviewer
├── Step 1: Validate markdown format
├── Step 2: Extract structure
├── Step 3: Analyze methodology
├── Step 4: Assess novelty
└── Step 12: Generate report
    ↓
Tools Used: None required (pure analysis)
            Optional: Web search for fact-checking
```

---

## 📊 Project Status

### Completed
✅ 9 comprehensive documentation files
✅ 40 advanced questions mapped and answered
✅ Research Paper Reviewer skill (v1.0 with v1.1 upgrade)
✅ Article Summarizer skill (v1.0)
✅ Gen2IR sample paper for testing
✅ Best practices checklist
✅ Learning paths for different roles
✅ Skill upgrade documentation
✅ Comprehensive version control and changelog

### In Progress
🔄 Additional skills development (Dataset Quality Analyzer, etc.)
🔄 Skill testing and validation
🔄 Example outputs and case studies

### Planned
📋 RAG Evaluator skill
📋 Experiment Reviewer skill
📋 Code Reviewer skill
📋 Production deployment guide
📋 Enterprise skill library patterns

---

## 🎓 Learning Paths

### For Individual Contributors (30 minutes)
1. Read: `docs/01-introduction.md`
2. Read: `docs/02-basics-about-skills.md`
3. Reference: `docs/03-dos-and-donts.md`
4. Try: Use research-paper-reviewer skill on Gen2IR.md

### For Team Leads (1 hour)
1. Read: `docs/00-index.md`
2. Skim: `docs/06-list-of-skills-and-explanations.md`
3. Study: `docs/07-advanced-topics.md` (Topics 10-12)
4. Assess: Skill creation needs for your team

### For Principal Data Scientists (2-3 hours)
1. Read all docs in `docs/` folder
2. Deep dive: `docs/07-advanced-topics.md`
3. Study: `docs/08-40-questions-coverage-map.md`
4. Plan: Enterprise skill library architecture

---

## 💡 Key Concepts

**Skill** = Reusable workflow that orchestrates multiple steps to solve a business problem

**Tool** = Single atomic action (Python function, SQL query, API call)

**MCP Server** = Infrastructure layer that publishes and manages tools

**Workflow** = Sequence of skills and tools to solve larger problems

---

## 🔍 How to Know If a Skill Is Being Used

### In Claude Code:

**Method 1: Direct Invocation (Explicit)**
```
I'll use the research-paper-reviewer skill to analyze this paper:
[Skill execution begins]
```
✅ Clear that skill is being used

**Method 2: Reference in Request**
```
Use the research-paper-reviewer skill on Gen2IR.md
```
✅ Explicitly requesting skill

**Method 3: Via Slash Command** (If registered)
```
/research-paper-reviewer Gen2IR.md
```
✅ Would work if registered as slash command

**Method 4: Automatic Selection** (If configured in CLAUDE.md)
```
Review this research paper
```
✅ Claude recognizes task matches research-paper-reviewer skill

### How to Confirm a Skill is Active:
1. **Look for acknowledgment** - Claude will say "Using research-paper-reviewer skill..."
2. **Check for workflow execution** - See numbered steps or structured output
3. **Review output format** - Compare to skill's defined output format
4. **Look in documentation** - It should be listed in CLAUDE.md

---

## ⚙️ Configuration

### Current Setup
- Project: `D:\Study\Git_repo\agent-skills\`
- Skills folder: `skills/`
- Docs folder: `docs/`
- Configuration: `.claude/settings.local.json`

### To Make a Skill Discoverable
1. ✅ Define it in `skills/` folder (done)
2. ✅ Register it in CLAUDE.md (this file)
3. ⚠️ [Optional] Add to MCP server if sharing across teams
4. ⚠️ [Optional] Create slash command if in IDE

---

## 📞 Quick Reference

**What is a skill?**
→ See `docs/01-introduction.md`

**How do I write one?**
→ See `docs/02-basics-about-skills.md`

**What skills should I build?**
→ See `docs/06-list-of-skills-and-explanations.md`

**How do I scale to many skills?**
→ See `docs/07-advanced-topics.md` Topic 10

**Where is research-paper-reviewer?**
→ `skills/research-paper-reviewer.md` (ready to use!)

**How do I use it?**
→ Invoke via "Use the research-paper-reviewer skill..."

---

## 📝 Version History

### v1.0 (2026-08-03)
- ✅ Initial documentation (8 files)
- ✅ All 40 questions answered
- ✅ Research Paper Reviewer skill (v1.0)
- ✅ Sample paper (Gen2IR.md)
- ✅ CLAUDE.md project file

---

## 🎯 Next Steps

1. **Try the skill** - Use research-paper-reviewer on Gen2IR.md
2. **Read documentation** - Start with docs/01-introduction.md
3. **Create next skill** - Use template from research-paper-reviewer.md
4. **Gather feedback** - Test with sample papers
5. **Iterate** - Improve based on usage

---

## 📄 License & Attribution

Based on comprehensive discussions with ChatGPT on:
- Agent skills architecture
- Tool vs. Skill distinction
- MCP server integration
- Production-scale deployment

Generated by Claude Code (Claude Haiku 4.5)
Last updated: 2026-08-03
