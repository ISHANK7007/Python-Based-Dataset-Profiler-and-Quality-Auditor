class LazyGroupedProfileGenerator:
    def __init__(self, dataset):
        """Initialize with dataset but don't compute anything yet."""
        self.dataset = dataset
        self.computed_groups = {}
    
    def get_group_profile(self, group_by, group_value):
        """Compute profile for a specific group on demand."""
        key = (tuple(group_by) if isinstance(group_by, list) else group_by, 
              tuple(group_value) if isinstance(group_value, list) else group_value)
              
        if key not in self.computed_groups:
            # If not cached, compute it
            filtered_dataset = self._filter_dataset(self.dataset, group_by, group_value)
            self.computed_groups[key] = self._compute_profile(filtered_dataset)
            
        return self.computed_groups[key]