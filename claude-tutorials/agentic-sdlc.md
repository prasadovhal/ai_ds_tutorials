# Agentic SDLC

AI agents assist or drive every phase of software development — from planning to monitoring.

---

## Syllabus Coverage

| # | Phase | What AI Does |
|---|-------|-------------|
| 1 | Requirements | Gathers, clarifies, and writes specs |
| 2 | Design | Proposes architecture and data models |
| 3 | Implementation | Generates, completes, and refactors code |
| 4 | Testing | Creates tests, finds bugs, suggests fixes |
| 5 | Code Review | Reviews PRs, flags issues, enforces standards |
| 6 | Deployment | Automates CI/CD, infra-as-code, rollbacks |
| 7 | Monitoring | Analyzes logs, detects anomalies, suggests fixes |
| 8 | Maintenance | Triages bugs, updates deps, refactors debt |

---

## Step-by-Step with Examples

### Step 1 — Requirements Gathering

**What happens:** AI agent reads raw input (user stories, tickets, conversations) and produces structured requirements.

**Example:**

```
You say:  "I need a todo app with login"

Agent outputs:
  - FR-1: User registration with email/password
  - FR-2: User login/logout
  - FR-3: Create, read, update, delete todos
  - FR-4: Each user sees only their own todos
  - NFR-1: Passwords hashed with bcrypt
  - NFR-2: Response time < 200ms
```

---

### Step 2 — System Design

**What happens:** Agent proposes architecture, picks tech stack, and designs data models based on requirements.

**Example:**

```
Agent outputs:
  Architecture: React frontend + Node/Express API + PostgreSQL
  
  Table: users
    id | email | password_hash | created_at

  Table: todos
    id | user_id (FK) | title | done | created_at

  API Routes:
    POST   /auth/register
    POST   /auth/login
    GET    /todos
    POST   /todos
    PATCH  /todos/:id
    DELETE /todos/:id
```

---

### Step 3 — Implementation (Code Generation)

**What happens:** Agent writes functional code from the design. It generates files, handles boilerplate, and follows patterns.

**Example:**

```
You say:  "Create the todo model and CRUD routes"

Agent generates:
  src/models/todo.js       → Sequelize model
  src/routes/todos.js      → Express CRUD routes
  src/middleware/auth.js    → JWT auth middleware
```

```javascript
// Agent-generated route
router.get('/todos', auth, async (req, res) => {
  const todos = await Todo.findAll({ where: { userId: req.user.id } });
  res.json(todos);
});
```

---

### Step 4 — Testing

**What happens:** Agent generates unit tests, integration tests, and edge cases. It can also run them and fix failures.

**Example:**

```
Agent generates: tests/todos.test.js

  ✓ returns empty list for new user
  ✓ creates a todo successfully
  ✓ prevents access to another user's todos
  ✓ returns 401 without auth token
  ✓ handles missing title with 400 error
```

```javascript
// Agent-generated test
test('prevents access to other user todos', async () => {
  const res = await request(app)
    .get('/todos')
    .set('Authorization', `Bearer ${userBToken}`);
  expect(res.body).not.toContainEqual(
    expect.objectContaining({ userId: userA.id })
  );
});
```

---

### Step 5 — Code Review

**What happens:** Agent reviews pull requests — checks for bugs, security issues, style violations, and performance problems.

**Example:**

```
Agent reviews PR #42 and comments:

  ⚠ Line 15: SQL injection risk — use parameterized query
  ⚠ Line 38: Missing input validation on `title` (can be empty string)
  ℹ Line 52: Consider adding an index on `user_id` for faster lookups
  ✓ Auth middleware correctly verifies JWT
```

---

### Step 6 — Deployment

**What happens:** Agent generates CI/CD pipelines, Dockerfiles, and infrastructure config. It can trigger deploys and handle rollbacks.

**Example:**

```
You say:  "Set up CI/CD for this project"

Agent generates:

  Dockerfile
  docker-compose.yml
  .github/workflows/deploy.yml
    → on push to main:
       1. Run tests
       2. Build Docker image
       3. Push to registry
       4. Deploy to AWS ECS
       5. Run health check
       6. Rollback if health check fails
```

---

### Step 7 — Monitoring & Incident Response

**What happens:** Agent watches logs, metrics, and alerts. When something breaks, it diagnoses the root cause and suggests a fix.

**Example:**

```
Alert: 500 errors spiking on POST /todos

Agent analyzes:
  → Error: "column 'titl' does not exist"
  → Root cause: typo in migration #12 (titl instead of title)
  → Fix: generate corrective migration renaming column
  → Action: opens PR #51 with the fix
```

---

### Step 8 — Maintenance & Evolution

**What happens:** Agent triages bug reports, upgrades dependencies, refactors tech debt, and implements new features using the same cycle.

**Example:**

```
Agent weekly report:
  - 3 dependencies have security patches → PR #55 (auto-update)
  - Dead code detected in src/utils/old.js → PR #56 (cleanup)
  - Bug #89 "todo date wrong in UTC" → PR #57 (timezone fix)
  - Feature request "add due dates" → drafted requirements, awaiting approval
```

---

## Traditional SDLC vs Agentic SDLC

| Aspect | Traditional | Agentic |
|--------|------------|---------|
| Requirements | Humans write docs | Agent drafts, human approves |
| Coding | Humans write all code | Agent generates, human reviews |
| Testing | Humans write tests | Agent generates and runs tests |
| Review | Human reviewers only | Agent flags issues + human review |
| Deploy | Manual or scripted | Agent manages full pipeline |
| Monitoring | Humans read dashboards | Agent detects and responds |
| Speed | Weeks to months | Days to weeks |
| Human role | Doer | Supervisor and decision-maker |

---

## Key Takeaway

> In Agentic SDLC, **humans shift from doing to directing**. The AI agent handles repetitive, mechanical work across every phase. Humans focus on decisions, approvals, and creative problem-solving. The loop is: **Agent proposes → Human approves → Agent executes**.
