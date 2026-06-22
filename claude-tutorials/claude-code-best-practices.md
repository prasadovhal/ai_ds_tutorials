# Claude Code Best Practices: Ranked from Most to Least Impactful

> Compiled from 4 Medium articles covering 100+ skills and battle-tested productivity techniques. Verified against actual Claude Code features — fabricated commands removed. Includes token optimization strategies throughout.

---

## Tier 1: Game Changers

### 1. CLAUDE.md - Persistent Project Context

The single most recommended technique across every article. Create a `CLAUDE.md` file at your project root that documents your tech stack, coding standards, project structure, common commands, and discovered gotchas. Claude reads it at every session start — it transforms Claude from "meeting a stranger each time" to "working with a context-aware partner."

```bash
# Auto-generate one to get started
claude /init
```

**Why it's #1:** Every correction you add compounds — each fix improves all future sessions for everyone on the team. Anthropic calls this "Compounding Engineering."

**Token tips:**
- Keep it at **~150-200 lines**. Every extra line is read at session start and costs tokens on every interaction.
- Put all repeating preferences here (e.g., "use TypeScript strict mode", "prefer vitest") instead of re-stating them in prompts.
- Keep it stable — frequent edits invalidate the prompt cache.
- If it grows beyond 200 lines, split into focused files or move details into `.claude/commands/`.

```
# Check your CLAUDE.md size
wc -l CLAUDE.md
```

---

### 2. Verification & Self-Checking Loops

The official Anthropic guide says: *"If you only adopt one practice, make it verification — giving Claude a way to check its own output."* Include test commands or linter checks in your prompts so Claude catches its own mistakes. Install LSP plugins for automatic type checking after every edit — described as "the single highest-impact plugin you can install." This yields **2-3x quality improvements**.

```
Example prompt: "Implement the auth middleware, then run the tests and fix any failures."
```

---

### 3. Plan Mode (Shift+Tab) - Think Before Building

Press `Shift+Tab` to cycle permission modes, including Plan Mode. Use it before any multi-file change or unfamiliar codebase work. Claude maps out the approach before writing a single line of code. Pour effort into the plan so Claude can one-shot the implementation. Use `/plan` for standard planning or `/ultraplan` for cloud-based multi-agent planning.

**Why it matters:** Prevents wasted tokens and effort on incorrect approaches. Gets your first pass to 80% instead of 60%.

---

### 4. /init - Instant Project Understanding

Run `/init` at your project root and Claude analyzes your repository structure, dependencies, naming conventions, and coding patterns. It generates a `CLAUDE.md` automatically. Without it, Claude's responses remain generic rather than repo-specific.

```bash
cd your-project && claude
> /init
```

**Why it matters:** Saves 10-15 minutes at the start of every coding session. Claude suddenly understands your folder structure, your stack, and your conventions.

---

### 5. Parallel Sessions with --worktree

The biggest productivity unlock: run 3-5 Claude sessions simultaneously, each in its own isolated git worktree.

```bash
claude --worktree feature-auth
claude --worktree feature-dashboard
claude --worktree bugfix-api
```

Each session works on a separate branch independently. Use `/batch` for large-scale migrations that fan out across dozens of parallel agents, each testing independently and creating separate PRs.

---

### 6. /review - Pre-Commit Code Review

Run `/review` before every commit. Claude performs a comprehensive analysis covering bugs, security risks, architecture issues, performance problems, and code smells. It acts as an automated senior-engineer-level reviewer. Use `/ultrareview` for a multi-agent cloud-based review covering logic, security, and performance simultaneously.

---

## Tier 2: Major Productivity Boosters

### 7. MCP Server Integration

Connect Claude to external platforms — GitHub, PostgreSQL, Supabase, Linear, Notion, Slack, browsers, Figma — turning it from a chatbot into an autonomous agent. Claude can read tickets, modify code, open PRs, and generate documentation through natural language.

