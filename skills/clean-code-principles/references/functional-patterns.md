# Functional Patterns — Reference

Applicable to any language (Python, TypeScript, Go, Rust, Java, etc.) that supports
first-class functions.

---

## Core Concepts

### Pure Functions
```
input → [pure function] → output
```
No reads from external state. No writes to external state. Deterministic.

**Benefits:** trivially testable, safe to memoize, safe to parallelize, composable.

### Function Composition
Combine small functions into larger pipelines. The output of one function is the input to the next.

```
result = transform_c(transform_b(transform_a(raw_input)))
# Or with a pipe utility:
result = pipe(raw_input, transform_a, transform_b, transform_c)
```

Each transformation is independently testable. The pipeline is readable as a sequence of named steps.

### Map / Filter / Reduce
Prefer declarative collection transformations over stateful loops.

- `map(fn, collection)` — transform each element
- `filter(predicate, collection)` — select elements matching a condition
- `reduce(fn, collection, initial)` — aggregate into a single value

These communicate *intent* clearly; a `for` loop communicates *mechanism*.

### Higher-Order Functions
Functions that accept functions as arguments or return functions. This is the functional equivalent
of the Strategy and Decorator patterns.

```python
def apply_discount(discount_fn, price):
    return discount_fn(price)
```

### Partial Application / Currying
Fix some arguments of a function to produce a more specific function. Useful for creating
specialized versions of generic functions without repeating parameters.

---

## Immutability Patterns

**Prefer:** creating new data structures over mutating existing ones.

```python
# Mutable (fragile)
def add_item(cart, item):
    cart.items.append(item)  # mutates caller's data

# Immutable (safe)
def add_item(cart, item):
    return Cart(items=[*cart.items, item])  # returns new object
```

When mutation is necessary (performance-critical inner loops), isolate it. Do not let mutable
state escape the function boundary.

---

## Functional Core / Imperative Shell

The most practical application of FP in non-functional languages:

```
┌──────────────────────────────────────────┐
│  Imperative Shell                        │
│  (I/O, side effects, state, DB, HTTP)    │
│  ┌──────────────────────────────────┐    │
│  │  Functional Core                 │    │
│  │  (business logic, pure, tested)  │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

1. Read inputs at the shell.
2. Pass data to the pure functional core for processing.
3. Return results to the shell for output / persistence.

The core is pure and fully testable without mocks. The shell is thin and straightforward to audit.

---

## Error Handling — Functional Style

Prefer explicit error types over exceptions for expected failures.

**Result / Either types:**
```
Ok(value) | Err(error)   # Rust: Result<T, E>
Right(value) | Left(error) # Haskell convention
```

This forces callers to handle the error case explicitly rather than hoping for an exception catch.

**Railway-oriented programming:** chain operations that may fail; short-circuit on the first error;
the happy path is uncluttered.

---

## When NOT to Use Functional Patterns

- Performance-critical loops where immutable copies are prohibitively expensive.
- Stateful protocols (sockets, file handles) — model them explicitly as stateful, not as pure functions.
- Excessive abstraction: a simple `for` loop is sometimes clearer than a chain of `map`/`filter`.
- Team unfamiliarity: introducing FP idioms in a codebase without team buy-in creates confusion.
