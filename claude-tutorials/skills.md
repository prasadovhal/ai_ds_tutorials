# Agent Skills: From Concept to Creation

> A complete guide to understanding agent skills in general, then mastering them in Claude Code — with real-life analogies, examples, and step-by-step walkthroughs.

---

## Part 1: What Are Agent Skills? (The Big Picture) 

### The Simple Analogy

Think of an AI agent as a **new employee on their first day**. They're smart, capable, and eager — but they don't know your company's processes, tools, or quirks. Every time they start a task, they ask: *"How do we do things here?"*

A **skill** is like handing that employee a **Standard Operating Procedure (SOP)**. It tells them:
- What the task is
- When to do it
- How to do it step by step
- What tools to use
- What to avoid

Once they have the SOP, they don't ask the same questions again. They just *do the work*.

### Real-Life Parallels

| Real World | Agent World |
|------------|-------------|
| A recipe card in a kitchen | A skill that tells the agent how to "cook" a specific task |
| A pilot's preflight checklist | A skill that runs safety checks before deployment |
| An employee handbook chapter | A skill that encodes coding standards or review processes |
| A doctor's diagnostic protocol | A skill that walks through debugging steps systematically |

### What Makes a Skill Different from a Prompt?

| Aspect | A Prompt | A Skill |
|--------|----------|---------|
| **Lifespan** | One conversation | Permanent — works across all sessions |
| **Reusability** | You retype it every time | Write once, invoke forever |
| **Trigger** | You manually type it | Can auto-trigger when relevant |
| **Shareability** | Copy-paste to others | Check into git, the whole team gets it |
| **Complexity** | Usually simple | Can include scripts, templates, tool restrictions, model selection |

### Why Skills Matter for Agentic AI

In the agentic AI paradigm, the agent doesn't just answer questions — it **takes actions**: reads files, writes code, runs commands, calls APIs. Without skills:

- The agent invents its own approach every time (inconsistent)
- You repeat the same instructions across sessions (wasteful)
- The agent can't learn from your corrections (no memory)
- Team members get different results (no standardization)

With skills:

- **Consistency** — The same task is done the same way every time
- **Efficiency** — No re-explaining; the skill encodes your preferences
- **Quality** — Encode expert knowledge so even simple prompts produce expert results
- **Safety** — Restrict dangerous tools, enforce review steps, block risky commands
- **Scalability** — One person writes the skill, the entire team benefits

---

## Part 2: The Anatomy of a Skill (General Model)

Every agent skill, regardless of platform, has these core components:

```
┌─────────────────────────────────────────────┐
│                  A SKILL                     │
├──────────────┬──────────────────────────────┤
│  METADATA    │ Name, description, when to   │
│              │ trigger, who can invoke it    │
├──────────────┼──────────────────────────────┤
│  CONSTRAINTS │ Which tools to allow/deny,   │
│              │ which model to use, effort    │
├──────────────┼──────────────────────────────┤
│  CONTEXT     │ Background info the agent    │
│              │ needs (standards, patterns)   │
├──────────────┼──────────────────────────────┤
│  INSTRUCTIONS│ Step-by-step process for     │
│              │ the agent to follow           │
├──────────────┼──────────────────────────────┤
│  INPUTS      │ Arguments/parameters the     │
│              │ user provides at invocation   │
└──────────────┴──────────────────────────────┘
```

### Example: A "Code Review" Skill in Plain English

```
NAME:        code-review
TRIGGER:     When someone says "review my code" or "check this PR"
CONSTRAINTS: Read-only (don't modify files), use Sonnet (cheaper)
CONTEXT:     Our team follows Google's style guide, prefers small functions
INSTRUCTIONS:
  1. Read the changed files
  2. Check for bugs, security issues, and style violations
  3. Suggest improvements ranked by severity
  4. Output a summary with pass/fail recommendation
INPUTS:      Optional PR number or file path
```

This pattern is universal — whether you're using Claude Code, LangChain, CrewAI, AutoGen, or any agentic framework.

---

## Part 3: Skills in Claude Code

### How Claude Code Implements Skills

In Claude Code, a skill is a **markdown file** (`SKILL.md`) inside a specific directory. It has:

1. **YAML frontmatter** (between `---` markers) — metadata and constraints
2. **Markdown body** — the actual instructions Claude follows

