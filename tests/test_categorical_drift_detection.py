import argparse
import sys
import os
from datetime import datetime
from enum import Enum

class ExitCode(Enum):
    SUCCESS = 0  # No drift or only minor drift
    WARNING = 1  # Moderate drift detected
    ERROR = 2    # Major drift detected
    CRITICAL = 3 # Schema breaking changes detected
    FAILURE = 10 # Command execution failed

def create_drift_audit_parser(subparsers):
    """Create the parser for the 'drift audit' command."""
    
    parser = subparsers.add_parser(
        'audit',
        help='Audit data drift between two datasets',
        description='Compare two datasets and detect schema, distribution, and quality drift.'
    )
    
    # Required positional arguments
    parser.add_argument(
        'baseline_dataset',
        help='Baseline/reference dataset path (CSV, JSON, etc.)'
    )
    
    parser.add_argument(
        'current_dataset',
        help='Current/new dataset path to compare against baseline'
    )
    
    # Output format
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json', 'html', 'excel', 'text', 'all'],
        default='markdown',
        help='Output format for the drift report (default: markdown)'
    )
    
    # Output directory
    parser.add_argument(
        '--output-dir', '-o',
        default='./reports',
        help='Directory to save the generated reports (default: ./reports)'
    )
    
    # Output filename
    parser.add_argument(
        '--output-name',
        help='Custom name for the output file(s) (default: auto-generated from input files)'
    )
    
    # Custom thresholds
    parser.add_argument(
        '--thresholds',
        help='Path to JSON file with custom drift thresholds'
    )
    
    # Columns to include/exclude
    parser.add_argument(
        '--include-columns',
        help='Comma-separated list of columns to include in analysis'
    )
    
    parser.add_argument(
        '--exclude-columns',
        help='Comma-separated list of columns to exclude from analysis'
    )
    
    # CI/CD integration options
    parser.add_argument(
        '--exit-on-drift',
        choices=['none', 'major', 'moderate', 'minor', 'schema'],
        default='major',
        help='Exit with non-zero code on specified drift severity (default: major)'
    )
    
    parser.add_argument(
        '--summary-only', '-s',
        action='store_true',
        help='Only show summary results, useful for CI/CD pipelines'
    )
    
    # Comparison customization
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.7,
        help='Threshold for column name similarity when detecting renames (0.0-1.0)'
    )

    parser.add_argument(
        '--sample',
        type=int,
        help='Sample N rows from each dataset for faster processing'
    )
    
    # Report customization
    parser.add_argument(
        '--title',
        help='Custom title for the drift report'
    )
    
    # Visualization options
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate visualizations for detected drift'
    )
    
    parser.add_argument(
        '--no-visualize',
        action='store_true',
        help='Skip visualization generation'
    )
    
    # Stdout/stderr control
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress console output except for errors'
    )
    
    parser.add_argument(
        '--print-to-stdout',
        action='store_true',
        help='Print report to stdout instead of writing to file'
    )

    # Advanced customization
    parser.add_argument(
        '--config',
        help='Path to config file with comprehensive settings'
    )
    
    return parser