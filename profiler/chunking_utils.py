def determine_optimal_chunk_size(df, available_memory):
    """Determine optimal chunk size based on dataframe and memory constraints."""
    row_size_estimate = df.memory_usage(deep=True).sum() / len(df)
    
    # Target using 25% of available memory for chunk
    target_rows = (available_memory * 0.25) / row_size_estimate
    
    # Round to reasonable chunk size between 1,000 and 100,000
    return max(1000, min(100000, int(target_rows)))