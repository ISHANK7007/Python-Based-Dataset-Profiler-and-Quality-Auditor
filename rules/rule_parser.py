import re

class RuleParser:
    def parse(self, rule_string):
        tokens = self.tokenize(rule_string)
        normalized_tokens = [t for group in tokens for t in group if t]
        return self.build_ast(normalized_tokens)

    def tokenize(self, rule_string):
        token_pattern = r"""
            (\w+\([\w\.]+\))       |  # Function calls
            (==|!=|<=|>=|<|>)      |  # Comparison ops
            (\d+\.\d+|\d+)         |  # Numbers
            (["'][^"']+["'])       |  # Strings
            (\()|(\))              |  # Parentheses
            (\bAND\b|\bOR\b|\bNOT\b) # Logical ops
        """
        matches = re.findall(token_pattern, rule_string, re.IGNORECASE | re.VERBOSE)
        return matches

    def build_ast(self, tokens):
        raise NotImplementedError("AST builder not yet implemented.")
