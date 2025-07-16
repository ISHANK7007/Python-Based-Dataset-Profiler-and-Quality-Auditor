class SchemaComparer:
    """
    Compare schemas between two DatasetProfile instances to identify
    missing, renamed, or type-changed columns.
    """
    
    def __init__(self, baseline_profile, current_profile, similarity_threshold=0.7):
        """
        Initialize with two DatasetProfile instances to compare.
        
        Args:
            baseline_profile: The baseline/reference DatasetProfile
            current_profile: The current/new DatasetProfile to compare
            similarity_threshold: Threshold for column name similarity (for rename detection)
        """
        self.baseline = baseline_profile
        self.current = current_profile
        self.similarity_threshold = similarity_threshold
        self.schema_changes = None
    
    def compare_schemas(self):
        """
        Perform schema comparison to identify all types of changes.
        """
        # Get column metadata from both profiles
        baseline_columns = self._get_column_metadata(self.baseline)
        current_columns = self._get_column_metadata(self.current)
        
        # Identify direct matches (same name)
        baseline_col_names = set(baseline_columns.keys())
        current_col_names = set(current_columns.keys())
        
        # 1. Find exact matches and type changes
        common_columns = baseline_col_names.intersection(current_col_names)
        type_changes = {
            col: {
                'baseline_type': baseline_columns[col]['type'],
                'current_type': current_columns[col]['type']
            }
            for col in common_columns
            if baseline_columns[col]['type'] != current_columns[col]['type']
        }
        
        # 2. Find missing columns
        missing_columns = baseline_col_names - current_col_names
        
        # 3. Find new columns
        new_columns = current_col_names - baseline_col_names
        
        # 4. Detect potential renames
        potential_renames = self._detect_potential_renames(
            missing_columns, new_columns, baseline_columns, current_columns
        )
        
        # 5. Track "truly missing" columns (those not likely renamed)
        truly_missing = set(missing_columns) - set(col for col, _ in potential_renames)
        
        # 6. Track "truly new" columns (those not likely from renames)
        truly_new = set(new_columns) - set(new_col for _, new_col in potential_renames)
        
        # Store all changes
        self.schema_changes = {
            'type_changes': type_changes,
            'missing_columns': list(truly_missing),
            'new_columns': list(truly_new),
            'potential_renames': potential_renames
        }
        
        return self.schema_changes
    
    def _get_column_metadata(self, profile):
        """
        Extract relevant column metadata from a profile.
        """
        columns = {}
        for col_name in profile.get_column_names():
            col_profile = profile.get_column_profile(col_name)
            columns[col_name] = {
                'type': col_profile.inferred_type,
                'stats': {
                    'count': col_profile.count,
                    'missing': col_profile.missing_count,
                    'unique': getattr(col_profile, 'unique_count', None),
                    'min': getattr(col_profile, 'min_value', None),
                    'max': getattr(col_profile, 'max_value', None),
                }
            }
        return columns
    
    def _detect_potential_renames(self, missing_columns, new_columns,
                                 baseline_columns, current_columns):
        """
        Detect potential column renames by analyzing:
        1. String similarity between column names
        2. Statistical similarity between column distributions
        3. Semantic/content similarity
        
        Returns a list of (old_name, new_name, confidence) tuples
        """
        potential_renames = []
        
        # Calculate similarity between each missing and new column
        for old_col in missing_columns:
            old_type = baseline_columns[old_col]['type']
            old_stats = baseline_columns[old_col]['stats']
            
            candidates = []
            
            for new_col in new_columns:
                new_type = current_columns[new_col]['type']
                new_stats = current_columns[new_col]['stats']
                
                # Skip if types are completely incompatible
                if not self._are_types_compatible(old_type, new_type):
                    continue
                
                # Calculate name similarity
                name_similarity = self._calculate_name_similarity(old_col, new_col)
                
                # Calculate statistical similarity
                stat_similarity = self._calculate_statistical_similarity(
                    old_stats, new_stats
                )
                
                # Calculate overall similarity
                # 60% weight on statistical similarity, 40% on name similarity
                overall_similarity = 0.4 * name_similarity + 0.6 * stat_similarity
                
                if overall_similarity >= self.similarity_threshold:
                    candidates.append((new_col, overall_similarity))
            
            # Get the best match if any
            if candidates:
                best_match = max(candidates, key=lambda x: x[1])
                confidence = best_match[1]
                evidence = self._get_rename_evidence(old_col, best_match[0], confidence)
                potential_renames.append((old_col, best_match[0], confidence, evidence))
        
        # Sort by confidence (highest first)
        return sorted(potential_renames, key=lambda x: x[2], reverse=True)
    
    def _calculate_name_similarity(self, col1, col2):
        """
        Calculate string similarity between column names.
        Uses multiple techniques and returns the highest similarity.
        """
        from difflib import SequenceMatcher
        
        # Direct string similarity
        direct_similarity = SequenceMatcher(None, col1.lower(), col2.lower()).ratio()
        
        # Tokenized similarity (for multi-word column names)
        tokens1 = set(self._tokenize_column_name(col1))
        tokens2 = set(self._tokenize_column_name(col2))
        
        if not tokens1 or not tokens2:
            token_similarity = 0
        else:
            token_similarity = len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))
        
        return max(direct_similarity, token_similarity)
    
    def _tokenize_column_name(self, column_name):
        """
        Split column name into tokens based on common separators.
        """
        import re
        # Convert camelCase to snake_case first
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', column_name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        # Split on common separators
        return re.split(r'[_\s-]', s2)
    
    def _calculate_statistical_similarity(self, stats1, stats2):
        """
        Calculate statistical similarity between two columns.
        """
        # Start with a base similarity
        similarity = 0.0
        factors = 0
        
        # Compare count
        if stats1['count'] > 0 and stats2['count'] > 0:
            count_ratio = min(stats1['count'], stats2['count']) / max(stats1['count'], stats2['count'])
            similarity += count_ratio
            factors += 1
        
        # Compare uniqueness ratio
        if stats1['unique'] is not None and stats2['unique'] is not None:
            if stats1['count'] > 0 and stats2['count'] > 0:
                unique_ratio1 = stats1['unique'] / stats1['count']
                unique_ratio2 = stats2['unique'] / stats2['count']
                uniqueness_similarity = 1 - abs(unique_ratio1 - unique_ratio2)
                similarity += uniqueness_similarity
                factors += 1
        
        # Compare min/max for numeric columns
        if (stats1['min'] is not None and stats2['min'] is not None and
            stats1['max'] is not None and stats2['max'] is not None):
            # Only if they're actually numeric
            if all(isinstance(x, (int, float)) for x in [stats1['min'], stats1['max'], 
                                                        stats2['min'], stats2['max']]):
                # Check if ranges overlap
                if not (stats1['max'] < stats2['min'] or stats2['max'] < stats1['min']):
                    range1 = stats1['max'] - stats1['min']
                    range2 = stats2['max'] - stats2['min']
                    if range1 > 0 and range2 > 0:
                        range_overlap = (min(stats1['max'], stats2['max']) - 
                                        max(stats1['min'], stats2['min']))
                        range_similarity = range_overlap / max(range1, range2)
                        similarity += range_similarity
                        factors += 1
        
        # Compare missing value ratio
        if stats1['count'] > 0 and stats2['count'] > 0:
            missing_ratio1 = stats1['missing'] / stats1['count']
            missing_ratio2 = stats2['missing'] / stats2['count']
            missing_similarity = 1 - abs(missing_ratio1 - missing_ratio2)
            similarity += missing_similarity
            factors += 1
        
        # Return average similarity
        return similarity / max(1, factors)
    
    def _are_types_compatible(self, type1, type2):
        """
        Check if two types are potentially compatible for a rename.
        """
        # Exact match is always compatible
        if type1 == type2:
            return True
        
        # Define groups of compatible types
        numeric_types = ['integer', 'float', 'numeric']
        text_types = ['string', 'text', 'categorical']
        date_types = ['date', 'time', 'datetime', 'timestamp']
        
        # Check if types are in the same group
        for group in [numeric_types, text_types, date_types]:
            if type1 in group and type2 in group:
                return True
        
        return False
    
    def _get_rename_evidence(self, old_col, new_col, confidence):
        """
        Generate human-readable evidence for why columns are considered renamed.
        """
        evidence = []
        
        # Name similarity explanation
        name_sim = self._calculate_name_similarity(old_col, new_col)
        if name_sim > 0.5:
            evidence.append(f"Name similarity: {name_sim:.2f}")
            
            # Check for common patterns
            old_tokens = set(self._tokenize_column_name(old_col))
            new_tokens = set(self._tokenize_column_name(new_col))
            common_tokens = old_tokens.intersection(new_tokens)
            
            if common_tokens:
                evidence.append(f"Common terms: {', '.join(common_tokens)}")
        
        # Statistical similarity explanation
        old_stats = self.baseline.get_column_profile(old_col).to_dict()
        new_stats = self.current.get_column_profile(new_col).to_dict()
        
        # Type similarity
        old_type = self.baseline.get_column_profile(old_col).inferred_type
        new_type = self.current.get_column_profile(new_col).inferred_type
        
        if old_type == new_type:
            evidence.append(f"Same data type: {old_type}")
        else:
            evidence.append(f"Compatible data types: {old_type} → {new_type}")
        
        # Distinct value similarity
        if hasattr(self.baseline.get_column_profile(old_col), 'unique_count') and \
           hasattr(self.current.get_column_profile(new_col), 'unique_count'):
            old_distinct = self.baseline.get_column_profile(old_col).unique_count
            new_distinct = self.current.get_column_profile(new_col).unique_count
            
            if abs(old_distinct - new_distinct) / max(old_distinct, 1) < 0.2:
                evidence.append(f"Similar cardinality: {old_distinct} vs {new_distinct} distinct values")
        
        return evidence