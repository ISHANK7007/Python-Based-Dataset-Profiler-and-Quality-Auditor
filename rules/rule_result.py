def validate_rule_syntax(rule_string):
    """
    Validate rule syntax without executing it.

    Returns:
        tuple: (True, None) if valid, or (False, error_message) if invalid.
    """
    try:
        # Step 1: Tokenize
        try:
            tokens = tokenize(rule_string)
        except Exception as e:
            return False, f"Tokenization failed: {str(e)}"

        if not tokens:
            return False, "Tokenization returned empty result."

        # Step 2: Parse into AST
        try:
            ast = build_ast(tokens)
        except Exception as e:
            return False, f"AST building failed: {str(e)}"

        if ast is None:
            return False, "AST is None — rule might be malformed."

        # Step 3: Validate AST semantics
        try:
            validate_ast(ast)
        except Exception as e:
            return False, f"AST validation failed: {str(e)}"

        return True, None

    except Exception as e:
        # Final fallback — shouldn't be hit if above stages are correct
        return False, f"Unknown error during validation: {str(e)}"
