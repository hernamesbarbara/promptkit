# Good PM Index

> Quick navigation for your project's specs and issues.

---

## Quick Links

| Resource | Location | Description |
|----------|----------|-------------|
| Contract | [PM_CONTRACT.md](context/PM_CONTRACT.md) | Status vocabulary and conventions |
| Session | [session/current.md](session/current.md) | Current work state and handoff notes |
| Specs | [specs/](specs/) | Specification documents |
| Issues | [issues/](issues/) | Issue files |
| Templates | [templates/](templates/) | Templates for new specs/issues |

---

## Specs

*No specs yet. Create one with:*

```
/good-pm:create-spec <name> "<summary>"
```

---

## Issues

*No issues yet. Break down a spec with:*

```
/good-pm:create-issues .good-pm/specs/SPEC_<name>.md
```

---

## Getting Started

1. **Create a spec:** `/good-pm:create-spec my-feature "Brief description of the feature"`
2. **Review and refine:** Edit `.good-pm/specs/SPEC_my-feature.md` to fill in details
3. **Break into issues:** `/good-pm:create-issues .good-pm/specs/SPEC_my-feature.md`
4. **Track progress:** `/good-pm:issues`

---

*This index is created by `/good-pm:setup`. Update it manually or regenerate with `/good-pm:setup --force`.*
