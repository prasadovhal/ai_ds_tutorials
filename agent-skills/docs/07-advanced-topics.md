# Advanced Topics in Agent Skills

This document covers important advanced questions about agent skills in production systems.

---

## Topic 1: How Does an Agent Discover the Correct Skill?

### The Problem

When you have multiple skills available, how does the agent know which one to use?

### The Key Principle

**Separation of Concerns:**
- **Skill decides:** What workflow to follow
- **Agent decides:** Which skill to invoke
- **Tools provide:** Atomic capabilities

### Best Practices

1. **Keep responsibilities clear** - Each skill has one purpose
2. **Reusable and observable** - Skills should be easy to describe
3. **Avoid mixing** - Don't mix business logic, orchestration, and tool implementation

### Example: Research Paper Reviewer

**The complete flow:**
1. Skill decides the workflow (read, extract, compare, evaluate)
2. Agent selects this skill based on user request
3. Agent selects appropriate tools (PDF reader, search tool, etc.)
4. MCP-exposed tools perform actions (search ArXiv, read PDFs)

### Related Questions

**Q: How does an agent choose between multiple matching skills?**

- Use clear, descriptive skill names and purposes
- Provide examples of when each skill should be used
- Let the agent reason over descriptions
- Consider using skill grouping or namespacing for organization

**Q: How should skills be named and described for accurate selection?**

- **Name:** Clear, action-oriented (e.g., "Research Paper Reviewer" not "Reviewer")
- **Description:** One sentence on purpose, one on when to use it
- **Examples:** Provide 2-3 example inputs/outputs
- **Boundaries:** Clearly state when NOT to use this skill

---

## Topic 2: Skill Granularity and Composition

### How Small Should a Skill Be?

**Question:** Should "RAG Evaluation" be one skill or multiple skills?

**Decision Framework:**

Keep as ONE skill if:
- All steps share the same purpose
- They're always done together
- The user requests them as one task
- They produce one unified output

Split into SEPARATE skills if:
- They solve different problems
- They're used independently
- They have different tool requirements
- They produce separate outputs

### Example: Research Paper Review

**Could split into:**
- Paper Metadata Extractor
- Methodology Reviewer
- Citation Checker
- Novelty Evaluator

**Keep as one if:**
- User always asks: "Review this paper"
- Each step informs the next
- Produces one comprehensive review

**Split if:**
- User sometimes asks for just citation checking
- Each can be used independently
- Different teams need different reviewers

### When to Create a New Skill vs Extending an Existing One

**Use ONE skill if:**
- Core workflow is 80%+ identical
- Only minor variations needed
- Users can't distinguish between them

**Use SEPARATE skills if:**
- Different workflows
- Different tool requirements
- Different output formats
- Users explicitly name them differently

### Example

- Research Paper Reviewer
- Research Proposal Reviewer
- Conference Paper Reviewer

These might all be one "Research Reviewer" skill with a "document_type" parameter, OR separate skills if the workflows diverge significantly.

### Skill Communication and Composition

**Can one skill call another skill?**

In standard architecture: Not directly.

Instead:
1. Skill A runs and calls a Tool
2. That Tool (implementation) might internally invoke another agent
3. That agent executes Skill B

This is common in **multi-agent systems** but requires careful design.

**How should multiple related skills be organized?**

- By domain (e.g., "ML Ops" skills)
- By team (e.g., "Data Science" skills)
- By project (e.g., "Churn Prediction" skills)
- By capability (e.g., "Review" skills)

Choose the organization that makes skills easiest to discover and maintain.

---

## Topic 3: Skill Versioning and Management

### How Do You Version Skills?

Naming convention example:
- paper-review-v1
- paper-review-v2
- paper-review-v3

### Version Management Strategy

**When to increment version:**
1. **Major change** (v1.0 → v2.0): Different workflow, incompatible inputs/outputs
2. **Minor change** (v1.0 → v1.1): New capability, compatible with old versions
3. **Patch** (v1.0 → v1.0.1): Bug fix, no functional change

