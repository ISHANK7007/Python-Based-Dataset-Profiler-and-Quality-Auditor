class FunctionCall:
    def __init__(self, func_name, field_name):
        self.func_name = func_name
        self.field_name = field_name

class Comparison:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class LogicalExpression:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator  # AND / OR
        self.right = right

class Literal:
    def __init__(self, value):
        self.value = value
