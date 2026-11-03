# Mapping: All 40 Questions Coverage

This document maps all 40 questions from the Agent Skills Handbook to specific sections in the documentation.

---

## Questions 1-3: Skill Discovery

**Q1: How does an agent discover the correct skill?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 1: Skill Discovery
- Separation of concerns
- Best practices for clear responsibilities
- Example: Research Paper Reviewer

**Q2: How does an agent choose between multiple matching skills?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 1: Related Questions
- Use clear, descriptive names
- Provide examples
- Let agent reason over descriptions
- Skill grouping/namespacing

**Q3: How should skills be named and described for accurate selection?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 1: Related Questions
- Name: action-oriented
- Description: clear purpose + when to use
- Examples: 2-3 sample inputs/outputs
- Boundaries: when NOT to use

---

## Questions 4-8: Skill Granularity & Composition

**Q4: How small or large should a skill be?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 2: Skill Granularity
- Keep as ONE if steps share purpose
- Split if solve different problems
- Decision framework provided

**Q5: When should I create a new skill instead of extending an existing one?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 2: Extending vs Creating
- Use ONE if 80%+ identical workflow
- Use SEPARATE if different workflows
- Example: Research Reviewers

**Q6: How should multiple related skills be organized?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 2: Organization
- By domain
- By team
- By project
- By capability

**Q7: Can one skill call another skill?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q8: Skill Nesting
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 2: Composition
- Not directly in standard architecture
- Tool implementation can invoke another agent
- Common in multi-agent systems

**Q8: How do skills communicate with each other?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q8: Skill Communication
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 8: Multi-agent Systems
- Through shared tools
- Via agent orchestration
- State passing between skills

---

## Questions 9-14: Skills, Tools, and MCP

**Q9: How do skills work with tools?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q2: How Skills Use Tools
- Skills describe workflow
- Agents choose which tool to use
- Good vs bad patterns
- Portability principle

**Q10: How do skills work with MCP servers?**
📄 **File:** [05-skills-with-mcp.md](05-skills-with-mcp.md) (Entire document)
- Architectural hierarchy
- With/without MCP patterns
- Real-world examples
- Data scientist workflow

**Q11: How do skills discover newly available tools?**
📄 **File:** [05-skills-with-mcp.md](05-skills-with-mcp.md) → Q9: Tool Discovery
- Agent reads available tools from MCP
- Similar to reading function docstrings
- Tools advertised when connecting

**Q12: When should logic be implemented in a skill versus in code?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q5: Logic Placement
- In Code: atomic operations, transformations, algorithms
- In Skill: decision logic, orchestration, error strategy
- Separation of concerns principle

**Q13: When should something be a tool instead of a skill?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q1: Tool vs Skill
- Tool: atomic, reusable, well-defined
- Skill: orchestrated, domain-specific
- Decision framework with questions

**Q14: When should a tool be local versus exposed through an MCP server?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q6: Local vs MCP Tools
- Local: single use, frequently changing, local resources
- MCP: multiple teams, infrastructure-managed, version control

---

## Questions 15-18: Versioning, Testing, Evaluation

**Q15: How do you version skills?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 3: Skill Versioning
- Naming convention (v1, v2, v3)
- Version increments (major, minor, patch)
- Backwards compatibility strategy

**Q16: How do you test skills?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 4: Skill Testing
- Automated test suites
- Input → Expected Output patterns
- Example test cases
- Regression testing

**Q17: How do you evaluate the quality of a skill?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 4: Quality Evaluation
- Correctness
- Completeness
- Consistency
- Latency, cost, user satisfaction
- Failure handling

**Q18: How do you benchmark one version of a skill against another?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 4: Benchmarking
- Evaluation dataset (30-50 examples)
- Metrics comparison
- Statistical significance testing
- User feedback collection

---

## Questions 19-22: Debugging & Reliability

**Q19: How do you debug a failing skill?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 5: Debugging
- Diagnose prompt, tool, model, context, workflow issues
- Debugging checklist
- Root cause analysis approach

