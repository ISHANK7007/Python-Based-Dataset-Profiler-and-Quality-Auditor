import operator
from rules.ast_nodes import FunctionCall, Comparison, LogicalExpression, Literal
from rules.rule_parser import RuleParser  # Assumes a RuleParser class exists

class RuleEvaluator:
    def __init__(self):
        # Register statistical functions
        self.function_registry = {
            'std': self._std,
            'mean': self._mean,
            'mode': self._mode,
            'missing_rate': self._missing_rate,
            'unique_count': self._unique_count,
        }

        # Register comparison operators
        self.operator_registry = {
            '<': operator.lt,
            '>': operator.gt,
            '==': operator.eq,
            '!=': operator.ne,
            '<=': operator.le,
            '>=': operator.ge,
        }

        # Register logical operators
        self.logical_operators = {
            'AND': lambda x, y: x and y,
            'OR': lambda x, y: x or y,
        }

        # Rule parser instance
        self.parser = RuleParser()

    def evaluate(self, rule, context):
        """
        Evaluate a rule string against the given profiling context.
        """
        ast = self.parser.parse(rule)
        return self.evaluate_ast(ast, context)

    def evaluate_ast(self, ast, context):
        """
        Recursively evaluate an AST node. Must be implemented or injected.
        """
        # You already have this logic — reuse the latest fixed version provided earlier
        raise NotImplementedError("Must implement evaluate_ast or provide externally.")

    # ==== Function Implementations (simplified) ====

    def _std(self, context, field): return context.get(field, {}).get("std")
    def _mean(self, context, field): return context.get(field, {}).get("mean")
    def _mode(self, context, field): return context.get(field, {}).get("mode")
    def _missing_rate(self, context, field): return context.get(field, {}).get("missing_rate")
    def _unique_count(self, context, field): return context.get(field, {}).get("unique_count")
