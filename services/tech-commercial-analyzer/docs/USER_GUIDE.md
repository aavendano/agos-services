# User & Operator Guide

## 1. Installation & Environment

The analyzer is pre-installed in the AA Digital Business environment. You can run `tech-eval` from any terminal session.

```bash
which tech-eval
# Output: /home/alejandro/.local/bin/tech-eval
```

---

## 2. Common Workflows

### 2.1 Viewing Portfolio Overview
```bash
tech-eval list
```

### 2.2 Evaluating a Single Asset
```bash
tech-eval analyze agos-logic-solver
```
Outputs:
- Composite Commercial Score
- Multi-dimensional dimension breakdown
- 5-Year financial trajectory table
- Monte Carlo confidence distribution (P10, P50, P90)
- SWOT & Recommended Next Steps

### 2.3 Comparing the Entire Portfolio
```bash
tech-eval compare
```

### 2.4 Exporting Executive Memos
```bash
tech-eval export --format markdown --output /tmp/executive_memo.md
```

### 2.5 Launching the Web UI
```bash
tech-eval serve --port 8080
```
Navigate to `http://localhost:8080` to interact with charts and what-if parameter sliders.
