# Python Dunder Method Cheatsheet

Quick reference for the Python Dunder Enforcer skill.

---

## Always Implement

| Method | Purpose | Template |
|--------|---------|----------|
| `__repr__` | Developer representation | `f"{self.__class__.__name__}(attr={self.attr!r})"` |
| `__str__` | User-friendly display | Human-readable format |

---

## Implement When Appropriate

### Comparison (with `@total_ordering`)

```python
from functools import total_ordering

@total_ordering
class MyClass:
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.value < other.value
```

### Arithmetic

```python
def __add__(self, other: Any) -> "MyClass":
    """Add two instances."""
    if not isinstance(other, MyClass):
        return NotImplemented
    return MyClass(self.value + other.value)
```

### Container-Like (only if semantically a collection)

| Method | Usage | When to Implement |
|--------|-------|-------------------|
| `__len__` | `len(obj)` | Object has countable items |
| `__getitem__` | `obj[key]` | Object supports indexing |
| `__iter__` | `for x in obj` | Object is iterable |
| `__contains__` | `x in obj` | Membership testing makes sense |

### Context Manager (only if manages resources)

```python
def __enter__(self) -> "MyClass":
    """Acquire resource."""
    return self

def __exit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
) -> bool:
    """Release resource. Return False to propagate exceptions."""
    self.cleanup()
    return False  # Don't swallow exceptions
```

---

## Never Implement

### Forbidden Categories

| Category | Methods |
|----------|---------|
| Object Lifecycle | `__new__`, `__del__` |
| Class Creation | `__init_subclass__`, `__class_getitem__`, `__prepare__`, `__mro_entries__` |
| Pickling | `__getstate__`, `__setstate__`, `__reduce__`, `__reduce_ex__`, `__getnewargs__`, `__getnewargs_ex__` |
| Async Protocol | `__await__`, `__aiter__`, `__anext__`, `__aenter__`, `__aexit__` |
| Descriptors | `__get__`, `__set__`, `__delete__`, `__set_name__` |
| Attribute Access | `__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__` |
| Identity | `__hash__` (unless immutable), `__bool__` (unless unambiguous) |

---

## Return Value Patterns

### For Type Mismatches

```python
# GOOD: Return NotImplemented
def __eq__(self, other: Any) -> bool:
    if not isinstance(other, MyClass):
        return NotImplemented  # Let Python try other.__eq__(self)
    return self.value == other.value

# BAD: Raise or return False
def __eq__(self, other: Any) -> bool:
    if not isinstance(other, MyClass):
        return False  # Prevents reverse comparison
    return self.value == other.value
```

### For __repr__ and __str__

```python
# GOOD: Unambiguous, recreatable
def __repr__(self) -> str:
    return f"Temperature(celsius={self.celsius!r})"

# GOOD: User-friendly
def __str__(self) -> str:
    return f"{self.celsius}°C"

# BAD: Ambiguous
def __repr__(self) -> str:
    return str(self.celsius)  # Is this Temperature? int? float?
```

---

## Subclass Rules

1. **Call `super()`** when overriding
2. **Extend, don't replace** `__repr__`/`__str__`
3. **Don't change** equality/container/hashing semantics
4. **Use `UserDict`/`UserList`** instead of `dict`/`list`
5. **When unsure**, don't override

```python
# GOOD: Extending parent repr
def __repr__(self) -> str:
    parent = super().__repr__()
    return f"{parent[:-1]}, extra={self.extra!r})"

# BAD: Completely replacing
def __repr__(self) -> str:
    return f"MySubclass({self.extra})"  # Lost parent info!
```

---

## Dataclass Integration

```python
from dataclasses import dataclass
from functools import total_ordering

@total_ordering
@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float

    def __repr__(self) -> str:
        """Custom repr (overrides dataclass default)."""
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) < (other.x, other.y)
```

---

## Quick Checklist

Before implementing a dunder method, ask:

- [ ] Is this Python source code (not tests)?
- [ ] Does this method have type hints?
- [ ] Does this method have a docstring?
- [ ] Does it return `NotImplemented` for type mismatches?
- [ ] Is it free of side effects?
- [ ] Does it follow the principle of least astonishment?
- [ ] For subclasses: does it call `super()` when appropriate?
- [ ] Is this method NOT in the forbidden list?
