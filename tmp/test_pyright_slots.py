# In your .py file:
class Point:
    __slots__ = ["x", "y"]

    # It's common to define them without an assignment,
    # but modern Python often prefers using the new syntax
    # or dataclasses/NamedTuple for better typing support.
    # For simple cases, Pyright can often infer the types
    # from the __init__ method, but explicitly declaring them is safer:
    # x: int
    # y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.z = 3
