from rules.ast_nodes import FunctionCall, Comparison, LogicalExpression, Literal

def evaluate_ast(self, ast, context):
    """
    Recursively evaluate an AST node using the profiling context.

    Args:
        ast: An AST node (FunctionCall, Comparison, LogicalExpression, Literal)
        context: Dictionary or object holding profiling values.

    Returns:
        The boolean or literal result of evaluating the AST.
    """
    if isinstance(ast, FunctionCall):
        func = self.function_registry.get(ast.func_name)
        if not func:
            raise ValueError(f"Unknown function: '{ast.func_name}'")
        return func(context, ast.field_name)

    elif isinstance(ast, Comparison):
        left_value = self.evaluate_ast(ast.left, context)
        right_value = self.evaluate_ast(ast.right, context)

        op_func = self.operator_registry.get(ast.operator)
        if not op_func:
            raise ValueError(f"Unknown comparison operator: '{ast.operator}'")
        return op_func(left_value, right_value)

    elif isinstance(ast, LogicalExpression):
        operator = ast.operator.upper()
        if operator not in self.logical_operators:
            raise ValueError(f"Unknown logical operator: '{operator}'")

        left_result = self.evaluate_ast(ast.left, context)

        if operator == 'AND':
            return left_result and self.evaluate_ast(ast.right, context)
        elif operator == 'OR':
            return left_result or self.evaluate_ast(ast.right, context)

    elif isinstance(ast, Literal):
        return ast.value

    else:
        raise TypeError(f"Unsupported AST node type: {type(ast).__name__}")
