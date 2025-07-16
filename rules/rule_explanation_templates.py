# For missing value rate changes
"Column '{column}' missing rate increased from {previous_rate:.1%} to {current_rate:.1%}, exceeding threshold of {threshold:.1%}"

# For distribution shifts
"Distribution of '{column}' has shifted significantly (KS-stat: {ks_value:.2f}). The mean changed from {old_mean:.2f} to {new_mean:.2f}."

# For cardinality changes
"Field '{column}' lost {removed_count} previously observed values including [{examples}], potentially breaking downstream dependencies."