### How to Know if a New Version Is Better

Metrics to track:
- **Success rate** - % of successful executions
- **User satisfaction** - Feedback from skill users
- **Tool selection accuracy** - % of correct tool choices
- **Cost** - Tokens consumed per execution
- **Latency** - Execution time
- **Failure rate** - % of failed executions

### Backwards Compatibility

- Document breaking changes clearly
- Provide migration guide for old version users
- Maintain old versions during transition period
- Set deprecation timeline

---

## Topic 4: Skill Testing and Evaluation

### How Do You Test a Skill?

Similar to unit tests for Python:

```
Input A → Expected Output A
Input B → Expected Output B
```

This becomes an automated regression test suite.

### Example Test Cases

**Skill:** Research Paper Reviewer

Test cases:
1. Valid PDF → Structured review output
2. Missing abstract → Handled gracefully
3. Non-academic paper → Appropriate handling
4. Very long paper (100+ pages) → Reasonable latency

### How Do You Evaluate the Quality of a Skill?

Use these metrics:

1. **Correctness** - Does it solve the stated problem?
2. **Completeness** - Does it produce all required outputs?
3. **Consistency** - Do repeated runs produce similar outputs?
4. **Latency** - How long does it take?
5. **Cost** - Token usage and API costs
6. **User satisfaction** - Do users find it useful?
7. **Failure handling** - How gracefully does it handle errors?

### How Do You Benchmark One Version Against Another?

Setup:
1. Define evaluation dataset (30-50 representative examples)
2. Run both versions on the dataset
3. Compare metrics across all test cases
4. Statistical significance testing (if using larger datasets)
5. User feedback on output quality

Metrics to compare:
- Success rate
- Output quality (using rubrics)
- Latency
- Cost
- Error handling

---

## Topic 5: Debugging and Troubleshooting

### How Do You Debug a Failing Skill?

When a skill fails, diagnose:

1. **Was the prompt wrong?**
   - Unclear instructions?
   - Missing context?
   - Conflicting constraints?

2. **Was the tool wrong?**
   - Tool not available?
   - Tool returned unexpected output?
   - Tool timed out?

3. **Was the model wrong?**
   - Model misunderstood task?
   - Model hallucinating?
   - Model too small for task?

4. **Was the retrieved context wrong?**
   - Missing information?
   - Irrelevant information?
   - Incomplete data?

5. **Was the workflow wrong?**
   - Steps in wrong order?
   - Missing intermediate step?
   - Unclear transitions?

### Debugging Checklist

- [ ] Can I reproduce the failure?
- [ ] Does it fail on all inputs or just specific ones?
- [ ] Which step in the workflow fails?
- [ ] What's the exact error message?
- [ ] Did this work in a previous version?
- [ ] Does it work with a stronger model?
- [ ] Is the tool actually being called?

---

## Topic 6: Production Readiness

### What Makes a Skill Production-Ready?

**Essential components:**

1. **Error handling** - Graceful failure with clear messages
2. **Logging** - Track execution for debugging
3. **Timeouts** - Prevent infinite loops
4. **Retry policies** - Handle transient failures
5. **Observability** - Monitor in production
6. **Security** - No hardcoded secrets, input validation
7. **Versioning** - Clear version tracking
8. **Documentation** - Usage guide and examples
9. **Testing** - Automated test suite
10. **Rollback plan** - How to revert if needed

### Example Production Checklist

- [ ] Error messages are clear and actionable
- [ ] All secrets are externalized (no hardcoding)
- [ ] Inputs are validated
- [ ] Outputs are consistent
- [ ] Timeouts are configured
- [ ] Logging is comprehensive
- [ ] Test coverage is ≥80%
- [ ] Documentation is complete
- [ ] Performance meets SLAs
- [ ] Security review completed

---

## Topic 7: Skill Optimization

### How Do You Optimize Skill Cost?

