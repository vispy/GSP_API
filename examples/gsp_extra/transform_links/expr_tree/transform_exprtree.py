from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Union

Number = Union[int, float]


# ============================
# Base Expression Node
# ============================
class Node(ABC):
    @abstractmethod
    def eval(self, context: Dict[str, float]) -> float: ...

    # --- Operator overloads to create DSL ---
    def __add__(self, other: Union[Node, Number]) -> Node:
        return Add(self, _to_node(other))

    def __radd__(self, other: Number) -> Node:
        return Add(_to_node(other), self)

    def __sub__(self, other: Union[Node, Number]) -> Node:
        return Sub(self, _to_node(other))

    def __rsub__(self, other: Number) -> Node:
        return Sub(_to_node(other), self)

    def __mul__(self, other: Union[Node, Number]) -> Node:
        return Mul(self, _to_node(other))

    def __rmul__(self, other: Number) -> Node:
        return Mul(_to_node(other), self)

    def __truediv__(self, other: Union[Node, Number]) -> Node:
        return Div(self, _to_node(other))

    def __rtruediv__(self, other: Number) -> Node:
        return Div(_to_node(other), self)


# helper to auto-convert literals into Value()
def _to_node(x: Union[Node, Number]) -> Node:
    return x if isinstance(x, Node) else Value(float(x))


# ============================
# Leaf nodes
# ============================
class Value(Node):
    def __init__(self, value: float) -> None:
        self.value = value

    def eval(self, context: Dict[str, float]) -> float:
        return self.value

    def __repr__(self) -> str:
        return f"{self.value}"


class Variable(Node):
    def __init__(self, name: str) -> None:
        self.name = name

    def eval(self, context: Dict[str, float]) -> float:
        if self.name not in context:
            raise KeyError(f"Variable '{self.name}' not found in context")
        return context[self.name]

    def __repr__(self) -> str:
        return self.name


# ============================
# Operator base
# ============================
class BinaryOp(Node):
    def __init__(self, left: Node, right: Node) -> None:
        self.left = left
        self.right = right

    @property
    @abstractmethod
    def symbol(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"({self.left} {self.symbol} {self.right})"


# ============================
# Specific operators
# ============================
class Add(BinaryOp):
    @property
    def symbol(self) -> str:
        return "+"

    def eval(self, context: Dict[str, float]) -> float:
        return self.left.eval(context) + self.right.eval(context)


class Sub(BinaryOp):
    @property
    def symbol(self) -> str:
        return "-"

    def eval(self, context: Dict[str, float]) -> float:
        return self.left.eval(context) - self.right.eval(context)


class Mul(BinaryOp):
    @property
    def symbol(self) -> str:
        return "*"

    def eval(self, context: Dict[str, float]) -> float:
        return self.left.eval(context) * self.right.eval(context)


class Div(BinaryOp):
    @property
    def symbol(self) -> str:
        return "/"

    def eval(self, context: Dict[str, float]) -> float:
        return self.left.eval(context) / self.right.eval(context)


# =============================================================================
#
# =============================================================================
def pretty_print(node: Node, indent: str = "", last: bool = True) -> str:
    """Return an ASCII representation of the expression tree."""
    out = indent
    out += "└── " if last else "├── "
    out += repr(node) + "\n"

    if isinstance(node, BinaryOp):
        indent += "    " if last else "│   "
        # left is printed first, then right
        out += pretty_print(node.left, indent, False)
        out += pretty_print(node.right, indent, True)

    return out


# ============================
# Test Example
# ============================
if __name__ == "__main__":
    x, y = Variable("x"), Variable("y")
    # (5 + x) * (y - 1)
    expr = (5 + x) * (y - 1)

    print("Expr =", expr)
    print("Result =", expr.eval({"x": 3, "y": 2}))
    print(pretty_print(expr))
