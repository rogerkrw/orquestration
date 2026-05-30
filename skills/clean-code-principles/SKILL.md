---
name: clean-code-principles
description: >
  Universal software engineering principles for writing minimal, clean, functional, and bug-resistant code.
  Use this skill whenever the task involves writing new code, reviewing existing code, refactoring, identifying
  code smells, discussing software design, debating naming conventions, or applying principles like DRY, KISS,
  YAGNI, SOLID, functional programming patterns, defensive programming, or fail-fast strategies.
  Also trigger when the user asks how to "improve", "simplify", "clean up", "make more robust", or "reduce bugs"
  in any codebase — regardless of language. This skill is language-agnostic: principles apply universally
  to Python, TypeScript, Go, Java, Rust, or any other language.
---

# Clean Code Principles

Language-agnostic principles for writing code that is minimal, readable, correct, and maintainable.
The cardinal rule: **code is read far more often than it is written — optimize for the reader, not the writer.**

---

## Tier 1 — Foundations (always apply)

### DRY — Don't Repeat Yourself
Every piece of knowledge or logic has exactly one authoritative representation. Duplication is not just
redundant lines — it's divergent knowledge. When the same logic lives in two places, they will inevitably
diverge. Extract the abstraction; let it have a single home.

**Anti-pattern:** copy-paste with minor variations.
**Correct:** a single function/module/constant that is composed or parameterized.

> ⚠️ DRY can conflict with KISS. Premature abstraction is worse than duplication. Extract only when the
> pattern is stable and the abstraction earns its complexity.

---

### KISS — Keep It Simple
The simplest solution that correctly solves the problem is the best solution. Complexity is a liability,
not a feature. Every abstraction, indirection, and generalization adds cognitive load. Add them only when
they pay for themselves.

**Test:** "Would a new team member understand this in 30 seconds?" If not, simplify.

---

### YAGNI — You Aren't Gonna Need It
Implement features when they are concretely required — not when you anticipate needing them. Speculative
code is debt: it must be maintained, tested, and understood even if it is never used.

**Rule:** never write code for a requirement that does not exist today.

---

### Single Responsibility
Every unit of code (function, class, module, service) should have one reason to change. If you can
describe what a function does and the description contains the word "and", it is doing too much.

A function that validates input *and* transforms it *and* persists it *and* sends an email is four
functions. Split them.

---

### Intention-Revealing Names
Names are the primary documentation. A well-named function eliminates the need for comments.

- Variables: what it contains (`userEmail`, not `e` or `data`)
- Functions: what they do, using a verb (`calculateDiscount`, not `process`)
- Booleans: a predicate (`isAuthenticated`, `hasPermission`)
- Avoid abbreviations, single letters (except loop counters), and generic names (`manager`, `handler`, `util`)

**Stepdown rule:** code should read top-to-bottom — high-level summary first, implementation details below.

---

## Tier 2 — Structure (apply when designing modules or classes)

### SOLID Principles

**S — Single Responsibility:** one reason to change (see above).

**O — Open/Closed:** open for extension, closed for modification. Add behavior by composing or extending,
not by editing existing, tested code.

**L — Liskov Substitution:** subtypes must be substitutable for their base type without altering program
correctness. If your subclass overrides a method and breaks callers' assumptions, the hierarchy is wrong.

**I — Interface Segregation:** clients should not be forced to depend on methods they do not use.
Prefer many small, focused interfaces over one fat interface.

**D — Dependency Inversion:** depend on abstractions, not on concrete implementations. High-level
policy should not know about low-level details. Inject dependencies; don't hardcode them.

> SOLID is most applicable in OOP contexts. In functional or procedural code, the same intent maps to:
> small pure functions, composable modules, and injected dependencies.

---

### Separation of Concerns
Business logic, I/O, persistence, presentation, and configuration are distinct concerns and must not
be entangled. Mixing them creates code that is hard to test, hard to change, and hard to understand.

**Functional core / imperative shell:** keep the business logic pure and side-effect-free; push I/O,
state mutation, and external calls to the outermost shell.

---

### Law of Demeter (Principle of Least Knowledge)
A unit of code should only talk to its immediate collaborators. Avoid chains like `a.getB().getC().doSomething()`.
Each dot is a dependency on internals you should not know about.

---

### Composition Over Inheritance
Prefer composing small, focused units over deep inheritance hierarchies. Inheritance couples
tightly; composition is flexible and testable.

---

## Tier 3 — Functional Principles (apply regardless of language paradigm)

These principles from functional programming improve correctness and testability in *any* language.

### Pure Functions
A pure function: (1) always returns the same output for the same input, and (2) has no side effects.
Pure functions are trivially testable, cacheable, and safe to parallelize.

**Strive for a pure functional core.** Move I/O, mutation, and non-determinism (time, randomness,
network) to the edges of the system.

---

### Immutability by Default
Treat data as immutable unless mutation is explicitly necessary. Prefer creating new values over
modifying existing ones. Immutable data eliminates a class of bugs (unexpected mutation, race conditions)
and makes state changes explicit and traceable.

---