**Q20: How do you make skills deterministic and reliable?**
📄 **File:** [02-basics-about-skills.md](02-basics-about-skills.md) → Best Practice #10
- Same input → similar output
- Avoid unnecessary randomness
- Consistent error handling

**Q21: How do you handle errors and retries inside skills?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 6: Production Readiness
- Graceful failure with clear messages
- Retry policies
- Timeout configuration
- Error handling strategy in skill instructions

**Q22: How do you prevent infinite loops or recursive skill execution?**
📄 **File:** [04-skills-with-tools.md](04-skills-with-tools.md) → Q10: Infinite Loops
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 5: Debugging
- Depth limits
- Timeout policies
- Loop detection
- Clear termination conditions

---

## Questions 23-26: Optimization & Model Selection

**Q23: How do you optimize skills for latency and cost?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 7: Cost Optimization
- Progressive model routing
- Parallel tool calls
- Early termination
- Model selection strategy

**Q24: How do you optimize skills for token usage?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 7: Token Optimization
- Prompt compression
- Structured outputs
- Context pruning
- Summarization

**Q25: How do you make skills model-agnostic across Claude, ChatGPT, Gemini, and others?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 8: Model Agnostic
- Avoid model-specific features
- Use capability-based language
- Graceful degradation

**Q26: How do you decide which model should execute a particular skill?**
📄 **File:** [02-basics-about-skills.md](02-basics-about-skills.md) → Recommended Model Selection
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 8: Model Selection
- Decision factors: complexity, latency, cost, quality, availability
- Task to model mapping table
- Fallback strategies

---

## Questions 27-29: Context & Multi-Agent Systems

**Q27: How do skills use memory and conversation context?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 9: Context Management
- Skills should be context-independent
- Pass necessary info explicitly
- Don't assume user memory
- First-message execution

**Q28: How do skills work in multi-agent systems?**
📄 **File:** [05-skills-with-mcp.md](05-skills-with-mcp.md) → Q4-5: Nested Agents
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 8: Multi-agent Architecture
- Skill A → Tool A → Agent B → Skill B
- Avoid circular dependencies
- Set depth limits
- Clear interface contracts

**Q29: How do you compose multiple skills into a larger agent workflow?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 8: Skill Composition
- Skill orchestration pattern
- Sequential vs parallel execution
- State passing between skills
- Result aggregation

---

## Questions 30-35: Production Systems

**Q30: What makes a skill production-ready?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 6: Production Readiness
- Error handling, logging, timeouts
- Retry policies, observability
- Security, versioning
- Documentation, testing, rollback plan

**Q31: How should skills be documented and maintained?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 9: Documentation
- Purpose statement
- Use cases
- Inputs/outputs with examples
- Error cases, limitations
- Maintenance notes

**Q32: What are common anti-patterns when writing skills?**
📄 **File:** [02-basics-about-skills.md](02-basics-about-skills.md) → Anti-patterns Section
📄 **File:** [03-dos-and-donts.md](03-dos-and-donts.md) → Don'ts (10 items)
- One huge skill, hardcoded values
- Duplicate skills, forcing unnecessary tools
- Mixing business/tool logic
- Over-constraining, conversation dependency

**Q33: What security considerations should be included in skills?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 12: Security
- Input validation, secret management
- Access control, output sanitization
- Audit logging, safe error messages

**Q34: How do permissions and access control affect skill execution?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 12: Access Control
- Check permissions at skill start
- Log all access attempts
- Clear error messages for denied access
- Example: database auth, API credentials

**Q35: How do you observe and log skill execution in production?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 9: Observability
- Log start, steps, tools, end
- Track latency and cost
- Error logging with context
- Example log entry format

---

## Questions 36-40: Enterprise Scale

**Q36: How do you package, distribute, and reuse skills across teams?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 10: Distribution
- Shared repository
- Package format
- Versioning strategy
- Documentation, testing

