class Expression:
    """Base class for all expressions"""
    pass

class FunctionCall(Expression):
    def __init__(self, func_name, field_name):
        self.func_name = func_name
        self.field_name = field_name
        
class Comparison(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
        
class LogicalExpression(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Literal(Expression):
    def __init__(self, value):
        self.value = value