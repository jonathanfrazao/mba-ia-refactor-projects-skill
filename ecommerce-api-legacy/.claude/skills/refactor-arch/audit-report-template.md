# Audit Report Template

Use this exact format when generating the Phase 2 report. Fill every field — never omit evidence or leave recommendations vague.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project:   <project directory name>
Stack:     <Language> + <Framework>
Files:     <N analyzed> | ~<LOC> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
Total findings: <N>

## Findings

### [CRITICAL] <Short descriptive title>
File:           <relative/path/to/file.ext>:<start_line>-<end_line>
Category:       <Security | Architecture | Quality | Deprecated API | Performance>
Description:    <One clear sentence stating what the problem is.>
Evidence:       <Exact code snippet (3–8 lines) showing the problem.>
Impact:         <Concrete consequence if not fixed.>
Recommendation: <Specific action to take — reference PT-XX from playbook when applicable.>

### [CRITICAL] <Short descriptive title>
File:           <relative/path/to/file.ext>:<start_line>-<end_line>
Category:       <Security | Architecture | Quality | Deprecated API | Performance>
Description:    <...>
Evidence:       <...>
Impact:         <...>
Recommendation: <...>

### [HIGH] <Short descriptive title>
File:           <...>
...

### [HIGH] <Short descriptive title>
...

### [MEDIUM] <Short descriptive title>
...

### [MEDIUM] <Short descriptive title>
...

### [LOW] <Short descriptive title>
...

### [LOW] <Short descriptive title>
...

================================
Total: <N> findings
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Field Definitions

| Field | Requirement |
|-------|-------------|
| **Project** | Directory name as found on disk |
| **Stack** | Language + framework with version if detectable |
| **Files** | Count of `.py` or `.js` files read during analysis |
| **LOC** | Approximate total lines of code |
| **File** | Relative path from project root + colon + line range |
| **Category** | Exactly one of: Security, Architecture, Quality, Deprecated API, Performance |
| **Description** | One sentence. Must name the specific pattern, not a generic statement. |
| **Evidence** | A code snippet of 3–8 lines copied verbatim from the file, with the problematic line visible. Use fenced code block. |
| **Impact** | Concrete consequence (data loss, auth bypass, performance degradation). Not "bad practice." |
| **Recommendation** | Specific and actionable. Reference PT-XX from the refactoring playbook when a matching pattern exists. |

---

## Ordering Rules

1. Sort findings from most severe to least: CRITICAL → HIGH → MEDIUM → LOW
2. Within the same severity, order by impact (security issues before architecture before quality)
3. Never skip a severity level present in the project — report all findings found

---

## Minimum Requirements

The report is complete only when it contains:
- At least **1 CRITICAL or HIGH** finding
- At least **2 MEDIUM** findings
- At least **2 LOW** findings
- **5 findings minimum** total
- Every finding has a non-empty Evidence block with actual code from the project
- Every finding's File field contains the exact relative path and line range

---

## Example Finding (filled)

```
### [CRITICAL] SQL Injection via string concatenation
File:           models.py:28
Category:       Security
Description:    Product lookup query is built by concatenating the user-supplied id
                parameter directly into the SQL string without parameterization.
Evidence:
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
Impact:         Any request to GET /produtos/<id> can extract, modify or destroy
                arbitrary database records via SQL injection.
Recommendation: Replace with parameterized query (PT-01):
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```
