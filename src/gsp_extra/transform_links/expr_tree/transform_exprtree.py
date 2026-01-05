"""Expression tree for building and evaluating mathematical expressions.

This module provides a domain-specific language (DSL) for constructing and evaluating
mathematical expressions as abstract syntax trees. It supports basic arithmetic operations
(addition, subtraction, multiplication, division) with operator overloading for natural
expression construction.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Union

Number = Union[int, float]


# ============================
# Base Expression Node
# ============================
class Node(ABC):
    """Abstract base class for expression tree nodes.
    
    All expression nodes inherit from this class and must implement the eval method.
    Operator overloading is provided to enable natural mathematical syntax when
    constructing expressions.
    """
    
    @abstractmethod
    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate the expression node with the given variable context.
        
        Args:
            context: Dictionary mapping variable names to their values.
            
        Returns:
            The evaluated result as a float.
        """
        ...

    # --- Operator overloads to create DSL ---
    def __add__(self, other: Union[Node, Number]) -> Node:
        """Overload addition operator to create an Add node."""
        return Add(self, _to_node(other))

    def __radd__(self, other: Number) -> Node:
        """Overload reflected addition for number + Node."""
        return Add(_to_node(other), self)

    def __sub__(self, other: Union[Node, Number]) -> Node:
        """Overload subtraction operator to create a Sub node."""
        return Sub(self, _to_node(other))

    def __rsub__(self, other: Number) -> Node:
        """Overload reflected subtraction for number - Node."""
        return Sub(_to_node(other), self)

    def __mul__(self, other: Union[Node, Number]) -> Node:
        """Overload multiplication operator to create a Mul node."""
        return Mul(self, _to_node(other))

    def __rmul__(self, other: Number) -> Node:
        """Overload reflected multiplication for number * Node."""
        return Mul(_to_node(other), self)

    def __truediv__(self, other: Union[Node, Number]) -> Node:
        """Overload division operator to create a Div node."""
        return Div(self, _to_node(other))

    def __rtruediv__(self, other: Number) -> Node:
        """Overload reflected division for number / Node."""
        return Div(_to_node(other), self)


def _to_node(x: Union[Node, Number]) -> Node:
    """Convert a number to a Value node if needed.
    
    Helper function to auto-convert numeric literals into Value() nodes.
    
    Args:
        x: Either a Node or a numeric value.
        
    Returns:
        A Node instance (either the input Node or a new Value node).
    """
    return x if isinstance(x, Node) else Value(float(x))


# ============================
# Leaf nodes
# ============================
class Value(Node):
    """Leaf node representing a constant numeric value.
    
    Attributes:
        value: The constant float value stored in this node.
    """
    
    def __init__(self, value: float) -> None:
        """Initialize a Value node with a constant.
        
        Args:
            value: The constant value to store.
        """
        self.value = value

    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate the value node.
        
        Args:
            context: Variable context (unused for constant values).
            
        Returns:
            The stored constant value.
        """
        return self.value

    def __repr__(self) -> str:
        """Return string representation of the value."""
        return f"{self.value}"


class Variable(Node):
    """Leaf node representing a variable that will be looked up in the context.
    
    Attributes:
        name: The name of the variable.
    """
    
    def __init__(self, name: str) -> None:
        """Initialize a Variable node.
        
        Args:
            name: The name of the variable to look up during evaluation.
        """
        self.name = name

    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate the variable by looking it up in the context.
        
        Args:
            context: Dictionary mapping variable names to values.
            
        Returns:
            The value associated with this variable name.
            
        Raises:
            KeyError: If the variable name is not found in the context.
        """
        if self.name not in context:
            raise KeyError(f"Variable '{self.name}' not found in context")
        return context[self.name]

    def __repr__(self) -> str:
        """Return the variable name as its string representation."""
        return self.name


# ============================
# Operator base
# ============================
class BinaryOp(Node):
    """Abstract base class for binary operation nodes.
    
    Binary operations have a left and right child node and an operator symbol.
    
    Attributes:
        left: The left operand node.
        right: The right operand node.
    """
    
    def __init__(self, left: Node, right: Node) -> None:
        """Initialize a binary operation with left and right operands.
        
        Args:
            left: The left operand node.
            right: The right operand node.
        """
        self.left = left
        self.right = right

    @property
    @abstractmethod
    def symbol(self) -> str:
        """Return the operator symbol for this binary operation.
        
        Returns:
            The string representation of the operator (e.g., '+', '-', '*', '/').
        """
        pass

    def __repr__(self) -> str:
        """Return string representation with operator and parentheses."""
        return f"({self.left} {self.symbol} {self.right})"


# ============================
# Specific operators
# ============================
class Add(BinaryOp):
    """Binary operation node for addition."""
    
    @property
    def symbol(self) -> str:
        """Return the addition operator symbol."""
        return "+"

    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate addition by summing left and right operands.
        
        Args:
            context: Variable context for evaluation.
            
        Returns:
            The sum of the evaluated left and right operands.
        """
        return self.left.eval(context) + self.right.eval(context)


class Sub(BinaryOp):
    """Binary operation node for subtraction."""
    
    @property
    def symbol(self) -> str:
        """Return the subtraction operator symbol."""
        return "-"

    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate subtraction by subtracting right from left operand.
        
        Args:
            context: Variable context for evaluation.
            
        Returns:
            The difference of the evaluated left and right operands.
        """
        return self.left.eval(context) - self.right.eval(context)


class Mul(BinaryOp):
    """Binary operation node for multiplication."""
    
    @property
    def symbol(self) -> str:
        """Return the multiplication operator symbol."""
        return "*"

    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate multiplication by multiplying left and right operands.
        
        Args:
            context: Variable context for evaluation.
            
        Returns:
            The product of the evaluated left and right operands.
        """
        return self.left.eval(context) * self.right.eval(context)


class Div(BinaryOp):
    """Binary operation node for division."""
    
    @property
    def symbol(self) -> str:
        """Return the division operator symbol."""
        return "/"

    def eval(self, context: Dict[str, float]) -> float:
        """Evaluate division by dividing left operand by right operand.
        
        Args:
            context: Variable context for evaluation.
            
        Returns:
            The quotient of the evaluated left and right operands.
        """
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
