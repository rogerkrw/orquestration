# SOLID Principles — Reference

## S — Single Responsibility Principle (SRP)

**Statement:** A class/module should have one, and only one, reason to change.

**Practical test:** List the actors (stakeholders) who can require a change to this unit. If there is
more than one, the unit has more than one responsibility.

**Common violation:** `UserService` that authenticates, fetches user data, sends emails, and formats
output for the API. Each of those is a separate reason to change.

**When NOT to apply:** Micro-splitting creates shotgun surgery (one change → many files). Group things
that genuinely change together. SRP is about *reasons to change*, not about line count.

---

## O — Open/Closed Principle (OCP)

**Statement:** Software entities should be open for extension, closed for modification.

**Practical application:**
- Strategy pattern: inject behavior instead of branching on type.
- Plugin/hook architectures: extend by adding, not editing.
- Avoid `if type == "A" ... elif type == "B"` chains that must be edited for every new type.

**When NOT to apply:** OCP adds indirection. In small, stable domains, a simple switch is cleaner
than a strategy hierarchy. Apply OCP where you have proven variability.

---

## L — Liskov Substitution Principle (LSP)

**Statement:** If S is a subtype of T, objects of type T may be replaced with objects of type S
without altering program correctness.

**Practical test:** Can every caller of the base type use the subtype without knowing it? If
subtype methods throw unexpected exceptions, return narrower types, or violate the base class's
postconditions, LSP is violated.

**Common violation:** `Square extends Rectangle` — a Square cannot honor Rectangle's invariant
that width and height are independently settable.

---

## I — Interface Segregation Principle (ISP)

**Statement:** Clients should not be forced to depend on interfaces they do not use.

**Practical application:** Split fat interfaces into role-specific ones. A `Printer` that must
implement `scan()` and `fax()` to satisfy a large `IMultiFunctionDevice` interface violates ISP
if the printer does not scan or fax.

**When NOT to apply:** In dynamic languages with duck typing, formal interfaces may not exist.
Apply the intent: don't force callers to depend on methods they don't use.

---

## D — Dependency Inversion Principle (DIP)

**Statement:** High-level modules should not depend on low-level modules. Both should depend on
abstractions. Abstractions should not depend on details.

**Practical application:** Inject dependencies rather than instantiating them. The business logic
layer should not `import` a specific database driver — it should depend on a `Repository` interface.
The concrete driver is injected at runtime (in tests: a mock; in production: the real driver).

**Benefits:** Makes units testable in isolation. Allows swapping implementations without touching
business logic.

---

## Mapping SOLID to Functional Programming

| SOLID Principle | Functional Equivalent |
|---|---|
| Single Responsibility | One function, one transformation |
| Open/Closed | Higher-order functions; compose new behavior |
| Liskov Substitution | Function signatures as contracts |
| Interface Segregation | Small, focused function signatures |
| Dependency Inversion | Pass functions as arguments (dependency injection) |
