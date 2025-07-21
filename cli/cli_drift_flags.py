class SchemaEvolution:
    """
    Track schema changes over time and provide guidance for managing schema evolution.
    """
    
    def __init__(self, schema_version="1.0"):
        self.schema_version = schema_version
        self.change_history = []
    
    def add_schema_comparison(self, comparison, timestamp=None):
        """
        Add a schema comparison to the history.
        """
        if timestamp is None:
            import datetime
            timestamp = datetime.datetime.now()
        
        self.change_history.append({
            'timestamp': timestamp,
            'changes': comparison,
        })
        
        # Update schema version
        self.schema_version = self._increment_version(self.schema_version)
        
        return self.schema_version
    
    def _increment_version(self, version):
        """
        Increment schema version based on changes.
        - Major version: Breaking changes (removed columns, type changes)
        - Minor version: Compatible changes (added columns, renames with high confidence)
        """
        major, minor = map(int, version.split('.'))
        
        # Check last changes for breaking changes
        last_changes = self.change_history[-1]['changes']
        
        has_breaking_changes = (
            len(last_changes['missing_columns']) > 0 or
            len(last_changes['type_changes']) > 0
        )
        
        if has_breaking_changes:
            return f"{major + 1}.0"  # Major version bump
        else:
            return f"{major}.{minor + 1}"  # Minor version bump