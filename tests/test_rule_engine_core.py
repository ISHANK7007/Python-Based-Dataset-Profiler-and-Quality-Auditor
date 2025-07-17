import re

def parse(self, rule_string):
    """
    Tokenize and parse a rule string into an AST.
    """
    tokens = self.tokenize(rule_string)
    normalized_tokens = [t for group in tokens for t in group if t]  # Flatten
    return self.build_ast(normalized_tokens)

def tokenize(self, rule_string):
    """
    Tokenizes a rule expression string.

    Returns:
        List of tokens as flat strings.
    """
    token_pattern = r"""
        (\w+\([\w\.]+\))       |  # Function calls like null_rate(col)
        (==|!=|<=|>=|<|>)      |  # Comparison operators
        (\d+\.\d+|\d+)         |  # Numbers
        (["'][^"']+["'])       |  # Quoted literals
        (\()|(\))              |  # Parentheses
        (\bAND\b|\bOR\b|\bNOT\b) # Logical operators
    """
    matches = re.findall(token_pattern, rule_string, re.IGNORECASE | re.VERBOSE)
    tokens = [t for group in matches for t in group if t]
    return tokens
