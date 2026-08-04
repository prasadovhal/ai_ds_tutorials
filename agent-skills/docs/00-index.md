# Agent Skills Documentation Index

This documentation provides a comprehensive guide to understanding and building agent skills, based on conversations with ChatGPT about agentic AI systems.

---

## 📚 Documentation Structure

### [01-introduction.md](01-introduction.md)
**Overview and foundational concepts**

Start here if you're new to agent skills. Covers:
- What is an agent skill?
- Tools vs skills distinction
- Skill components
- Platform differences (Claude, Cursor, ChatGPT)
- Career progression

**Best for:** Getting started, understanding fundamentals

---

### [02-basics-about-skills.md](02-basics-about-skills.md)
**Core principles and best practices**

Detailed guide on writing high-quality skills. Covers:
- 10 best practices for skill design
- Skill components checklist
- Model selection recommendations
- Common anti-patterns
- Separation of concerns

**Best for:** Learning how to write good skills

---

### [03-dos-and-donts.md](03-dos-and-donts.md)
**Actionable quick reference**

Concise checklist for skill development. Covers:
- 10 Do's for skill design
- 10 Don'ts to avoid
- Quick validation checklist
- Key principles summary

**Best for:** Quick reference during skill development

---

### [04-skills-with-tools.md](04-skills-with-tools.md)
**How skills interact with tools**

Practical guide on skill-tool relationships. Covers:
- When to use tools vs skills
- How skills describe workflow
- Tool selection by agents
- Skill composition and nesting
- Infinite loop prevention

**Best for:** Understanding the skill-tool boundary

---

### [05-skills-with-mcp.md](05-skills-with-mcp.md)
**Skills and MCP server architecture**

Deep dive into MCP integration with skills. Covers:
- Architectural hierarchy (User → Agent → Skill → Tool → MCP)
- Without MCP vs with MCP patterns
- Tool discovery and selection
- Common misconceptions
- MCP as infrastructure layer

**Best for:** Understanding MCP architecture

---

### [06-list-of-skills-and-explanations.md](06-list-of-skills-and-explanations.md)
**Practical skill examples for data scientists**

Catalog of 16 pre-designed skills with explanations. Covers:
- Research Paper Reviewer
- Dataset Quality Analyzer
- Experiment Reviewer
- RAG Evaluator
- Agent Design Reviewer
- Code Reviewer
- Prompt Reviewer
- And 9 more...

**Best for:** Finding skill ideas, seeing examples

---

### [07-advanced-topics.md](07-advanced-topics.md)
**Production systems and enterprise concerns**

Advanced questions for scaling skills. Covers:
- Skill discovery by agents
- Granularity and composition
- Versioning and management
- Testing and evaluation
- Debugging failing skills
- Production readiness
- Cost and latency optimization
- Multi-agent systems
- Security considerations
- Enterprise skill libraries

**Best for:** Building production-grade skills

---

### [08-40-questions-coverage-map.md](08-40-questions-coverage-map.md)
**Mapping all 40 handbook questions to documentation**

Cross-reference guide for the 40 important questions from the handbook. Covers:
- Question mapping to documentation sections
- Quick lookup table
- Which documents answer which questions
- Finding answers to specific concerns

**Best for:** Finding answers to specific questions

---

### [09-skill-upgrade-v1.1.md](09-skill-upgrade-v1.1.md)
**Research Paper Reviewer Skill - Upgrade from v1.0 to v1.1**

Complete documentation of what changed in v1.1. Covers:
- New algorithm explanation capabilities
- Step-by-step example walkthroughs
- Real-world analogies for algorithms
- Visual diagrams and pseudocode
- Common questions about algorithms
- Backward compatibility
- Migration path from v1.0

**Best for:** Understanding the research-paper-reviewer upgrade

---

### [10-article-summarizer-skill.md](10-article-summarizer-skill.md)
**Article Summarizer Skill - Complete Guide**

Comprehensive documentation for the new article-summarizer skill. Covers:
- What the skill does (summarize, compare, research)
- Smart URL validation and paywall detection
- Conditional web search (1 article = search, 2+ = skip)
- Key point extraction and comparison matrices
- Study notes generation
- Use cases and examples
- Paywall workarounds
- Success criteria
- Model recommendations

