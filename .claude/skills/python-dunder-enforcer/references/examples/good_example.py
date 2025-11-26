"""
Good Example: Python class with well-implemented dunder methods.

This demonstrates best practices for implementing dunder methods:
- Type hints on all methods
- Docstrings explaining behavior
- No side effects in __repr__/__str__
- Proper use of NotImplemented for type mismatches
- @total_ordering to reduce boilerplate
- Frozen dataclass for immutability
"""

from dataclasses import dataclass
from functools import total_ordering
from typing import Any


@total_ordering
@dataclass(frozen=True)
class Temperature:
    """Represents a temperature in Celsius.

    This is an immutable value object that supports:
    - Comparison operations (via @total_ordering)
    - Addition of temperatures
    - Developer-friendly repr and user-friendly str
    """

    celsius: float

    def __post_init__(self) -> None:
        """Validate that celsius is a numeric value."""
        if not isinstance(self.celsius, (int, float)):
            raise TypeError("celsius must be numeric")

    def __repr__(self) -> str:
        """Return unambiguous developer representation.

        Format follows the pattern: ClassName(attr=value)
        This could be used to recreate the object.
        """
        return f"Temperature(celsius={self.celsius!r})"

    def __str__(self) -> str:
        """Return user-friendly display format.

        Shows temperature with degree symbol and unit.
        """
        return f"{self.celsius}\u00b0C"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Temperature.

        Returns NotImplemented for non-Temperature comparisons,
        allowing Python to try the reverse operation.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius == other.celsius

    def __lt__(self, other: Any) -> bool:
        """Check if this temperature is less than another.

        Returns NotImplemented for non-Temperature comparisons.
        Combined with @total_ordering, this provides all comparison ops.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius

    def __add__(self, other: Any) -> "Temperature":
        """Add two temperatures together.

        Returns a new Temperature with the sum of celsius values.
        Returns NotImplemented for non-Temperature operands.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        return Temperature(self.celsius + other.celsius)

    def __sub__(self, other: Any) -> "Temperature":
        """Subtract one temperature from another.

        Returns a new Temperature with the difference.
        Returns NotImplemented for non-Temperature operands.
        """
        if not isinstance(other, Temperature):
            return NotImplemented
        return Temperature(self.celsius - other.celsius)


@dataclass
class Money:
    """Represents a monetary amount with currency.

    Demonstrates:
    - Mutable dataclass (no frozen=True)
    - Currency-aware operations
    - Clear error handling for currency mismatch
    """

    amount: float
    currency: str = "USD"

    def __repr__(self) -> str:
        """Return unambiguous developer representation."""
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"

    def __str__(self) -> str:
        """Return user-friendly currency format."""
        symbols = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5"}
        symbol = symbols.get(self.currency, self.currency + " ")
        return f"{symbol}{self.amount:.2f}"

    def __eq__(self, other: Any) -> bool:
        """Check equality considering both amount and currency."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other: Any) -> "Money":
        """Add two Money objects of the same currency.

        Raises ValueError if currencies don't match.
        """
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add {self.currency} and {other.currency}: "
                "currency mismatch"
            )
        return Money(self.amount + other.amount, self.currency)


class Interval:
    """Represents a numeric interval [start, end].

    Demonstrates:
    - Container-like behavior (only where meaningful)
    - __contains__ for 'in' operator
    - __len__ representing interval size (when it makes sense)
    - Manual __init__ with validation
    """

    def __init__(self, start: float, end: float) -> None:
        """Initialize interval with start and end bounds.

        Args:
            start: Lower bound (inclusive)
            end: Upper bound (inclusive)

        Raises:
            ValueError: If start > end
        """
        if start > end:
            raise ValueError(f"start ({start}) must be <= end ({end})")
        self._start = start
        self._end = end

    @property
    def start(self) -> float:
        """Lower bound of the interval."""
        return self._start

    @property
    def end(self) -> float:
        """Upper bound of the interval."""
        return self._end

    def __repr__(self) -> str:
        """Return unambiguous developer representation."""
        return f"Interval(start={self._start!r}, end={self._end!r})"

    def __str__(self) -> str:
        """Return mathematical interval notation."""
        return f"[{self._start}, {self._end}]"

    def __contains__(self, value: Any) -> bool:
        """Check if a value falls within the interval.

        Supports the 'in' operator: `5 in Interval(0, 10)`
        """
        if not isinstance(value, (int, float)):
            return False
        return self._start <= value <= self._end

    def __eq__(self, other: Any) -> bool:
        """Check if two intervals are equal."""
        if not isinstance(other, Interval):
            return NotImplemented
        return self._start == other._start and self._end == other._end

    def __len__(self) -> int:
        """Return the integer size of the interval.

        Note: This returns floor(end - start), which makes sense
        for discrete intervals. For continuous intervals, consider
        a .size or .length property instead.
        """
        return int(self._end - self._start)
