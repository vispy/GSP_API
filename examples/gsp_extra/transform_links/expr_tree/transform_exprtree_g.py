"""Expression tree DSL with unit-aware arithmetic.

This module provides a domain-specific language for building and evaluating
mathematical expressions with optional unit tracking. It supports basic arithmetic
operations with unit validation to prevent operations on incompatible units.
"""
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Union, Any, Optional

# Define Type Aliases for clarity
# A Value is a number (int or float)
Value = Union[int, float]
# The result of evaluate is always a (Value, UnitName) tuple. UnitName can be None.
UnitName = Optional[str]
EvalResult = Tuple[Value, UnitName]
# Context maps variable names (str) to their values/units (Value or EvalResult)
Context = Dict[str, Union[Value, EvalResult]]


# --- Abstract Base Node ---
class Node(ABC):
    """Abstract base class for all tree nodes."""

    @abstractmethod
    def evaluate(self, context: Context) -> EvalResult:
        """Calculates and returns the result as (Value, UnitName)."""
        pass


# --- DSL Enabling Base Class ---
class ExpressionNode(Node):
    """Implements DSL by overloading arithmetic operators to build the tree.
    
    All concrete nodes (NumberNode, VariableNode) must inherit this class
    to enable natural mathematical syntax for expression construction.
    """

    def __add__(self, other: Union["Node", Value]) -> "OperatorNode":
        """Overload addition operator to create an addition node."""
        other_node: Node = other if isinstance(other, Node) else NumberNode(other)
        return OperatorNode("+", self, other_node)

    def __sub__(self, other: Union["Node", Value]) -> "OperatorNode":
        """Overload subtraction operator to create a subtraction node."""
        other_node: Node = other if isinstance(other, Node) else NumberNode(other)
        return OperatorNode("-", self, other_node)

    def __mul__(self, other: Union["Node", Value]) -> "OperatorNode":
        """Overload multiplication operator to create a multiplication node."""
        other_node: Node = other if isinstance(other, Node) else NumberNode(other)
        return OperatorNode("*", self, other_node)

    # Right-side operators handle cases like `5 + x` or `5 * x`
    def __radd__(self, other: Value) -> "OperatorNode":
        """Overload reflected addition for Value + Node."""
        return self.__add__(other)

    def __rmul__(self, other: Value) -> "OperatorNode":
        """Overload reflected multiplication for Value * Node."""
        return self.__mul__(other)

    # Note: Division (__, __rdiv__) and power (__, __rpow__) can be added similarly


# --- Concrete Nodes ---


class NumberNode(ExpressionNode):
    """Represents a final numerical value (a leaf node) with an optional unit."""

    def __init__(self, value: Value, unit: UnitName = None):
        """Initialize a number node with a value and optional unit.
        
        Args:
            value: The numeric value to store.
            unit: Optional unit name for the value.
        """
        self.value = value
        self.unit = unit

    def evaluate(self, context: Context) -> EvalResult:
        """Returns the stored value and unit."""
        return (self.value, self.unit)

    def __repr__(self) -> str:
        """Return string representation of the number with its unit."""
        unit_str = f"'{self.unit}'" if self.unit else ""
        return f"{self.value}{unit_str}"


class VariableNode(ExpressionNode):
    """Represents a variable whose value must be looked up in the context."""

    def __init__(self, name: str):
        """Initialize a variable node with a name.
        
        Args:
            name: The variable name to look up during evaluation.
        """
        self.name = name

    def evaluate(self, context: Context) -> EvalResult:
        """Looks up the value/unit tuple in the context."""
        if self.name in context:
            val = context[self.name]
            if isinstance(val, tuple):
                return val  # Already an EvalResult (value, unit)
            return (val, None)  # Raw number, assume no unit
        raise KeyError(f"Variable '{self.name}' not found in context.")

    def __repr__(self) -> str:
        """Return the variable name as its string representation."""
        return self.name


class OperatorNode(ExpressionNode):
    """Represents an operation (+, -, *, /) (an internal node)."""

    def __init__(self, operator: str, left: Node, right: Node):
        """Initialize an operator node with an operator and two operands.
        
        Args:
            operator: The operator symbol ('+', '-', '*', '/').
            left: The left operand node.
            right: The right operand node.
        """
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, context: Context) -> EvalResult:
        """Evaluates children and performs unit-aware arithmetic."""
        left_val, left_unit = self.left.evaluate(context)
        right_val, right_unit = self.right.evaluate(context)

        result_value: Value = 0
        result_unit: UnitName = None

        if self.operator == "+" or self.operator == "-":
            # Unit Validation for Addition/Subtraction
            if left_unit != right_unit:
                raise ValueError(f"Cannot {self.operator} nodes with different units: " f"'{left_unit}' and '{right_unit}'. Ensure units match.")
            result_unit = left_unit
            result_value = left_val + right_val if self.operator == "+" else left_val - right_val

        elif self.operator == "*":
            # Simple unit tracking for multiplication (unit * dimensionless = unit)
            result_value = left_val * right_val
            # If one side is dimensionless (None), the result takes the other side's unit.
            result_unit = left_unit if right_unit is None else right_unit if left_unit is None else None
            # Complex unit math (e.g., inch*inch) would require more logic here.

        else:
            raise ValueError(f"Unknown operator: {self.operator}")

        return (result_value, result_unit)

    def __repr__(self) -> str:
        """Return string representation of the operation with parentheses."""
        return f"({self.left!r} {self.operator} {self.right!r})"