**Strategy: Progressive model routing**

```
Haiku (fast, cheap)
  ↓
  Only if confidence is low
  ↓
Sonnet (balanced)
  ↓
  Still uncertain
  ↓
Opus (powerful, expensive)
```

This routing pattern can **dramatically reduce cost**.

### How Do You Optimize for Latency?

**Strategies:**
1. **Parallel tool calls** - Call multiple tools simultaneously
2. **Early termination** - Stop if we have enough information
3. **Caching** - Store results from repeated queries
4. **Pruning** - Skip unnecessary steps
5. **Model selection** - Use faster models for simple tasks

### How Do You Optimize for Token Usage?

**Strategies:**
1. **Prompt compression** - Remove unnecessary words
2. **Structured outputs** - JSON vs. natural language
3. **Context pruning** - Include only relevant information
4. **Summarization** - Reduce input size
5. **Tool usage** - Use tools instead of LLM reasoning

---

## Topic 8: Skills in Production Systems

### How Do You Make Skills Model-Agnostic?

Across Claude, ChatGPT, Gemini, and others:

**Avoid model-specific features:**
- ❌ "Use Claude's thinking feature"
- ❌ "Use GPT-4's vision"

**Instead:**
- ✅ "Use the available model's reasoning capability"
- ✅ "If vision is required, use a model with vision support"

### How Do You Decide Which Model Should Execute a Skill?

**Decision factors:**
1. **Task complexity** - Simple = small model, complex = large model
2. **Latency requirements** - Tight deadline = fast model
3. **Cost constraints** - Budget = smaller model
4. **Quality requirements** - High accuracy = large model
5. **Availability** - Use what's available

### How Do You Handle Skills in Multi-agent Systems?

**Architecture:**

```
Agent A
  ↓ (uses Skill A)
  Tool A
    ↓ (invokes)
  Agent B
    ↓ (uses Skill B)
    Tool B
```

**Considerations:**
- Avoid circular dependencies
- Set depth limits
- Implement timeouts
- Clear interface contracts
- Monitoring at each level

### How Do You Compose Multiple Skills into a Larger Workflow?

**Pattern: Skill orchestration**

```
User Request
  ↓
Orchestrator Agent
  ↓
Selects Skill A
  ↓
Skill A completes
  ↓
Selects Skill B (based on Skill A results)
  ↓
Skill B completes
  ↓
Combines results
  ↓
Returns final output
```

**Key decisions:**
1. Sequential vs. parallel execution
2. How to pass state between skills
3. Error handling and fallbacks
4. Result aggregation

---

## Topic 9: Skills and Context Management

### How Do Skills Use Memory and Conversation Context?

**Design principle:** Skills should be context-independent.

A skill should work even if:
- It's the first message in a conversation
- It's isolated from prior context
- It's called by a different agent

**When to use context:**
- Only pass necessary information
- Make it explicit in skill parameters
- Don't assume user remembers prior discussion

### How Should Skills Be Documented and Maintained?

**Documentation includes:**
1. **Purpose statement** - One sentence on what it does
2. **Use cases** - When to use it
3. **Inputs/outputs** - Expected format and examples
4. **Error cases** - How it handles failures
5. **Examples** - Sample usage
6. **Limitations** - What it can't do
7. **Maintenance notes** - Known issues, future improvements

### How Do You Observe and Log Skill Execution?

**Logging strategy:**
1. **Start** - Log skill name, inputs, timestamp
2. **Steps** - Log each major step completion
3. **Tools** - Log tool calls and results
4. **End** - Log final output, latency, cost
5. **Errors** - Log all failures with context