**Q37: How do you build a reusable enterprise skill library?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 10: Enterprise Library
- Start small, standardize, document
- Test, review, share
- Gather feedback, scale
- Governance: version control, deprecation, notification

**Q38: How do you decide whether a workflow belongs in a skill, an agent, or an orchestration framework like LangGraph?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 11: Architecture Decisions
- Skill: simple, linear (< 10 steps)
- Agent: complex reasoning with branching
- LangGraph: graph-based, multiple agents, loops

**Q39: How do skills interact with evaluation frameworks and automated testing?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 4: Testing & Evaluation
- Test suites for skills
- Automated regression testing
- Quality metrics
- Benchmarking frameworks

**Q40: How do enterprise AI teams manage hundreds of skills at scale?**
📄 **File:** [07-advanced-topics.md](07-advanced-topics.md) → Topic 10: Enterprise Scale
- Skill library architecture
- Governance and standards
- Multi-team skill sharing
- Performance monitoring
- Deprecation policies

---

## Coverage Summary

| Question Set | Coverage | File(s) |
|--------------|----------|---------|
| Q1-3: Discovery | ✅ Complete | 07-advanced-topics.md |
| Q4-8: Granularity & Composition | ✅ Complete | 04, 07 |
| Q9-14: Skills/Tools/MCP | ✅ Complete | 04, 05, 07 |
| Q15-18: Versioning & Testing | ✅ Complete | 07-advanced-topics.md |
| Q19-22: Debugging & Reliability | ✅ Complete | 04, 07 |
| Q23-26: Optimization | ✅ Complete | 02, 07 |
| Q27-29: Context & Multi-agent | ✅ Complete | 05, 07 |
| Q30-35: Production | ✅ Complete | 07-advanced-topics.md |
| Q36-40: Enterprise | ✅ Complete | 07-advanced-topics.md |

## Quick Reference

**All 40 questions are covered** across 8 markdown files:

- **Foundation** (Start here): 01-introduction.md
- **Learning** (How to write): 02-basics-about-skills.md, 03-dos-and-donts.md
- **Implementation** (Building skills): 04-skills-with-tools.md, 05-skills-with-mcp.md
- **Examples** (Ready-to-use): 06-list-of-skills-and-explanations.md
- **Production** (Advanced): 07-advanced-topics.md
- **Navigation** (Overall guide): 00-index.md

---

## By File

### 00-index.md
- Quick-start guides
- Learning paths
- Cross-references
- 15-point checklist

### 01-introduction.md
- Tools vs Skills (Q9, Q13)
- Skill components
- Career progression

### 02-basics-about-skills.md
- Best Practices (Q1-8, 20)
- Model selection (Q26)
- Anti-patterns (Q32)
- 10-point checklist

### 03-dos-and-donts.md
- Actionable rules (Q1-8, 20, 32)
- Quick validation checklist

### 04-skills-with-tools.md
- Q1, Q2, Q5, Q6, Q7, Q8, Q9, Q12, Q13, Q14, Q22
- Skill-tool interaction
- Tool discovery
- Composition patterns

### 05-skills-with-mcp.md
- Q10, Q11, Q27, Q28
- MCP architecture
- Multi-agent systems
- Tool integration

### 06-list-of-skills-and-explanations.md
- 16 practical skills
- Real-world examples
- Integration patterns
- Model recommendations

### 07-advanced-topics.md
- Q1-Q40 (all advanced topics)
- 12 major topics
- Production concerns
- Enterprise scale

### 08-40-questions-coverage-map.md
- This file
- Complete mapping
- Where to find answers
- Coverage summary

---

## How to Use This Map

**If you're looking for an answer to Question #X:**
1. Find Question X in this document
2. See the recommended file(s)
3. Navigate to the specific section
4. Use 00-index.md for cross-references if needed

**All 40 questions from the Agent Skills Handbook are comprehensively covered!** ✅
