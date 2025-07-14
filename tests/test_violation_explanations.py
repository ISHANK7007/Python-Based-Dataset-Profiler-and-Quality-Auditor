def generate_examples(violation, profiles):
    """Generate relevant examples from the data to illustrate the issue"""
    column = violation.details['column']
    
    if violation.type == 'new_values_detected':
        new_values = profiles.get_new_values(column)
        # Get top 3 most frequent new values
        top_examples = sorted(new_values, key=lambda v: v.frequency, reverse=True)[:3]
        return {
            'examples': [str(ex.value) for ex in top_examples],
            'example_frequencies': [ex.frequency for ex in top_examples],
            'example_count': len(new_values),
            'top_example': str(top_examples[0].value) if top_examples else None
        }
    
    return {}