```json
// ~/.claude/config.json
{
  "mcpServers": {
    "github": { "command": "gh", "args": ["mcp"] },
    "slack": { "command": "slack-mcp", "args": ["--token", "$SLACK_TOKEN"] }
  }
}
```

**Real impact:** One author reports not having written a line of SQL in 6+ months thanks to database MCP integration.

---

### 8. Custom Commands (.claude/commands/)

Store markdown files in `.claude/commands/` to transform repetitive multi-step workflows into single slash commands. Commands can reference other commands for automation chains.

```
.claude/commands/
  new-api-endpoint.md    # Creates validated endpoints with tests
  pr.md                  # Reviews commits, summarizes changes
  refactor-plan.md       # Identifies code smells with estimates
  debug-session.md       # Systematic bug investigation
  ship-feature.md        # Plan -> implement -> test -> document
  quick-fix.md           # Minimal-touch bug fixes
```

```markdown
<!-- .claude/commands/quick-fix.md -->
Find and fix the issue described below. Only modify the minimum number 
of files needed. Run tests after fixing. Do not refactor surrounding code.

$ARGUMENTS
```

```bash
> /project:quick-fix the date picker shows wrong timezone on Safari
```

**Token savings:** The command template is loaded once; without it, you'd re-type the constraints every time.

---

### 9. /memory - Persistent Preferences

Save coding standards, tech preferences, and style rules that persist across sessions. No more repeating "use TypeScript strict mode" or "prefer Tailwind + shadcn/ui" every conversation.

```bash
> /memory Always use Server Actions over API routes
> /memory Prefer Tailwind + shadcn/ui for all UI work
```

---

### 10. /compact - Compress Without Losing Context

When sessions get long and Claude starts losing coherence, run `/compact` to compress the conversation into a summarized memory. You keep the context but regain speed and focus.

**Use it proactively, not reactively.** Compact early — especially before:
- Starting a new sub-task within the same session
- Large multi-file edits
- Any architectural discussion after a long debugging session

```bash
# Compact with a custom summary focus
/compact focus on the auth refactor decisions we made
```

**Auto-compact:** Configure automatic compaction so you never hit context limits unexpectedly.

```json
// .claude/settings.json
{
  "contextCompaction": {
    "enabled": true,
    "threshold": 80
  }
}
```

**Token savings:** Compaction can reduce context by 50-80% while preserving key decisions.

---

### 11. /clear & Session Hygiene

Wipe session history when switching between unrelated work. A five-second reset often outperforms thirty minutes of diminishing returns. Claude's quality degrades in bloated contexts.

**One task per session.** Don't reuse sessions across unrelated tasks. Each unrelated question adds permanent context bloat.

```bash
# Session 1: Fix the login bug
claude
> fix the 401 error in @auth/login.ts

# Session 2 (separate): Add dashboard feature
claude
> implement the analytics dashboard per @docs/dashboard-spec.md
```

If you must use one session for multiple topics, `/clear` between them:

```
> fix the typo in @README.md
[done]
> /clear
> now help me design the caching layer
```

---

## Tier 3: Advanced Workflow Techniques

### 12. Skills - Reusable Expert Behaviors

Install community skills that encode expert-level workflows into Claude's behavior.

**Top 6 Skills (ranked by impact):**

| Rank | Skill | What It Does |
|------|-------|-------------|
| 1 | **Superpowers** | Enforces senior-dev practices: planning, isolated testing, pre-code test writing, dual-stage reviews. Gets first-pass quality from 60% to 80%. |
| 2 | **Grill Me** | Asks 16-50 thorough questions about your project before implementation begins. Eliminates assumptions. |
| 3 | **Skill Creator** | Builds custom skills from plain English. Compresses the learning curve to 5 minutes. |
| 4 | **Frontend Design** | Encodes spacing, typography, and layout principles. Produces professional designs instead of "generic AI" aesthetics. |
| 5 | **Context Mode** | Filters command noise and maintains session memory logs. Enables hours-long sessions without context loss. |
| 6 | **Claude Mem** | Preserves project knowledge across sessions with automatic documentation updates. |

