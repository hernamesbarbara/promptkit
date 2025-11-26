"""
Bad Example: Python class with poorly-implemented dunder methods.

DO NOT USE THIS AS A TEMPLATE.

This file demonstrates anti-patterns to AVOID:
- Side effects in __repr__/__str__
- Ambiguous representations
- Meaningless container dunders
- Context managers without resource semantics
- Broken equality/comparison
- Missing type hints
- Missing docstrings
"""


# BAD: Everything wrong with dunder implementation
class Temperature:
    def __init__(self, celsius):  # BAD: No type hints
        self.celsius = celsius

    def __repr__(self):  # BAD: No return type hint
        print("Calling __repr__!")  # BAD: Side effect (I/O)
        return f"{self.celsius}"  # BAD: Ambiguous, same as __str__

    def __str__(self):  # BAD: No return type hint
        return self.__repr__()  # BAD: Calls __repr__ directly

    def __eq__(self, other):  # BAD: No type hints
        return True  # BAD: Always equal, breaks collections/sets

    def __add__(self, other):  # BAD: No type hints
        return other  # BAD: Returns the other operand, nonsense

    def __len__(self):  # BAD: Temperature is NOT a container
        return int(self.celsius)  # BAD: Meaningless length

    def __getitem__(self, key):  # BAD: Temperature is NOT indexable
        return "lol"  # BAD: Returns nonsense

    def __enter__(self):  # BAD: Temperature manages no resources
        print("Entering!")  # BAD: Side effect
        return 123  # BAD: Wrong return type (should return self)

    def __exit__(self, *args):  # BAD: No proper signature
        print("Exiting!")  # BAD: Side effect
        return True  # BAD: Swallows ALL exceptions!


# BAD: Mutable class with __hash__
class BadPoint:
    def __init__(self, x, y):
        self.x = x  # Mutable attribute
        self.y = y  # Mutable attribute

    def __hash__(self):  # BAD: Never hash mutable objects!
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# BAD: Overriding dunders on well-known base class
class BadDict(dict):
    def __len__(self):  # BAD: Changes meaning of len() for dict
        return 42  # BAD: Always returns 42, breaks dict contract

    def __contains__(self, key):  # BAD: Changes 'in' operator meaning
        return True  # BAD: Everything is "in" this dict

    def __bool__(self):  # BAD: dict's truthiness is well-defined
        return False  # BAD: Empty or not, always falsy


# BAD: __bool__ without clear meaning
class BadContainer:
    def __init__(self, items):
        self.items = items

    def __bool__(self):  # BAD: What does "truthy container" mean?
        # Is it truthy when non-empty? When all items are truthy?
        # When some condition is met? Ambiguous!
        return len(self.items) > 5  # BAD: Arbitrary threshold


# BAD: Side effects everywhere
class BadLogger:
    def __init__(self, name):
        self.name = name
        self.call_count = 0

    def __repr__(self):
        self.call_count += 1  # BAD: Mutates state!
        with open("/tmp/repr.log", "a") as f:  # BAD: I/O in __repr__!
            f.write(f"repr called {self.call_count} times\n")
        return f"BadLogger({self.name})"

    def __str__(self):
        import time  # BAD: Import inside method
        time.sleep(0.1)  # BAD: Expensive operation
        return self.__repr__()  # BAD: Calls __repr__ directly


# BAD: Missing NotImplemented returns
class BadMoney:
    def __init__(self, amount):
        self.amount = amount

    def __eq__(self, other):
        # BAD: Should return NotImplemented for non-BadMoney
        return self.amount == other.amount  # Raises AttributeError!

    def __add__(self, other):
        # BAD: Should return NotImplemented for non-BadMoney
        return BadMoney(self.amount + other.amount)  # Raises AttributeError!

    def __lt__(self, other):
        # BAD: Should return NotImplemented for non-BadMoney
        return self.amount < other.amount  # Raises AttributeError!


"""
Summary of Anti-Patterns:

1. Side effects in __repr__/__str__:
   - print(), logging, file I/O
   - State mutation
   - Expensive computations

2. Ambiguous representations:
   - __repr__ == __str__ when they should differ
   - Missing class name in __repr__
   - Not showing key attributes

3. Meaningless dunders:
   - Container methods on non-containers
   - Context managers on non-resources
   - __bool__ with arbitrary/unclear meaning

4. Broken contracts:
   - __eq__ always True/False
   - __hash__ on mutable objects
   - Overriding base class dunders incorrectly

5. Missing safeguards:
   - No type hints
   - No docstrings
   - No NotImplemented returns
   - No input validation

6. Direct dunder calls:
   - self.__repr__() instead of repr(self)
   - obj.__len__() instead of len(obj)
"""
