"""
Subclass Example: Proper dunder handling when subclassing.

This demonstrates best practices for subclass dunder methods:
- Calling super() appropriately
- Extending rather than replacing parent behavior
- Respecting parent class contracts
- Being conservative with overrides
"""

from collections import UserDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


# GOOD: Extending UserDict with custom __repr__
class ConfigDict(UserDict):
    """A dictionary that tracks its source file.

    Demonstrates safe subclassing of dict-like classes.
    - Uses UserDict (designed for subclassing) instead of dict
    - Only adds __repr__ without changing container semantics
    - Calls super() to preserve parent behavior
    """

    def __init__(self, data: dict | None = None, source: str = "unknown") -> None:
        """Initialize with optional data and source tracking."""
        super().__init__(data)
        self._source = source

    def __repr__(self) -> str:
        """Extend parent repr with source information.

        Calls super().__repr__() and augments it rather than
        completely replacing the representation.
        """
        parent_repr = super().__repr__()
        return f"ConfigDict({parent_repr}, source={self._source!r})"

    # Note: We do NOT override __len__, __contains__, __getitem__, etc.
    # The parent class handles these correctly.


# GOOD: Safe Path subclass
class ProjectPath(Path):
    """A Path that knows about project structure.

    Demonstrates:
    - Minimal overrides on standard library class
    - Preserving Path's well-defined behavior
    - Adding new methods instead of changing existing ones
    """

    _flavour = Path(".")._flavour  # Required for Path subclassing

    def __new__(cls, *args: Any, project_root: str | None = None) -> "ProjectPath":
        """Create new ProjectPath instance."""
        obj = super().__new__(cls, *args)
        return obj

    def __init__(self, *args: Any, project_root: str | None = None) -> None:
        """Initialize with optional project root tracking."""
        # Note: Path.__init__ doesn't take arguments, but we need to
        # store our custom attribute
        self._project_root = project_root

    def __repr__(self) -> str:
        """Provide informative repr while preserving Path info.

        Shows both the path and project context.
        """
        path_str = super().__str__()
        if self._project_root:
            return f"ProjectPath({path_str!r}, project_root={self._project_root!r})"
        return f"ProjectPath({path_str!r})"

    # Note: We do NOT override __eq__, __hash__, __truediv__, etc.
    # Path's behavior for these is well-defined and expected.

    # GOOD: Add new methods instead of changing existing behavior
    def relative_to_project(self) -> Path:
        """Return path relative to project root if known."""
        if self._project_root:
            return self.relative_to(self._project_root)
        return self


# GOOD: Dataclass inheriting from another dataclass
@dataclass
class BaseEntity:
    """Base class for entities with an ID."""

    id: int
    name: str

    def __repr__(self) -> str:
        """Base representation showing id and name."""
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"


@dataclass
class User(BaseEntity):
    """User entity extending BaseEntity.

    Demonstrates:
    - Proper dataclass inheritance
    - Extending __repr__ via super()
    - Not changing equality semantics
    """

    email: str

    def __repr__(self) -> str:
        """Extend parent repr with email.

        Builds on parent representation rather than replacing it.
        """
        # Get base info and extend it
        base = super().__repr__()
        # Remove closing paren and add our field
        return f"{base[:-1]}, email={self.email!r})"


# GOOD: Custom iterator with proper __iter__
class PagedResults:
    """Iterator over paged API results.

    Demonstrates:
    - Implementing __iter__ for iteration protocol
    - Clear resource semantics
    - Not overriding unnecessary dunders
    """

    def __init__(self, pages: list[list[Any]]) -> None:
        """Initialize with a list of pages."""
        self._pages = pages
        self._current_page = 0
        self._current_index = 0

    def __repr__(self) -> str:
        """Show current iteration state."""
        total_items = sum(len(p) for p in self._pages)
        return f"PagedResults(pages={len(self._pages)}, total_items={total_items})"

    def __iter__(self) -> Iterator[Any]:
        """Return iterator over all items across pages.

        Yields items one at a time, handling page boundaries.
        """
        for page in self._pages:
            yield from page

    def __len__(self) -> int:
        """Return total number of items across all pages.

        This makes sense because we're iterating over items.
        """
        return sum(len(p) for p in self._pages)

    # Note: We implement __iter__ and __len__ because this IS
    # semantically a collection of items. We do NOT implement
    # __getitem__ because random access across pages is not
    # the primary use case.


# AVOID: Example of what NOT to do (commented out)
"""
# BAD: Breaking dict contract
class BrokenDict(dict):
    def __eq__(self, other):
        # BAD: Changes equality to only check keys
        return set(self.keys()) == set(other.keys())

    def __len__(self):
        # BAD: Returns something other than item count
        return sum(len(str(v)) for v in self.values())


# BAD: Adding container behavior to non-container
class BrokenPath(Path):
    def __len__(self):
        # BAD: Path is not a container, what does len mean?
        return len(str(self))

    def __getitem__(self, key):
        # BAD: Path indexing is confusing
        return self.parts[key]

    def __contains__(self, item):
        # BAD: What does "in" mean for a path?
        return item in str(self)
"""


# Summary of Subclass Guidelines:
#
# 1. Use super() for initialization and when extending behavior
# 2. Extend __repr__/__str__ rather than completely replacing
# 3. Don't override container methods unless you're a container
# 4. Don't change equality/hashing semantics from parent
# 5. Prefer adding new methods over changing existing ones
# 6. Use UserDict/UserList instead of dict/list for subclassing
# 7. Check parent documentation before any override
# 8. When unsure, don't override - add a comment for human review