**Best for:** Understanding the article-summarizer skill

---

## 🎯 Quick Start Guide

### If You Have 15 Minutes
1. Read: **01-introduction.md** (overview)
2. Skim: **03-dos-and-donts.md** (quick rules)

### If You Have 1 Hour
1. Read: **01-introduction.md** (foundations)
2. Read: **02-basics-about-skills.md** (principles)
3. Skim: **06-list-of-skills-and-explanations.md** (examples)

### If You Want to Build Your First Skill
1. Read: **02-basics-about-skills.md** (how to write)
2. Reference: **03-dos-and-donts.md** (checklist)
3. Study: **06-list-of-skills-and-explanations.md** (examples)
4. Check: **04-skills-with-tools.md** (tool selection)

### If You're Designing a Skill Library
1. Read: **01-introduction.md** (context)
2. Read: **07-advanced-topics.md** (enterprise concerns)
3. Study: **06-list-of-skills-and-explanations.md** (catalog)
4. Reference: **04-skills-with-tools.md** and **05-skills-with-mcp.md** (architecture)

### If You're Debugging a Failing Skill
1. Jump to: **07-advanced-topics.md** → Topic 5: Debugging
2. Reference: **04-skills-with-tools.md** → Tool selection
3. Check: **02-basics-about-skills.md** → Common anti-patterns

---

## 🔑 Key Concepts

### The Hierarchy
```
User
  ↓
Agent
  ↓
Skill (workflow orchestration)
  ↓
Tool (atomic capability)
  ↓
MCP Server (optional infrastructure)
```

### Core Distinction
- **Tool** = One atomic action (e.g., "read CSV")
- **Skill** = Workflow using multiple tools (e.g., "analyze CSV")

### Best Practice Pattern
1. Give skill ONE responsibility
2. Define clear inputs/outputs
3. Break into ordered steps
4. Specify tool guidance (not exact tools)
5. Handle edge cases
6. Keep reusable and deterministic

### Model Selection
| Task | Recommended |
|------|------------|
| Summarize | Haiku |
| Analyze | Sonnet |
| Review/Design | Opus |

---

## 📋 15-Point Skill Checklist

Before releasing a skill, verify:

- [ ] **Purpose** - One clear responsibility
- [ ] **When to use** - Situations clearly defined
- [ ] **Inputs** - Expected format documented
- [ ] **Outputs** - Format specified and consistent
- [ ] **Steps** - Workflow is ordered and clear
- [ ] **Tools** - Tool choices explained
- [ ] **Errors** - Edge cases handled
- [ ] **Reusability** - No hardcoded values
- [ ] **Reasoning** - Domain expertise shown
- [ ] **Determinism** - Consistent behavior
- [ ] **Documentation** - Clear for other engineers
- [ ] **Testing** - Test cases defined
- [ ] **Performance** - Latency acceptable
- [ ] **Security** - No secrets, validated inputs
- [ ] **Observability** - Loggable and monitorable

---

## 🚀 Learning Path for Principal Data Scientists

### Phase 1: Foundations (Week 1)
- Read: 01-introduction.md
- Read: 02-basics-about-skills.md
- Study: 06-list-of-skills-and-explanations.md (first 5 skills)

### Phase 2: Building (Week 2-3)
- Create: 2-3 simple skills
- Reference: 03-dos-and-donts.md during development
- Learn: 04-skills-with-tools.md
- Test: Skill quality against checklist

### Phase 3: Integration (Week 4)
- Learn: 05-skills-with-mcp.md
- Learn: Architecture patterns
- Integrate skills with MCP tools

### Phase 4: Production (Week 5-6)
- Study: 07-advanced-topics.md
- Implement: Error handling, logging, monitoring
- Build: Test suite and deployment process
- Design: Version management strategy

### Phase 5: Enterprise (Week 7+)
- Design: Skill library architecture
- Implement: Governance and standards
- Scale: Multi-team skill sharing
- Optimize: Performance, cost, latency

---

## 🔗 Cross-References

### If You're Asking...

**"What's a skill?"**
→ 01-introduction.md

**"How do I write a good skill?"**
→ 02-basics-about-skills.md + 03-dos-and-donts.md