### Avoid Hidden Side Effects
A function that modifies global state, writes to disk, sends an email, or alters its arguments while
appearing to just return a value is a trap. Side effects are necessary — but they must be explicit,
expected, and isolated.

---

### Referential Transparency
An expression is referentially transparent if it can be replaced with its value without changing
program behavior. Aim for this property in core logic. Code that relies on hidden state or context
is harder to reason about.

---

### Declarative Over Imperative
Describe *what* you want, not *how* to get it. Map/filter/reduce over explicit loops; named
predicates over inline conditions; data pipelines over stateful iteration. Declarative code is
more readable and less error-prone.

---

## Tier 4 — Robustness (apply when handling errors, inputs, and boundaries)

### Fail Fast
Detect invalid conditions as early as possible and fail loudly with a clear message. Do not
silently swallow errors or return ambiguous defaults. An error that surfaces immediately at the
boundary is cheaper to fix than one that propagates and corrupts state silently downstream.

**Validate inputs at entry points.** Return early / raise exceptions before doing real work.

---

### Defensive Programming
Assume that data from outside your control boundary (user input, API responses, file contents,
inter-service calls) is potentially invalid. Validate before processing. Design-by-contract:
specify preconditions, postconditions, and invariants. Use assertions for internal invariants
that "should never happen."

**Calibrate paranoia:** do not defensively program internal calls between your own well-tested
functions — excess defensive code obscures the main path and makes errors harder to trace.

---

### Explicit Error Handling
Errors are not second-class citizens. Handle them at the right level of abstraction. Do not
catch generic exceptions that swallow specific failure information. Do not use error codes that
callers can ignore — prefer types or exceptions that force acknowledgment. Standardize error
handling strategy across the codebase and be consistent.

---

### Single Source of Truth
Every piece of configuration, constant, schema, or business rule lives in exactly one place.
Scatter magic numbers or repeated literals and they will diverge. Extract to named constants,
config files, or canonical modules.

---

## Tier 5 — Code Quality Heuristics

### Functions

- Do one thing at one level of abstraction.
- Prefer few arguments (0–2 ideal; 3 is a smell; 4+ almost always needs a refactor).
- Avoid output arguments — return values instead of mutating parameters.
- Short is better than long, but not at the cost of clarity. Do not enforce arbitrary line limits.

### Comments

- Good code is self-documenting. Comments explain *why*, not *what*.
- A comment that describes *what* the code does is a sign the code needs to be renamed or refactored.
- Never leave commented-out code in commits — use version control for history.

### Tests

- Tests are first-class code, subject to the same quality standards.
- Follow FIRST: Fast, Independent, Repeatable, Self-validating, Timely.
- One behavior per test. Name tests to describe the behavior under test, not the function name.
- A test coupled to implementation (breaks when internals change but behavior is preserved) is a bad test.
- Write tests before fixing bugs: the test reproduces the bug; the fix makes it green.

### Complexity

- Cyclomatic complexity (number of independent paths through a function) should be low. If a function
  has more than ~5–7 branches, decompose it.
- Avoid deep nesting. Early returns (guard clauses) flatten structure and clarify intent.
- Avoid over-engineering: the right abstraction at the wrong time is the wrong abstraction.

### Boy Scout Rule
Leave every piece of code you touch slightly cleaner than you found it. Not perfect — slightly cleaner.
Rename a confusing variable. Extract a duplicated block. Remove a dead comment. Compound interest
of small improvements is real.

---

## Anti-Patterns to Recognize and Eliminate

| Smell | Meaning | Fix |
|---|---|---|
| Long function | Too many responsibilities | Decompose |
| Deep nesting | Complex control flow | Guard clauses, extract functions |
| Magic numbers/strings | No context for values | Named constants |
| Shotgun surgery | One change touches many files | Collocate related concerns |
| Feature envy | Function uses another module's data excessively | Move it there |
| Dead code | Unreachable or unused code | Delete it |
| God class/function | One unit does everything | Split by responsibility |
| Primitive obsession | Using raw strings/ints for domain concepts | Domain types/value objects |
| Inconsistent naming | Same concept named differently across codebase | Ubiquitous language |
| Hidden coupling | Units depend on each other's internals | Decouple via interfaces/abstractions |

---

## Guiding Questions for Code Review

1. Can I understand what this does in under 30 seconds?
2. Is there any duplicated logic that should be extracted?
3. Does each function do exactly one thing?
4. Are all names intention-revealing?
5. Are side effects visible, not hidden?
6. Does this code fail fast on invalid input?
7. Is there any code that doesn't need to exist yet (YAGNI)?
8. If I change this, what else breaks? (coupling indicator)
9. Is the error handling consistent and explicit?
10. Would a new team member understand this without asking?

---

## Reference Hierarchy

Load the relevant reference file when the task requires deep detail on a specific domain:

- `references/solid-principles.md` — detailed SOLID examples and when NOT to apply
- `references/functional-patterns.md` — composition, monads, algebraic types, pipeline patterns
- `references/testing-guide.md` — TDD, test architecture, mocking strategy
- `references/naming-guide.md` — naming rules by entity type with examples
- `references/code-smells.md` — extended catalog with refactoring recipes

> These files are loaded on demand — do not pre-load them. Only read the one(s) needed for the current task.