```
.claude/skills/my-skill/
├── SKILL.md              ← Required: frontmatter + instructions
├── reference.md          ← Optional: detailed docs Claude can read
├── examples.md           ← Optional: usage examples
├── template.txt          ← Optional: output templates
└── scripts/
    └── validate.sh       ← Optional: scripts the skill can run
```

### Skills vs Other Claude Code Features

| Feature | What It Does | How It Differs from Skills |
|---------|-------------|---------------------------|
| **CLAUDE.md** | Project context loaded every session | Always-on context; skills load on-demand |
| **Custom Commands** | `.claude/commands/name.md` → `/name` | Functionally identical to skills (merged system) |
| **Hooks** | Run scripts on lifecycle events | Deterministic automation; not Claude-driven |
| **MCP Servers** | Connect external tools/APIs | Adds tools; skills add knowledge/process |
| **Agents** | Isolated AI workers with their own context | Skills are instructions; agents are workers |

### Where Skills Live

| Scope | Location | Available In | Shared? |
|-------|----------|-------------|---------|
| **Personal** | `~/.claude/skills/name/SKILL.md` | All your projects | No (just you) |
| **Project** | `.claude/skills/name/SKILL.md` | This project only | Yes (via git) |
| **Nested** | `apps/web/.claude/skills/name/SKILL.md` | That subdirectory | Yes (via git) |

**Personal skills** = your preferences across all projects (like your IDE settings).
**Project skills** = team conventions for this repo (like a shared linter config).

---

## Part 4: Creating Your First Skill (Step by Step)

### Example 1: "Commit Helper" — Your First Skill

**Goal:** A skill that writes good commit messages following your team's convention.

#### Step 1: Create the directory

```bash
mkdir -p .claude/skills/commit-helper
```

#### Step 2: Write SKILL.md

```markdown
---
description: Write a conventional commit message for staged changes. Use when the user asks to commit, write a commit message, or says "commit this."
disable-model-invocation: true
---

## Staged Changes

!`git diff --cached --stat`

## Detailed Diff

!`git diff --cached`

## Instructions

Write a commit message for the staged changes above following these rules:

1. Use conventional commits format: `type(scope): description`
2. Types: feat, fix, refactor, docs, test, chore, style, perf
3. Keep the subject line under 72 characters
4. Add a blank line then a body if the change needs explanation
5. Reference issue numbers if visible in branch name or diff

Show me the commit message, then ask if I want to proceed with the commit.
```

#### Step 3: Use it

```
> /commit-helper
```

Claude reads the staged diff (injected via `!` commands), writes a message following your rules, and asks for confirmation.

**What happened:**
- `description` tells Claude when this skill is relevant
- `disable-model-invocation: true` means only YOU can trigger it (prevents accidental commits)
- `!`git diff --cached`` runs the command and injects the output before Claude reads the skill
- The markdown body is the instructions Claude follows

---

### Example 2: "Bug Investigator" — A Skill with Arguments

**Goal:** Given a bug description, Claude systematically investigates before jumping to fixes.

```markdown
---
description: Systematically investigate a bug before attempting fixes. Use when the user reports a bug or unexpected behavior.
argument-hint: "[bug description]"
allowed-tools: Read Grep Glob Bash(npm test *) Bash(git log *)
---

# Bug Investigation Protocol

## Bug Report
$ARGUMENTS

## Investigation Steps

Follow these steps IN ORDER. Do not skip to fixing until all steps are complete:

### Step 1: Reproduce
- Identify the exact steps or conditions that trigger the bug
- Find the relevant file(s) using Grep and Glob
- Confirm you can see the problematic code

### Step 2: Understand
- Read the surrounding code to understand intent
- Check git log for recent changes to the affected files
- Identify the root cause (not just the symptom)

### Step 3: Assess Impact
- What else could this bug affect?
- Are there related patterns elsewhere in the codebase?
- Could the fix break something else?

### Step 4: Report
Present your findings:
- **Root cause:** [one sentence]
- **Affected files:** [list]
- **Impact:** [low/medium/high]
- **Suggested fix:** [approach, not code yet]
- **Risk of fix:** [what could go wrong]

Ask the user if they want to proceed with the fix.
```

**Usage:**
```
> /bug-investigator Users see a blank screen after login on Safari
```

**Why this is powerful:**
- `allowed-tools` limits Claude to read-only tools + tests — it can't accidentally modify files during investigation
- `$ARGUMENTS` captures the bug description
- The structured steps prevent Claude from jumping to a fix before understanding the problem
- The report format gives you enough info to make an informed decision

---

### Example 3: "API Endpoint" — A Skill with Named Arguments

