# Code Smells — Extended Catalog with Refactoring Recipes

Smells are surface symptoms of deeper structural problems. They do not always indicate a bug,
but they reliably indicate a maintenance liability.

---

## Function-Level Smells

### Long Method
**Symptom:** Function exceeds ~20–30 lines or does more than one thing.
**Recipe:** Extract Method — identify cohesive blocks and name them.

### Too Many Parameters
**Symptom:** 4+ parameters. Callers cannot remember argument order.
**Recipe:** Introduce Parameter Object (group related params into a struct/dataclass/dict).

### Flag Arguments
**Symptom:** `process(data, is_dry_run=True)` — boolean controls radically different behavior.
**Recipe:** Split into two functions: `process(data)` and `preview(data)`.

### Nested Conditionals
**Symptom:** 3+ levels of `if/else` nesting.
**Recipe:** Guard clauses (return early on invalid/edge cases); extract to named predicates.

### Dead Code
**Symptom:** Commented-out code, unreachable branches, unused variables, obsolete functions.
**Recipe:** Delete. Version control preserves history.

---

## Class/Module-Level Smells

### God Class / God Module
**Symptom:** One class knows too much and does too much. Hundreds of methods. Everyone imports it.
**Recipe:** Extract Class; apply SRP; identify sub-responsibilities and collocate them.

### Feature Envy
**Symptom:** Method uses data from another class more than its own.
**Recipe:** Move Method to the class whose data it uses.

### Data Clumps
**Symptom:** The same group of fields always appears together (e.g., `city`, `state`, `zip`).
**Recipe:** Extract into a named type (`Address`).

### Primitive Obsession
**Symptom:** Using raw strings/ints/dicts to represent domain concepts (`"USD"`, `42.0`, `{"role": "admin"}`).
**Recipe:** Introduce domain types: `Currency`, `Money`, `UserRole`. Gives you a single place for
validation and behavior.

### Divergent Change
**Symptom:** One class changes for many different reasons (one time for a new DB, next for a new API).
**Recipe:** Split by reason-to-change (SRP).

### Shotgun Surgery
**Symptom:** One conceptual change requires edits to many different files/classes.
**Recipe:** Move related logic together. Collocate what changes together.

---

## Architecture-Level Smells

### Hidden Coupling / Inappropriate Intimacy
**Symptom:** Module A depends on private internals of Module B.
**Recipe:** Introduce an interface or facade; enforce module boundaries.

### Circular Dependencies
**Symptom:** A depends on B, B depends on A.
**Recipe:** Extract a third module C that both A and B depend on; or invert the dependency via an interface.

### Leaky Abstractions
**Symptom:** A high-level module exposes implementation details of the lower-level module it wraps.
**Recipe:** Redesign the interface to expose only the operation, not the mechanism.

### Magic Numbers and Strings
**Symptom:** `if status == 3:` or `url = "https://api.internal/v2/users"`.
**Recipe:** Named constants. Configuration. Enumerations.

---

## Testing Smells

### Test Coupled to Implementation
**Symptom:** Test breaks when internal structure changes but observable behavior is unchanged.
**Recipe:** Test behavior (inputs → outputs), not implementation (method calls, internal state).

### Slow Tests
**Symptom:** Unit tests hit the database, filesystem, or network.
**Recipe:** Inject dependencies; use in-memory fakes or mocks for I/O.

### Fragile / Flaky Tests
**Symptom:** Test passes sometimes, fails other times, with no code change.
**Recipe:** Eliminate non-determinism (time, randomness, external calls). Each test must be fully deterministic.

### Assert-Nothing Test
**Symptom:** Test runs code but asserts nothing meaningful (or nothing at all).
**Recipe:** Define what the correct behavior is and assert it explicitly.

---

## Quick Reference

| Smell | Root Cause | Primary Recipe |
|---|---|---|
| Long method | Too many responsibilities | Extract Method |
| Too many params | Missing abstraction | Parameter Object |
| Nested conditionals | Complex control flow | Guard clauses |
| Dead code | Over-engineering or leftover | Delete |
| God class | No SRP | Extract Class |
| Feature envy | Wrong home for the logic | Move Method |
| Primitive obsession | Missing domain model | Introduce Value Object |
| Shotgun surgery | Scattered responsibility | Move & collocate |
| Magic values | No named concept | Named constants / enums |
| Circular dependency | Architectural tangle | Extract shared module |