**"When should this be a tool vs skill?"**
→ 04-skills-with-tools.md

**"How do skills work with MCP?"**
→ 05-skills-with-mcp.md

**"What skill should I build?"**
→ 06-list-of-skills-and-explanations.md

**"How do I deploy skills in production?"**
→ 07-advanced-topics.md (Topic 6)

**"How do I evaluate my skill?"**
→ 07-advanced-topics.md (Topic 4)

**"How do I debug a failing skill?"**
→ 07-advanced-topics.md (Topic 5)

**"How do I version my skills?"**
→ 07-advanced-topics.md (Topic 3)

**"How do I build an enterprise skill library?"**
→ 07-advanced-topics.md (Topic 10)

---

## 📖 Source Material

This documentation is compiled from:

1. **Comprehensive ChatGPT Conversation** - Detailed discussions on tools, skills, MCP architecture, and production systems
2. **Agent Skills Handbook for Principal Data Scientists** - 40 important questions with core concepts, best practices, and common mistakes
3. **Agent Skills List for Data Scientists** - Practical catalog of 16 pre-designed skills with explanations and use cases

---

## 🎓 Key Takeaways

### For Individual Contributors
- A skill encodes reusable domain expertise
- Good skills are portable across platforms
- Tools are building blocks; skills are solutions

### For Team Leads
- Skills enable consistent automation across teams
- Versioning and testing prevent regressions
- Clear documentation reduces maintenance burden

### For Principal Data Scientists
- Skills bridge ML engineering and systems engineering
- Enterprise skill libraries enable platform thinking
- Good architecture makes skills scalable and maintainable

---

## ❓ Common Questions

**Q: Is a skill just a prompt?**
A: No. A skill is a structured workflow with purpose, inputs, outputs, steps, tool guidance, and error handling. A prompt invokes a skill.

**Q: Can a skill use tools from MCP?**
A: Yes. Skills describe what's needed (conceptually), and agents choose which available tools to use.

**Q: Should I version every small change?**
A: No. Use semantic versioning: major for workflow changes, minor for new capabilities, patch for bug fixes.

**Q: How do I know if my skill is production-ready?**
A: Check the checklist in 07-advanced-topics.md (Topic 6). Focus on error handling, logging, testing, and monitoring.

**Q: What's the difference between Skill, Tool, and MCP?**
A: Tool = atomic action. Skill = orchestrates tools. MCP = manages/publishes tools.

---

## 📞 Getting Help

Refer to the relevant document section for:
- **Conceptual questions** → 01-introduction.md or 05-skills-with-mcp.md
- **How-to questions** → 02-basics-about-skills.md or 04-skills-with-tools.md
- **Example skills** → 06-list-of-skills-and-explanations.md
- **Production concerns** → 07-advanced-topics.md

---

## 📊 Skill Documentation

### Active Skills with Documentation

1. **Research Paper Reviewer (v1.0 → v1.1)**
   - Location: `skills/research-paper-reviewer.md`
   - Documentation: `docs/09-skill-upgrade-v1.1.md`
   - Status: v1.1 with algorithm explanations
   - Model: Opus (recommended) or Sonnet

2. **Article Summarizer (v1.0)**
   - Location: `skills/article-summarizer.md`
   - Documentation: `docs/10-article-summarizer-skill.md`
   - Status: Ready to use
   - Model: Opus (recommended) or Sonnet

### Planned Skills

- Dataset Quality Analyzer
- RAG Evaluator
- Experiment Reviewer
- Code Reviewer
- And more from 06-list-of-skills-and-explanations.md

---

## 📝 Notes for Your Review

This documentation was created by:
1. Extracting and organizing ChatGPT conversation content
2. Incorporating practical skill examples
3. Structuring into learning paths
4. Creating quick references and checklists
5. Documenting skill implementations and upgrades

**Please review and provide feedback on:**
- Clarity and organization
- Completeness of explanations
- Accuracy of examples
- Any missing sections or categories
- Any corrections needed
- Skill workflow accuracy

---

**Last Updated:** 2026-08-03
**Status:** 2 skills implemented, comprehensive documentation complete
**Next Steps:** Additional skill development, integration testing
