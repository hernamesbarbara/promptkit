# File Categorization Pattern Reference

Detailed pattern tables for the file-categorization skill.

---

## Phase 1: Directory Patterns

| Pattern | Category |
|---------|----------|
| `test/`, `tests/`, `spec/`, `__tests__/`, `e2e/` | Tests |
| `docs/`, `documentation/`, `references/`, `.github/` | Docs |
| `scripts/`, `bin/`, `tools/` | Scripts |
| `src/`, `lib/`, `pkg/`, `app/`, `core/`, `backend/`, `frontend/` | Source Code |
| `data/`, `datasets/`, `fixtures/`, `samples/` | Data |
| `.claude/`, `.cursor/`, `.aider/`, `prompts/` | AI Tooling |
| `config/`, `conf/`, `.config/`, `.vscode/`, `.github/workflows/` | Config |

**Note:** `.github/` defaults to Docs, but `.github/workflows/` is specifically Config (CI/CD configuration files). The more specific pattern takes precedence.

---

## Phase 1: Filename Patterns

### Config

**Exact matches:**
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `pyproject.toml`, `setup.py`, `setup.cfg`, `MANIFEST.in`
- `requirements.txt`, `Pipfile`, `Pipfile.lock`, `poetry.lock`
- `Gemfile`, `Gemfile.lock`, `Cargo.toml`, `Cargo.lock`
- `go.mod`, `go.sum`, `composer.json`, `composer.lock`
- `tsconfig.json`, `jsconfig.json`, `babel.config.js`
- `webpack.config.js`, `vite.config.js`, `rollup.config.js`
- `Makefile`, `Dockerfile`, `Procfile`, `Vagrantfile`
- `.gitignore`, `.gitattributes`, `.env`, `.env.example`
- `.editorconfig`, `.prettierrc`, `.eslintrc`, `.stylelintrc`
- `tox.ini`, `pytest.ini`, `.coveragerc`, `codecov.yml`

**Pattern matches:**
- `*.config.{js,ts,mjs,cjs,json}`
- `*rc.{js,json,yaml,yml}`
- `.[a-z]+rc` (dotfile rc pattern)
- `*.{toml,ini,cfg}`
- `docker-compose*.{yaml,yml}`
- `requirements*.txt`

### Tests

**Pattern matches:**
- `test_*.py`, `*_test.py`
- `*.test.{js,ts,jsx,tsx}`
- `*.spec.{js,ts,jsx,tsx}`
- `conftest.py`

### Docs

**Exact matches (case-insensitive stem):**
- `README`, `CHANGELOG`, `CONTRIBUTING`, `LICENSE`, `AUTHORS`, `HISTORY`

**Extensions (in docs directories):**
- `.md`, `.rst`, `.txt`, `.adoc`

### Scripts

**Extensions:**
- `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`, `.bat`, `.cmd`

**Content indicator:**
- Shebang line: `#!/...`

### Source Code

**Extensions:**
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`, `.mjs`, `.cjs`
- Go: `.go`
- Rust: `.rs`
- Java/Kotlin/Scala: `.java`, `.kt`, `.scala`
- Ruby: `.rb`
- C/C++: `.c`, `.cpp`, `.cc`, `.h`, `.hpp`
- Swift/Objective-C: `.swift`, `.m`, `.mm`
- C#/F#: `.cs`, `.fs`
- Elixir: `.ex`, `.exs`
- Haskell/ML: `.hs`, `.ml`
- Other: `.elm`, `.vue`, `.svelte`, `.php`, `.clj`

### Data

**Extensions:**
- Tabular: `.csv`, `.tsv`, `.parquet`, `.arrow`, `.feather`
- Databases: `.sqlite`, `.db`, `.sql`
- Structured: `.json`, `.xml`, `.yaml`, `.yml`
- Binary: `.pickle`, `.pkl`, `.npy`, `.npz`, `.h5`, `.hdf5`

**Note:** Root-level `.json`/`.yaml` files default to Config; use `data/` directory for Data.

### AI Tooling

**Exact matches:**
- `SKILL.md`, `CLAUDE.md`, `.cursorrules`, `.cursorignore`

**Pattern matches:**
- `.aider*`
- `*.prompt`, `*.prompt.md`

---

## Schema & Specification Files

These files describe structure rather than contain data — classify as **Docs**:

| Pattern | Category | Reasoning |
|---------|----------|-----------|
| `schema.json`, `*.schema.json` | Docs | Pydantic/JSON Schema definitions |
| `openapi.json`, `openapi.yaml` | Docs | API specifications |
| `swagger.json`, `swagger.yaml` | Docs | API specifications |
| `*.graphql`, `schema.graphql` | Docs | GraphQL schema |
| `sql/schema.sql`, `**/schema.sql` | Docs | Database DDL |
| `*.proto` | Docs | Protocol buffer definitions |
| `tsconfig.json`, `jsconfig.json` | Config | Already handled as config |

**Why Docs, not Data?** Schema files are *documentation of structure*. They tell you what shape data
takes, but don't contain the data itself. When someone asks "find the schema," they want documentation,
not a dataset.

---

## Phase 2: Frontmatter Indicators

### Config Indicators
```yaml
settings:
version:
env:
paths:
database:
```

### AI Tooling Indicators
```yaml
name:
description:
allowed-tools:
model:
prompt:
```

### Docs Indicators
```markdown
# Overview
# Introduction
# Getting Started
# Usage
# API Reference
```

---

## Phase 3: Content Structure Signals

| Category | Content Signals |
|----------|-----------------|
| **Tests** | `assert`, `expect(`, `pytest`, `unittest.TestCase`, `describe(`, `it(`, `beforeEach`, `afterEach` |
| **Scripts** | `argparse`, `click`, `sys.argv`, `if __name__ == "__main__"`, CLI parsers |
| **Source Code** | `class`, `def`, `function`, `import`, `from ... import`, `export`, `module.exports` |
| **Docs** | Heading hierarchy, prose paragraphs, no executable code blocks |
| **Data** | JSON arrays/objects, CSV rows, numeric columns, structured records |
| **AI Tooling** | "sub-agent", "handoff", "allowed-tools", "system prompt", "workflow" |

---

## Phase 4: Keyword Detection

| Category | Keywords |
|----------|----------|
| **Config** | config, settings, workspace, lint, dependencies, environment |
| **Tests** | fixtures, assert, mock, unit test, integration, coverage |
| **Docs** | guide, overview, tutorial, how to, best practices, documentation |
| **Scripts** | usage:, examples:, run:, startup, entrypoint, main |
| **Source Code** | class, def, function, import, export, module |
| **Data** | id, name, value, records, rows, columns |
| **AI Tooling** | skill, agent, prompt, workflow, Claude, assistant |