---

### 13. Subagents for Deep Investigation

Spawn separate Claude instances with isolated context windows for research tasks, keeping your main session clean. Configure custom agents with specific tools, models, and permissions.

```bash
claude --agent=security-reviewer
claude --agent=quick-search
```

---

### 14. Hooks - Automated Lifecycle Actions

Deterministic automation at specific lifecycle points:

- **PreToolUse:** Block dangerous commands (`rm -rf`, `drop table`)
- **PostToolUse:** Auto-format code after every edit
- **SessionStart:** Load project context
- **Stop:** Run final checks

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "command": "bun run format"
    }]
  }
}
```

---

### 15. Choose the Right Model for the Task

Not every task needs Opus. Use `--model` to pick the cheapest model that handles the job.

```bash
# Simple tasks: use Haiku (fastest, cheapest)
claude --model haiku "rename this variable from 'x' to 'userCount' in @utils.ts"

# Medium tasks: use Sonnet (good balance)
claude --model sonnet "add input validation to @api/routes.ts"

# Hard tasks: use Opus (most capable, most expensive)
claude --model opus "redesign the entire caching layer"
```

| Task Type | Model | ~Cost Ratio |
|-----------|-------|-------------|
| Renaming, formatting, simple fixes | Haiku | 1x |
| Feature implementation, tests, reviews | Sonnet | 3-5x |
| Architecture, complex debugging, multi-system | Opus | 15-25x |

---

### 16. Ultrathink for Hard Problems

Add "ultrathink" to your prompt to trigger adaptive deep reasoning on Opus. Claude dynamically allocates more thinking effort based on complexity. Use it surgically — it consumes significantly more tokens.

**Worth the tokens:**
- Debugging race conditions or concurrency bugs
- Designing system architecture with multiple tradeoffs
- Security vulnerability analysis
- Complex algorithm implementation

**Not worth the tokens:**
- Adding a new field to a form
- Writing straightforward CRUD endpoints
- Renaming variables or formatting changes

---

## Tier 4: Token Optimization & Efficient Prompting

### 17. Write Precise, Structured Prompts

Vague prompts cause Claude to explore broadly (reading many files, asking clarifying questions). Precise prompts go straight to execution.

```
# Vague (Claude explores broadly, burns tokens):
"something is wrong with the API"

# Precise (Claude targets exactly what's needed):
"The POST /api/users endpoint in @src/routes/users.ts returns 500 
when email contains a '+'. Fix the email validation on line 45."
```

**Structure for complex requests:**
```
GOAL: [what you want]
FILES: [which files to touch]
CONSTRAINTS: [what NOT to do]
VERIFY: [how to confirm it works]
```

---

### 18. @file References Instead of Pasting Code

Direct Claude to exact files rather than pasting code into your prompt. Every pasted block burns tokens permanently in the conversation.

```
# Bad (wastes tokens):
"Here's my auth middleware: [pastes 200 lines]"

# Good (Claude reads only what it needs):
"Fix the session handling in @src/auth/middleware.ts"
```

**Why:** Claude reads the file with tool calls (efficient, not stored in chat history) rather than processing inline pasted content that sits in the conversation permanently.

---

### 19. Raw Data Over Interpretation

Paste error logs, stack traces, and CI output directly instead of summarizing them. Claude extracts root causes better from original data than from human descriptions.

```
# Bad:  "I'm getting a type error in my auth module"
# Good: *paste the full stack trace*
```

---

### 20. Batch Related Changes in One Prompt

Multiple small prompts cost more than one well-structured prompt because each turn re-sends the full conversation context.

```
# Expensive (3 round trips, context sent 3 times):
> "add email validation"
> "add phone validation" 
> "add address validation"