**Goal:** Scaffold a new API endpoint following your team's patterns.

```markdown
---
description: Create a new API endpoint following project conventions
argument-hint: "[method] [path] [description]"
arguments: [method, path, desc]
---

# Create New API Endpoint

Create a **$method** endpoint at **$path**.

**Purpose:** $desc

## Requirements

1. Follow the patterns in existing route files (check @src/routes/ for examples)
2. Include:
   - Input validation using zod
   - Error handling with proper HTTP status codes
   - TypeScript types for request and response
   - A test file in the corresponding __tests__ directory
3. Register the route in @src/routes/index.ts
4. Add the endpoint to @docs/api.md

## Verification

After creating the endpoint:
1. Run `npm test` to verify tests pass
2. Run `npm run typecheck` to verify types
```

**Usage:**
```
> /api-endpoint POST /api/users/invite "Send an invitation email to a new user"
```

Claude receives:
- `$method` = "POST"
- `$path` = "/api/users/invite"
- `$desc` = "Send an invitation email to a new user"

---

### Example 4: "Deploy" — A Safety-Critical Skill

**Goal:** A deployment skill that only runs when explicitly invoked and follows a strict checklist.

```markdown
---
description: Deploy the application to the specified environment
disable-model-invocation: true
argument-hint: "[staging|production]"
arguments: [env]
---

# Deploy to $env

## Pre-Deploy Checklist

Before deploying, verify ALL of the following:

1. Run `npm test` — all tests must pass
2. Run `npm run build` — build must succeed
3. Run `npm run lint` — no errors
4. Check `git status` — working directory must be clean
5. Check `git log origin/main..HEAD` — confirm changes are expected

If ANY check fails, STOP and report the failure. Do NOT proceed.

## Deploy

Only if all checks pass:

1. For staging: `npm run deploy:staging`
2. For production: `npm run deploy:production`

## Post-Deploy

1. Wait 30 seconds
2. Run `curl -s https://$env.example.com/health | jq .`
3. Report the health check result
4. If unhealthy, suggest rollback steps
```

**Why `disable-model-invocation: true` matters here:** You don't want Claude to autonomously decide "I should deploy this." Deployment is a human decision.

---

## Part 5: Skill Features Deep Dive

### Dynamic Context Injection (`!` Commands)

Lines starting with `` !`command` `` are executed BEFORE Claude reads the skill. The output replaces the line.

```markdown
## Current Branch
!`git branch --show-current`

## Recent Changes
!`git log --oneline -5`

## Package Version
!`node -p "require('./package.json').version"`
```

Claude sees the actual values, not the commands. This gives skills real-time awareness.

**Multi-line commands:**
````markdown
```!
npm --version
node --version
git status --short
```
````

All three outputs are injected inline.

---

### Model and Effort Control

Force a specific model or thinking effort for a skill:

```yaml
---
name: quick-rename
model: haiku
effort: low
---
Rename $0 to $1 in all files. Don't change logic.
```

```yaml
---
name: architecture-review
model: opus
effort: max
---
Deeply analyze the system architecture...
```

| Effort Level | When to Use |
|-------------|-------------|
| `low` | Simple renames, formatting |
| `medium` | Standard feature work |
| `high` | Complex implementations |
| `xhigh` | Architecture decisions, debugging |
| `max` | Hardest problems — equivalent to ultrathink |

---

### Tool Control

#### Allow specific tools (pre-approved, no permission prompt):
```yaml
allowed-tools: Read Grep Bash(git *) Bash(npm test *)
```

#### Deny specific tools (removed from Claude's toolkit):
```yaml
disallowed-tools: Write Edit Bash(rm *)
```

**Use case:** A "research" skill that can read everything but can't modify anything:
```yaml
---
name: research
allowed-tools: Read Grep Glob
disallowed-tools: Write Edit Bash
---
```

---

### Running Skills in Subagents (`context: fork`)

Heavy research or analysis can run in an isolated subagent, keeping your main session clean:

```yaml
---
name: deep-research
description: Research a topic across the codebase
context: fork
agent: Explore
---

