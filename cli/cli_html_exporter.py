def assess_impact(violation, profiles, rules):
    """
    Assess the impact of a violation based on profiling metadata and rule dependencies.

    Parameters:
        violation (RuleViolation): Violation object with at least a 'details' dict containing 'column'.
        profiles: Object with access to profiling metadata, including correlations.
        rules (List[Rule]): List of rule objects, each supporting get_dependencies().

    Returns:
        dict: Impact metadata including rule dependency count, correlation with target,
              usage score, and a qualitative impact assessment.
    """
    column = violation.details.get('column')
    if column is None:
        return {
            'dependent_rule_count': 0,
            'has_target_correlation': False,
            'usage_score': 0,
            'impact_assessment': 'low'
        }

    # Check if column is used in other rules
    dependent_rules = [r for r in rules if hasattr(r, "get_dependencies") and column in r.get_dependencies()]

    # Check correlation with target variable (safely)
    try:
        target_correlation = profiles.current.get_correlation(column, 'target_variable') or 0.0
    except AttributeError:
        target_correlation = 0.0

    # Estimate column usage score
    try:
        usage_score = get_column_usage_score(column)
    except Exception:
        usage_score = 0

    # Qualitative impact score
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