# Cheap (1 round trip):
> "add validation for email, phone, and address fields in @forms/contact.ts. 
   Use zod schemas matching the patterns in @forms/user.ts"
```

---

### 21. Piping: git diff & cat into Claude

Pipe content directly into Claude for focused analysis without opening a full session.

```bash
# PR review
git diff | claude -p "review these changes"

# Analyze just one file
cat src/critical-module.ts | claude -p "find potential race conditions"

# Analyze test output
npm test 2>&1 | claude -p "summarize failures and suggest fixes"

# Analyze logs
tail -100 app.log | claude -p "identify the root cause of the 503 errors"
```

**Token savings:** Only the piped content enters the context — no project scanning, no file exploration.

---

### 22. Limit Image and Screenshot Usage

Images consume significantly more tokens than text. Use them only when text can't convey the information.

```
# Expensive (image tokens):
"Here's a screenshot of the error" [attaches 1080p screenshot]

# Cheap (text tokens):
"Error on /dashboard page: TypeError: Cannot read property 'map' of undefined
  at DashboardList (dashboard.tsx:42)"
```

**Rule:** One screenshot can cost 1,000-5,000+ tokens. A stack trace is ~100 tokens.

---

### 23. Multi-File Context with Explicit Boundaries

When Claude needs to understand relationships between files, provide explicit boundaries rather than letting it explore.

```
"Refactor the shared types between these 3 files only:
- @src/types/user.ts (source of truth)
- @src/api/user-routes.ts (consumer)  
- @src/components/UserProfile.tsx (consumer)
Do not modify any other files."
```

**Why:** Without explicit boundaries, Claude may read 20+ files to "understand the full picture" — most of which are irrelevant.

---

### 24. Prompt Caching Awareness

Claude Code uses prompt caching automatically. Your CLAUDE.md and system context are cached for ~5 minutes. This means:

- **Rapid successive prompts are cheaper** — the cached prefix isn't re-billed at full rate
- **Sessions idle >5 minutes lose the cache** — consider compacting before stepping away
- **Stable CLAUDE.md = better caching** — frequent edits to CLAUDE.md invalidate the cache

**Practical tip:** Do your thinking and planning before opening Claude, then execute in a focused burst. This maximizes cache hits.

---

### 25. Task Decomposition Strategy

Break large tasks into phases that minimize context carryover.

```
# Phase 1 (Session 1): Design
claude
> /plan design a notification system for @docs/requirements.md
[save the plan to a file]
> /clear

# Phase 2 (Session 2): Implement core
claude  
> implement the notification service per @docs/notification-plan.md

# Phase 3 (Session 3): Implement UI
claude
> build the notification UI components per @docs/notification-plan.md
```

**Why:** Each session starts fresh with only the plan file as context, rather than carrying 50 turns of discussion from previous phases.

---

### 26. /cost - Monitor Token Spend

Check how many tokens you've used in the current session.

```bash
> /cost
```

Run periodically during long sessions. If cost is climbing fast, compact or start a new session.

---

## Tier 5: Commands, Flags & Utilities

### 27. -p (Print Mode) & --bare for Scripts

For quick non-interactive tasks, use print mode. No session overhead, no history.

```bash
# One-shot: no session context loaded
claude -p "explain what @src/utils/cache.ts does" 

# Pipe output directly
claude -p "generate a SQL migration for adding a 'role' column to users" > migration.sql

# Skip local config search for scripted usage (~10x faster startup)
claude -p "prompt" --bare
```

---

### 28. --resume - Continue Previous Sessions

When returning to a previous task, resume instead of re-explaining.

```bash
# Resume the most recent session
claude --resume