Research $ARGUMENTS:
1. Find all relevant files
2. Read and analyze patterns
3. Summarize findings with file references
```

The subagent gets its own context window, does the work, and returns a summary to your main session.

---

### Variable Reference

| Variable | What It Contains | Example |
|----------|-----------------|---------|
| `$ARGUMENTS` | Everything the user typed after the command | `/fix 404 error` → `"404 error"` |
| `$ARGUMENTS[0]` or `$0` | First argument | `"404"` |
| `$ARGUMENTS[1]` or `$1` | Second argument | `"error"` |
| `$name` | Named argument (from `arguments` frontmatter) | With `arguments: [issue]`, `$issue` works |
| `${CLAUDE_SESSION_ID}` | Current session identifier | For logging |
| `${CLAUDE_EFFORT}` | Current effort level | `low`, `medium`, `high`, etc. |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md | For referencing supporting files |

**Escaping:** Use `\$` for a literal dollar sign (e.g., `costs \$5`).

---

## Part 6: Complete SKILL.md Reference

### Full Frontmatter Schema

```yaml
---
# ── Identity ──
name: my-skill                              # Display name (defaults to directory name)
description: When and why to use this skill  # Key trigger phrase — be specific
when_to_use: Additional trigger context      # Appended to description
argument-hint: "[arg1] [arg2]"              # Shown in autocomplete

# ── Arguments ──
arguments: [arg1, arg2]                     # Named positional args → $arg1, $arg2

# ── Invocation Control ──
disable-model-invocation: true              # true = user-only (for side-effect actions)
user-invocable: false                       # false = Claude-only (background knowledge)

# ── Tool Control ──
allowed-tools: Read Grep Bash(git *)        # Pre-approved without prompts
disallowed-tools: Write Edit                # Removed while skill active

# ── Model & Effort ──
model: sonnet                               # sonnet | opus | haiku | fable | inherit
effort: high                                # low | medium | high | xhigh | max

# ── Execution ──
context: fork                               # Run in isolated subagent
agent: Explore                              # Subagent type (Explore | Plan | general-purpose)
paths: ["src/**/*.ts"]                      # Only load for matching file paths
shell: bash                                 # Shell for ! commands (bash | powershell)

# ── Lifecycle Hooks ──
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "npm run lint --fix"
---

# Markdown body: your instructions for Claude
```

### How the Command Name Is Determined

| File Location | Command Name |
|--------------|-------------|
| `.claude/skills/deploy/SKILL.md` | `/deploy` |
| `~/.claude/skills/deploy/SKILL.md` | `/deploy` |
| `apps/web/.claude/skills/deploy/SKILL.md` | `/apps/web:deploy` |
| `.claude/commands/deploy.md` | `/deploy` |

---

## Part 7: Real-World Skill Collection

### Starter Kit: 6 Skills Every Project Should Have

#### 1. commit-message (saves time on every commit)
```yaml
---
description: Generate a conventional commit message for staged changes
disable-model-invocation: true
---

!`git diff --cached`

Write a conventional commit message (type(scope): description) for the diff above.
Keep the subject under 72 chars. Ask before committing.
```

#### 2. pr-summary (saves time on every PR)
```yaml
---
description: Summarize changes for a pull request description
---

## Changes
!`git log origin/main..HEAD --oneline`

## Diff Summary
!`git diff origin/main --stat`

Write a PR description with: a one-line summary, bullet points of changes,
and a testing checklist. Use markdown format.
```

#### 3. investigate (prevents jumping to wrong fixes)
```yaml
---
description: Investigate before fixing — understand root cause first
allowed-tools: Read Grep Glob Bash(git log *) Bash(npm test *)
disallowed-tools: Write Edit
---

Investigate this issue: $ARGUMENTS

1. Find related files
2. Read the code and understand intent  
3. Check git history for recent changes
4. Identify root cause
5. Report findings WITHOUT making changes
```

#### 4. new-component (enforces team patterns)
```yaml
---
description: Scaffold a new React component following project conventions
arguments: [name]
---

Create a new component called $name:

1. Check existing components in @src/components for patterns
2. Create @src/components/$name/$name.tsx
3. Create @src/components/$name/$name.test.tsx
4. Create @src/components/$name/index.ts (barrel export)
5. Follow the same structure as existing components
6. Run `npm test` to verify
```

#### 5. explain-code (onboards new team members)
```yaml
---
description: Explain how a piece of code works in plain language
model: haiku
effort: low
---

Explain the code in $ARGUMENTS in plain language:

1. What does it do? (one paragraph)
2. How does it work? (step by step)
3. What are the key dependencies?
4. Any gotchas a new developer should know?

Keep it concise. No code changes.
```

#### 6. security-check (catches issues before they ship)
```yaml
---
description: Check recent changes for common security issues
disallowed-tools: Write Edit
---

