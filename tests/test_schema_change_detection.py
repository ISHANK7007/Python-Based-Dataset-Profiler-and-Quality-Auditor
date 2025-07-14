import json

def to_monitoring_json(self):
    """
    Generate a monitoring-optimized JSON with alerts and thresholds.
    Designed for integration with monitoring systems.
    """
    monitoring_data = {
        'timestamp': self.timestamp.isoformat() if hasattr(self, 'timestamp') else None,
        'dataset_id': self.metadata.get('current_dataset', 'unknown'),
        'alerts': [],
        'metrics': {}
    }

    # Convert findings to alerts
    for drift_type, severity_dict in self.findings.items():
        for severity in ['major', 'moderate']:
            for finding in severity_dict.get(severity, []):
                monitoring_data['alerts'].append({
                    'column': finding.get('column', 'unknown'),
                    'drift_type': drift_type,
                    'severity': severity,
                    'description': finding.get('description', '')
                })

    # Add key metrics for time-series tracking
    if hasattr(self, 'calculate_overall_drift_score'):
        monitoring_data['metrics']['drift_score'] = self.calculate_overall_drift_score()
    else:
        monitoring_data['metrics']['drift_score'] = 0.0

    if hasattr(self, 'calculate_schema_stability'):
        monitoring_data['metrics']['schema_stability'] = self.calculate_schema_stability()
    else:
        monitoring_data['metrics']['schema_stability'] = 1.0

    return json.dumps(monitoring_data, indent=2)
