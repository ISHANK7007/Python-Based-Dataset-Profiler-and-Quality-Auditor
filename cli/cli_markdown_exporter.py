class SchemaMigrationGenerator:
    """
    Generate migration code to handle schema changes.
    """
    
    def __init__(self, schema_comparer):
        """
        Initialize with a completed schema comparison.
        """
        self.comparison = schema_comparer.schema_changes
        self.baseline_profile = schema_comparer.baseline
        self.current_profile = schema_comparer.current
    
    def generate_pandas_migration_code(self):
        """
        Generate pandas code to migrate from baseline to current schema.
        """
        migration_code = [
            "# Auto-generated schema migration code",
            "# From schema version: {previous_version}",
            "# To schema version: {current_version}",
            "",
            "def migrate_dataframe(df):",
            "    \"\"\"",
            "    Migrate a dataframe from previous schema to current schema.",
            "    \"\"\"",
            "    # Make a copy to avoid modifying the original",
            "    df = df.copy()",
            ""
        ]
        
        # Handle renames
        if self.comparison['potential_renames']:
            migration_code.append("    # Handle column renames")
            for old_col, new_col, confidence, _ in self.comparison['potential_renames']:
                if confidence > 0.8:  # Only include high confidence renames
                    migration_code.append(f"    if '{old_col}' in df.columns:")
                    migration_code.append(f"        df['{new_col}'] = df['{old_col}']")
                    migration_code.append(f"        df = df.drop(columns=['{old_col}'])")
                    migration_code.append("")
        
        # Handle type changes
        if self.comparison['type_changes']:
            migration_code.append("    # Handle type changes")
            for col, type_info in self.comparison['type_changes'].items():
                base_type = type_info['baseline_type']
                current_type = type_info['current_type']
                
                migration_code.append(f"    if '{col}' in df.columns:")
                
                if current_type == 'integer':
                    migration_code.append(f"        df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce').fillna(0).astype('int')")
                elif current_type == 'float':
                    migration_code.append(f"        df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce')")
                elif current_type == 'datetime':
                    migration_code.append(f"        df['{col}'] = pd.to_datetime(df['{col}'], errors='coerce')")
                elif current_type == 'boolean':
                    migration_code.append(f"        df['{col}'] = df['{col}'].astype('str').str.lower()")
                    migration_code.append(f"        df['{col}'] = df['{col}'].map({{'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False}})")
                    migration_code.append(f"        df['{col}'] = df['{col}'].fillna(False)")
                else:
                    migration_code.append(f"        df['{col}'] = df['{col}'].astype('str')")
                
                migration_code.append("")
        
        # Add missing columns with default values
        if self.comparison['missing_columns']:
            migration_code.append("    # Add columns that are missing in the input")
            for col in self.comparison['missing_columns']:
                col_profile = self.current_profile.get_column_profile(col)
                col_type = col_profile.inferred_type
                
                default_value = "None"
                if col_type == 'integer':
                    default_value = "0"
                elif col_type == 'float':
                    default_value = "0.0"
                elif col_type == 'boolean':
                    default_value = "False"
                elif col_type == 'string':
                    default_value = "''"
                elif col_type == 'datetime':
                    default_value = "pd.NaT"
                
                migration_code.append(f"    if '{col}' not in df.columns:")
                migration_code.append(f"        df['{col}'] = {default_value}")
                migration_code.append("")
        
        # Return final code
        migration_code.append("    return df")
        
        return "\n".join(migration_code)