**Example log entry:**
```
{
  "skill": "research_paper_reviewer",
  "status": "started",
  "input_size": "2.5 MB",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Topic 10: Enterprise-Scale Skills

### How Do You Organize Dozens of Skills?

Imagine having 40 skills. Organization strategies:

**By domain:**
- ML Operations Skills
- Data Pipeline Skills
- Research Skills

**By team:**
- Data Science Skills
- Engineering Skills
- Operations Skills

**By capability:**
- Review Skills
- Analysis Skills
- Generation Skills

**By project:**
- Churn Prediction Skills
- Recommendation Engine Skills

### How Do You Package, Distribute, and Reuse Skills?

**Distribution options:**
1. **Shared repository** - Central location for all skills
2. **Package format** - YAML, JSON, or custom format
3. **Versioning** - Semantic versioning
4. **Documentation** - README, examples, tests
5. **Testing** - Pre-release test suite

### How Do You Build a Reusable Enterprise Skill Library?

**Strategy:**

1. **Start small** - 5-10 core skills
2. **Standardize** - Common format, naming, structure
3. **Document** - Clear purpose, inputs, outputs
4. **Test** - Automated tests for each skill
5. **Review** - Team review before adding to library
6. **Share** - Distribute to teams
7. **Gather feedback** - Improve based on usage
8. **Scale** - Grow as teams adopt

**Governance:**
- Version control
- Deprecation policy
- Breaking change notification
- Usage tracking
- Performance monitoring

---

## Topic 11: Advanced Architecture Decisions

### When Should a Task Be a Tool Instead of a Skill?

**Factors:**

- **Tool:** Atomic, reusable, well-defined
- **Skill:** Orchestrated, domain-specific, decision-heavy

Ask: Can multiple teams use this independently?
- Yes → Probably a tool
- No → Probably a skill

### When Should Logic Go Into Code vs a Skill?

**In Code:**
- Atomic operations
- Data transformations
- Algorithm implementations
- Performance-critical code

**In Skill:**
- Decision logic
- Workflow orchestration
- Tool selection
- Error handling strategy

### When Should You Use Local Tools vs MCP?

**Local tools:**
- Single use
- Frequently changing
- Local resources only

**MCP tools:**
- Multiple teams use it
- Infrastructure-managed
- Group related tools
- Version control important

### When Should a Workflow Belong in a Skill, Agent, or LangGraph?

**Skill:** Simple, linear workflow (< 10 steps)
**Agent:** Complex reasoning with branching
**LangGraph:** Graph-based orchestration, multiple agents, loops

---

## Topic 12: Security Considerations

### What Security Considerations Should Be Included?

1. **Input validation** - Check all user inputs
2. **Secret management** - Never hardcode keys
3. **Access control** - Verify user permissions
4. **Output sanitization** - Clean output before returning
5. **Audit logging** - Log sensitive operations
6. **Error messages** - Don't leak sensitive info

### How Do Permissions and Access Control Affect Skill Execution?

**Examples:**
- Only authorized users can run expensive skills
- Database access requires authentication
- API calls need credentials
- File access has permission checks

**Implementation:**
- Check permissions at skill start
- Log all access attempts
- Provide clear error messages for denied access

---

## Summary: Advanced Skill Questions

| Question | Key Point |
|----------|-----------|
| **Discovery** | Clear naming and descriptions help agents choose right skill |
| **Granularity** | Match skill size to problem scope |
| **Versioning** | Semantic versioning with clear migration paths |
| **Testing** | Automated test suites prevent regressions |
| **Production** | Error handling, logging, monitoring essential |
| **Optimization** | Progressive routing, caching, early termination |
| **Scale** | Enterprise library needs governance and standards |
| **Security** | Input validation, secrets, access control critical |

---

## Three Most Valuable Questions for Your Career

Given your goal of becoming a Principal Data Scientist:

1. **How do you evaluate and benchmark agent skills?**
   - Builds evaluation frameworks for GenAI systems

2. **How do you version, test, and deploy skills in production?**
   - Moves you into platform engineering

3. **How do you design a library of 50-100 reusable skills?**
   - Enables team scaling and enterprise adoption

These questions move you beyond creating individual workflows into engineering maintainable agent platforms that entire teams rely on.