# Resume a specific session
claude --resume session-id
```

**Token savings:** Avoids re-stating what you already discussed. The prior compacted context is far cheaper than re-explaining from scratch.

---

### 29. /btw - Side Questions Without Interruption

Ask quick clarifications while Claude works on the primary task. Single-turn, no tool calls — maintains conversation continuity without polluting history.

---

### 30. Voice Input (/voice)

Hold `Space` and dictate prompts naturally. Roughly **3x faster than typing** and spoken prompts naturally include more context than typed ones. Available in CLI (`/voice`), Desktop app (voice button), and via system dictation.

---

### 31. Interview Mode - Ask Before Building

When requirements are unclear, tell Claude to interview you before writing code. It asks targeted questions, then writes a complete spec before execution starts. This is a prompting technique, not a built-in command:

```
> Before writing any code, interview me about the requirements.
  Ask clarifying questions until you fully understand what I need.
```

Or use the **"Grill Me"** skill from Tier 3 for an automated version.

---

### 32. Esc & Esc+Esc - Interrupt and Rollback

- **`Esc` (single):** Stop Claude mid-generation or mid-tool-call. You keep everything generated up to that point. Stops token spend immediately.
- **`Esc+Esc` (double):** Open the checkpoint menu. Roll back file changes to any previous state in the conversation.

---

### 33. /config - Quick Settings Management

Change model, theme, and behavior settings without editing JSON files.

```bash
> /config
```

Useful for toggling between models mid-session, changing notification preferences, or adjusting permissions quickly.

---

### 34. /login & /logout - Account Management

Switch between accounts or organizations without leaving the terminal.

```bash
> /logout
> /login --org my-company
```

Critical for consultants working across multiple client codebases with separate billing.

---

### 35. --allowedTools - Restrict Tool Access

Limit which tools Claude can use to prevent unnecessary file reads and tool calls.

```bash
claude --allowedTools "Read,Edit,Bash(npm test)"
```

**Token savings:** Prevents Claude from running expensive exploratory commands when you know exactly which files matter.

---

### 36. --output-format & --verbose - Programmatic & Debug Use

```bash
# Structured output for scripts/pipelines
claude -p "list all TODO comments" --output-format stream-json