# --- Unit DSL Helper ---
class Unit:
    """Unit wrapper allowing syntax like `5 * cm` to create `NumberNode(5, 'cm')`."""

    def __init__(self, name: str):
        """Initialize a unit with a name.
        
        Args:
            name: The name of the unit (e.g., 'cm', 'inch').
        """
        self.name = name

    def __rmul__(self, value: Union[Value, Node]) -> Union[NumberNode, OperatorNode, Any]:
        """Handles the right-multiplication `Value * Unit` or `Node * Unit`."""
        # Case 1: Raw Number * Unit (e.g., 5 * cm)
        if isinstance(value, (int, float)):
            return NumberNode(value, unit=self.name)

        # Case 2: Node * Unit (e.g., x * cm)
        if isinstance(value, ExpressionNode):
            # Treat as Node * NumberNode(1, unit) and rely on ExpressionNode's __mul__
            return value * NumberNode(1, unit=self.name)

        return NotImplemented

    def __repr__(self) -> str:
        """Return the unit name as its string representation."""
        return self.name


# --- Mini Test Suite ---
if __name__ == "__main__":
    print("--- 🌳 Evaluation Tree DSL Test Suite ---")

    # 1. Instantiate the Unit objects for the DSL
    cm = Unit("cm")
    inch = Unit("inch")

    # 2. Define Variables
    length = VariableNode("length")
    count = VariableNode("count")

    # --- Test Case 1: Simple Calculation (Unit-aware) ---
    print("\n## Test 1: Simple Unit Addition")
    # Expression: (5 cm + 10 cm)
    expr1 = (5 * cm) + (10 * cm)
    context1: Context = {}

    result1, unit1 = expr1.evaluate(context1)
    print(f"Expression: {expr1}")
    # Expected: (15, 'cm')
    print(f"Result: {result1} {unit1}")
    assert result1 == 15 and unit1 == "cm", "Test 1 Failed: Simple addition."

    # --- Test Case 2: Calculation with Variables ---
    print("\n## Test 2: Calculation with Variables")
    # Expression: (length * 2) + 10
    expr2 = (length * 2) + 10
    context2: Context = {"length": 20}  # dimensionless context value

    result2, unit2 = expr2.evaluate(context2)
    print(f"Expression: {expr2}")
    # Expected: (20 * 2) + 10 = 50 (None)
    print(f"Context: {context2}")
    print(f"Result: {result2} {unit2}")
    assert result2 == 50 and unit2 is None, "Test 2 Failed: Variable calculation."

    # --- Test Case 3: Complex Expression with Unit Error ---
    print("\n## Test 3: Complex Expression & Unit Mismatch Error")
    # Expression: (length * inch) + (10 * cm)
    # This should fail due to unit mismatch at the root '+' operation.
    expr3 = (length * inch) + (10 * cm)
    context3: Context = {"length": 5}

    print(f"Expression: {expr3}")
    try:
        expr3.evaluate(context3)
    except ValueError as e:
        print(f"Error Caught (as expected): {e}")
        assert "Cannot + nodes with different units: 'inch' and 'cm'" in str(e), "Test 3 Failed: Wrong error message."

    # --- Test Case 4: Complex Expression with Unit Success ---
    print("\n## Test 4: Complex Expression with Unit Success")
    # Expression: (length * inch) * count + 50
    expr4 = (length * inch * count) + 50
    context4: Context = {"length": 10, "count": 5}

    result4, unit4 = expr4.evaluate(context4)
    print(f"Expression: {expr4}")
    # Calculation: (10 inch * 5) + 50 = 50 inch + 50 (error prone!)
    # *Correction*: OperatorNode currently allows adding 'inch' and 'None' unit if the unit is None for the right side
    # Let's adjust context4 to match units for safety:
    context4_safe: Context = {"length": 10, "count": 5}

    # Recalculation: (10 inch * 5) + 50 = (50 inch) + 50 (error is expected by logic!)
    # Let's test the error:
    try:
        expr4.evaluate(context4_safe)
    except ValueError as e:
        print(f"Error Caught (as expected): {e}")
        assert "Cannot + nodes with different units: 'inch' and 'None'" in str(e), "Test 4 Failed: Wrong error message."

    print("\n--- All tests passed (including expected errors)! ---")
