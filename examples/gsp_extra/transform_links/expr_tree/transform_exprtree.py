# expr_tree.py
from abc import ABC, abstractmethod
import math


# =========================
# Base Node + DSL Overloads
# =========================
class Node(ABC):
    @abstractmethod
    def evaluate(self, context=None) -> "Node":
        pass

    # Operator overloading for DSL
    def __add__(self, other):
        return Add(self, _to_node(other))

    # Operator overloading for DSL
    def __radd__(self, other):
        return Add(_to_node(other), self)

    def __sub__(self, other):
        return Sub(self, _to_node(other))

    def __mul__(self, other):
        return Mul(self, _to_node(other))

    def __truediv__(self, other):
        return Div(self, _to_node(other))

    def __pow__(self, other):
        return Pow(self, _to_node(other))

    # Optional for nice string representation
    def __repr__(self):
        return f"{self.__class__.__name__}()"


def _to_node(x):
    """Convert raw values (int/float) to Value nodes automatically."""
    return x if isinstance(x, Node) else Value(x)


# =========================
# Node Implementations
# =========================
class Value(Node):
    def __init__(self, value):
        self.value = value

    def evaluate(self, context=None):
        return self.value

    def __repr__(self):
        return f"Value({self.value})"


class Var(Node):
    def __init__(self, name):
        self.name = name

    def evaluate(self, context=None):
        if context and self.name in context:
            return context[self.name]
        raise ValueError(f"Variable '{self.name}' missing in context")

    def __repr__(self):
        return f"Var({self.name})"


class BinOp(Node):
    def __init__(self, left, right):
        self.left = _to_node(left)
        self.right = _to_node(right)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.left}, {self.right})"


class Add(BinOp):
    def evaluate(self, context=None) -> Node:
        return self.left.evaluate(context) + self.right.evaluate(context)


class Sub(BinOp):
    def evaluate(self, context=None):
        return self.left.evaluate(context) - self.right.evaluate(context)


class Mul(BinOp):
    def evaluate(self, context=None):
        return self.left.evaluate(context) * self.right.evaluate(context)


class Div(BinOp):
    def evaluate(self, context=None):
        return self.left.evaluate(context) / self.right.evaluate(context)


class Pow(BinOp):
    def evaluate(self, context=None):
        return self.left.evaluate(context) ** self.right.evaluate(context)


# =========================
# Functions (sin, cos, ...)
# =========================
class Func(Node):
    def __init__(self, func, node):
        self.func = func
        self.node = _to_node(node)

    def evaluate(self, context=None) -> "Node":
        return self.func(self.node.evaluate(context))

    def __repr__(self):
        return f"Func({self.func.__name__}, {self.node})"


def sin(x):
    return Func(math.sin, x)


def cos(x):
    return Func(math.cos, x)


# =========================
# Standalone Test / Demo
# =========================
if __name__ == "__main__":
    # Create DSL variables
    x = Var("x")
    y = Var("y")

    # Example expression: (x + 3) * (y - 1)^2 + sin(x)
    expr = (x + 3) * (y - 1) ** 2 + sin(x)

    print("Expression Tree:", expr)
    print()

    context = {"x": 1.57, "y": 5}  # sin(pi/2) approx 1
    result = expr.evaluate(context)

    print("Context:", context)
    print("Result:", result)
    print()
    print("Manual check:")
    print(f"  (1.57 + 3) * (5 - 1)^2 + sin(1.57)")
    print(f"≈ 4.57 * 16 + 1 = {4.57*16 + 1}")
