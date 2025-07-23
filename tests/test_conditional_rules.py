class ValidationPlanner:
    """Plan validation execution for optimal performance."""
    
    def create_execution_plan(self, expectations, dataset):
        """
        Create an optimal execution plan for validating expectations.
        
        Args:
            expectations: List of expectations to validate
            dataset: Dataset to validate
        """
        # Analyze dataset characteristics
        dataset_stats = self._analyze_dataset(dataset)
        
        # Analyze expectations
        exp_stats = self._analyze_expectations(expectations)
        
        # Create plan
        plan = self._generate_plan(expectations, dataset_stats, exp_stats)
        
        return plan
    
    def _analyze_dataset(self, dataset):
        """Analyze dataset to determine best processing strategy."""
        stats = {
            "size": self._estimate_size(dataset),
            "width": self._count_columns(dataset),
            "storage_type": self._determine_storage_type(dataset),
            "indexable": self._is_indexable(dataset)
        }
        return stats
    
    def _analyze_expectations(self, expectations):
        """Analyze expectations for optimization opportunities."""
        # Count by type, check independence, etc.
        return {
            "by_type": self._group_by_type(expectations),
            "column_coverage": self._calculate_column_coverage(expectations),
            "can_parallelize": self._check_parallelization(expectations),
            "metric_dependencies": self._extract_metric_dependencies(expectations)
        }
    
    def _generate_plan(self, expectations, dataset_stats, exp_stats):
        """Generate an execution plan based on analysis."""
        plan = {
            "stages": [],
            "metrics_to_compute": set()
        }
        
        # Determine processing mode
        if dataset_stats["size"] < 1e6:  # Small dataset
            plan["processing_mode"] = "in_memory"
        elif dataset_stats["width"] > 100:  # Wide dataset
            plan["processing_mode"] = "columnar_chunks"
        else:
            plan["processing_mode"] = "streaming"
            
        # Group expectations for efficient processing
        column_groups = exp_stats["column_coverage"]
        for column, exps in column_groups.items():
            metrics = self._determine_required_metrics(exps)
            plan["metrics_to_compute"].update(metrics)
            
            stage = {
                "column": column,
                "expectations": exps,
                "metrics": metrics
            }
            plan["stages"].append(stage)
            
        # Determine parallelization strategy
        if exp_stats["can_parallelize"] and dataset_stats["size"] > 1e6:
            plan["parallelization"] = {
                "enabled": True,
                "workers": min(len(plan["stages"]), 8)
            }
        else:
            plan["parallelization"] = {"enabled": False}
            
        return plan