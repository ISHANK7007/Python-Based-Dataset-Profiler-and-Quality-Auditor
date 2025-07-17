def get_column_usage_score(column_name):
    """
    Stub for downstream usage scoring logic.
    This should return a numeric score representing how heavily a column is used
    in downstream transformations, reports, or ML pipelines.

    For now, it returns a mocked score. Replace with actual logic or lookup.
    """
    usage_scores = {
        "age": 8,
        "income": 6,
        "zipcode": 3,
        "gender": 5,
    }
    return usage_scores.get(column_name, 2)


def assess_impact(violation, profiles, rules):
    """
    Assess the impact of a violation based on profiles and rule dependencies.

    Returns:
        dict with:
            - dependent_rule_count
            - has_target_correlation
            - usage_score
            - impact_assessment ("high" | "medium")
    """
    column = violation.details.get('column')
    if column is None:
        return {
            'dependent_rule_count': 0,
            'has_target_correlation': False,
            'usage_score': 0,
            'impact_assessment': 'low'
        }

    # Rules where this column is a dependency
    dependent_rules = [
        r for r in rules
        if hasattr(r, "get_dependencies") and column in r.get_dependencies()
    ]

    # Safe correlation lookup
    try:
        target_correlation = profiles.current.get_correlation(column, 'target_variable') or 0.0
    except AttributeError:
        target_correlation = 0.0

    # Usage score estimation
    try:
        usage_score = get_column_usage_score(column)
    except Exception:
        usage_score = 0

    high_impact = (
        len(dependent_rules) > 2 or 
        target_correlation > 0.5 or 
        usage_score > 7
    )

    return {
        'dependent_rule_count': len(dependent_rules),
        'has_target_correlation': target_correlation > 0.3,
        'usage_score': usage_score,
        'impact_assessment': 'high' if high_impact else 'medium'
    }
