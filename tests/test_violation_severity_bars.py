import argparse

def parse_chart_cli_flags():
    """
    Parse CLI flags related to chart rendering presets and output controls.
    Returns:
        argparse.Namespace: Parsed CLI arguments with chart-related options.
    """
    parser = argparse.ArgumentParser(
        description="Run dataset audit with visual reporting options"
    )

    # Chart preset flag
    parser.add_argument(
        '--chart-preset',
        type=str,
        choices=['minimal', 'basic', 'standard', 'comprehensive'],
        default='standard',
        help=(
            'Preset level of chart detail to include in the report: '
            "'minimal' = only summary charts, "
            "'basic' = summary + key fields, "
            "'standard' = recommended default set, "
            "'comprehensive' = all available charts"
        )
    )

    # Output format flag
    parser.add_argument(
        '--output-format',
        choices=['html', 'markdown'],
        default='html',
        help='Output format for the report'
    )

    # Optional flag to disable charts entirely
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='Disable chart rendering entirely (overrides presets)'
    )

    # Parse known args to allow CLI chaining
    return parser.parse_args()