# See what Claude is doing internally (files read, tools called, token counts)
claude --verbose
```

---

### 37. Headless / CI Mode

Run Claude in CI pipelines for automated tasks without interactive input.

```bash
# In GitHub Actions or CI
claude -p "run tests and report failures" --output-format json --model haiku
```

Use Haiku for CI tasks to minimize cost. Reserve Opus for human-interactive sessions.

---

### 38. Environment Variable Injection

Pass dynamic context through environment variables instead of typing it each time.

```bash
export CLAUDE_PROJECT="auth-service"
export CLAUDE_TASK="migration-v2"
```

Reference in CLAUDE.md:
```markdown
Current focus: $CLAUDE_PROJECT / $CLAUDE_TASK
```

---

## Tier 6: Skills for Specific Use Cases

### 39. webapp-testing

Spins up Playwright sessions, navigates flows, captures screenshots. Integrate into Routines for nightly smoke tests without CI configuration.

### 40. PDF / DOCX / PPTX / XLSX

Form filling, field extraction, text/table parsing for documents. Generates genuine Office files preserving styles and handling templates.

### 41. mcp-builder

Generates Model Context Protocol servers from plain descriptions. Bridges Skills to the external tools ecosystem.

### 42. brand-guidelines + theme-factory

Apply organizational color, logo, voice, and typography rules. Generates cohesive themes (light/dark, tokens, variants) as structured JSON for Tailwind, CSS variables, and design tools.

### 43. internal-comms + slack-gif-creator

Templates for announcements, status updates, and incident communications. Even generates on-message animated GIFs for Slack reactions.

---

## Tier 7: Nice-to-Have Extras

### 44. Remote Control & Mobile

Run `/remote-control` to monitor and approve actions from your phone. The iOS/Android app provides full Claude Code access. Use `/teleport` to move sessions between devices seamlessly.

### 45. /branch - Risk-Free Exploration

Fork your conversation to try risky refactors without losing the original path. Both outcomes remain accessible.

### 46. Session Naming & Coloring

Use `/rename` and `/color` to visually distinguish parallel sessions. Prevents mistakes when juggling multiple terminals.

### 47. Permissions Optimization

Run `/permissions` to pre-approve safe commands and check them into `.claude/settings.json`. Recommended alternative to `--dangerously-skip-permissions`. Supports wildcard patterns.

### 48. Two-Session Review Model

Have one Claude implement features and a second Claude review from fresh context — like a staff engineer catching shortcuts the implementer missed.

### 49. Routines for Recurring Automation

Configure once, then trigger on a schedule, via API, or in response to events. Nightly dependency upgrades, auto-triage of GitHub issues, on-merge changelog generation — all become one-time setup.

---

## Quick Reference Card

| Command / Shortcut | Purpose |
|---------------------|---------|
| `/init` | Generate project context |
| `/memory` | Save persistent preferences |
| `/plan` | Enter plan mode |
| `/review` | Pre-commit code review |
| `/ultrareview` | Multi-agent cloud review |
| `/compact` | Compress context |
| `/clear` | Reset session |
| `/batch` | Parallel large migrations |
| `/btw` | Side questions |
| `/voice` | Voice input |
| `/branch` | Fork conversation |
| `/cost` | Check token usage |
| `/config` | Change settings |
| `/login` / `/logout` | Account management |
| `/permissions` | Manage tool permissions |
| `/rename` / `/color` | Label parallel sessions |
| `/remote-control` | Mobile monitoring |
| `/teleport` | Move session between devices |
| `Shift+Tab` | Cycle permission modes |
| `Esc` | Stop mid-action |
| `Esc+Esc` | Checkpoint / rollback menu |
| `--model` | Pick model (haiku/sonnet/opus) |
| `--worktree` | Isolated git worktree session |
| `--resume` | Continue previous session |
| `--bare` | Fast startup, skip config |
| `--allowedTools` | Restrict tool access |
| `--verbose` | Debug mode |
| `--output-format` | Structured output (json) |
| `-p` | Print mode (non-interactive) |

---

## Token Budget Cheat Sheet

| Action | Approx Token Cost | Better Alternative |
|--------|-------------------|-------------------|
| Pasting 200 lines of code | ~800 tokens/turn | Use `@file` reference (~20 tokens) |
| Screenshot of error | 1,000-5,000 tokens | Paste text error (~100 tokens) |
| Vague prompt + exploration | 5,000-15,000 tokens | Precise prompt (~2,000 tokens) |
| 30-turn session without compact | grows to 50,000+ | Compact at turn 15 (~8,000) |
| Re-explaining preferences each session | ~200 tokens/session | CLAUDE.md (cached, ~50 tokens) |
| Full Opus session for simple fix | ~10,000 tokens | Haiku one-shot (~500 tokens) |

---

## The Token-Efficient Workflow

1. **Before opening Claude:** Know exactly what you want. Write it down if needed.
2. **Start session:** Let CLAUDE.md handle the boilerplate context.
3. **First prompt:** Be precise — name files, line numbers, constraints.
4. **Mid-session:** Compact after completing each sub-task.
5. **Switch topics:** `/clear` or start a new session.
6. **Simple tasks:** Use `-p` with Haiku. Don't open a full session.
7. **End of session:** Don't let it idle — cache expires in ~5 minutes.

---

## The Golden Rule

> Slow Claude down just enough to think. Verification, planning, and persistent context are the three pillars. Master those and everything else is a multiplier on top.

---

*Sources:*
- *"I Tried 33 Claude Code Skills. These Are The Best" — The PyCoach, Artificial Corner*
- *"Be 100x More Productive with This Free Claude Code Guide" — Jim Clyde Monge, Generative AI*
- *"I Tried 100 Claude Skills. These Are The Best" — The PyCoach, Artificial Corner*
- *"I Wasted 6 Months Using Claude Code Wrong: 14 Commands That Changed Everything" — Mouez Yazidi, Towards AI*