## Recent Changes
!`git diff HEAD~1`

Review the diff above for security issues:

- Hardcoded secrets, API keys, passwords
- SQL injection vulnerabilities  
- XSS vectors (unescaped user input in HTML)
- Missing input validation
- Insecure dependencies
- Exposed internal paths or error details

Rate each finding as CRITICAL / HIGH / MEDIUM / LOW.
If nothing found, confirm the changes look safe.
```

---

## Part 8: Tips and Troubleshooting

### Writing Good Descriptions (Most Important Part)

The `description` field determines when Claude auto-invokes your skill. Bad descriptions = skill never triggers or triggers at wrong times.

```yaml
# Bad: too vague
description: Help with code

# Bad: too narrow
description: Fix TypeScript compilation errors in auth module

# Good: specific trigger with context
description: Review staged git changes for bugs, security issues, and style
  violations. Use when the user asks to review code, check changes, or prepare
  a commit.
```

### Debugging Skills

**Skill not appearing?**
- Check it's in the right directory (`.claude/skills/name/SKILL.md`)
- Run `/skills` to see all loaded skills
- Check for YAML syntax errors in frontmatter

**Skill not auto-triggering?**
- Verify `disable-model-invocation` is NOT set to `true`
- Make the description match the language users actually use
- Test with `/skill-name` directly first

**Skill triggers too often?**
- Make the description more specific
- Add `disable-model-invocation: true` if it should be manual-only

**Supporting files not found?**
- Use `${CLAUDE_SKILL_DIR}` to reference files relative to the skill directory
- Example: `python3 ${CLAUDE_SKILL_DIR}/scripts/analyze.py`

### Performance Tips

- **Use `model: haiku`** for simple skills (explain, rename, format) — 15-25x cheaper than Opus
- **Use `context: fork`** for heavy research — keeps your main session light
- **Use `disallowed-tools`** to prevent unnecessary file reads during focused tasks
- **Use `!` injection** to give Claude data upfront instead of having it search for it (fewer tool calls = fewer tokens)

### Security Considerations

- Project skills (`.claude/skills/`) require **workspace trust** — Claude asks before using skills from untrusted repos
- Review third-party skills before trusting them — they can run arbitrary commands via `!` injection
- Use `disable-model-invocation: true` for any skill that has side effects (deploy, delete, publish)
- Use `disallowed-tools` to enforce read-only investigation skills

---

## Part 9: From General Agentic Skills to Claude Code — A Translation Guide

If you've worked with other agentic frameworks, here's how concepts map:

| General Concept | Claude Code Equivalent |
|----------------|----------------------|
| System prompt | CLAUDE.md + SKILL.md body |
| Tool definitions | MCP servers + `allowed-tools` |
| Agent instructions | SKILL.md markdown body |
| Agent config (model, temp) | SKILL.md frontmatter (`model`, `effort`) |
| Tool restrictions | `allowed-tools` / `disallowed-tools` |
| Agent spawning | `context: fork` + `agent: Explore` |
| Workflow orchestration | Skills chaining via natural language |
| Shared team prompts | Project skills checked into git |
| Personal agent config | User skills in `~/.claude/skills/` |
| Guardrails | Hooks (PreToolUse) + `disallowed-tools` |
| Dynamic context / RAG | `!` command injection in skills |

### The Key Insight

Most agentic frameworks require you to write Python/TypeScript to define agents, tools, and workflows. Claude Code skills are **just markdown files**. The barrier to entry is as low as it gets:

1. Create a folder
2. Write a markdown file
3. Done — it works

No compilation, no dependencies, no deployment. Edit the file and it takes effect immediately, even mid-session.

---

## Quick Reference

### Minimum Viable Skill
```
mkdir -p .claude/skills/my-skill
```

```yaml
# .claude/skills/my-skill/SKILL.md
---
description: What this skill does and when to use it
---

Your instructions here. $ARGUMENTS contains user input.
```

### Invoke It
```
/my-skill some arguments here
```

### Key Files
```
~/.claude/skills/         → Personal skills (all projects)
.claude/skills/           → Project skills (this repo)
.claude/commands/         → Legacy commands (still works, same as skills)
.claude/agents/           → Custom subagent definitions
```

### Key Commands
```
/skills                   → List all loaded skills
/skill-name               → Invoke a skill directly
/skill-name arg1 arg2     → Invoke with arguments
```

---

*Part of the Claude Code Best Practices collection. See also: `claude-code-best-practices.md`*
