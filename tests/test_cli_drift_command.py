import argparse
import sys

from cli.cli_drift_command import run_drift_audit
from cli.cli_drift_flags import create_drift_audit_parser
from cli.cli_exit_codes import ExitCode

def main():
    """Main entry point for the dsqa CLI."""
    parser = argparse.ArgumentParser(
        description='DSQA - Data Science Quality Assurance Toolkit',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Add 'drift' command
    drift_parser = subparsers.add_parser('drift', help='Data drift detection commands')
    drift_subparsers = drift_parser.add_subparsers(dest='subcommand')

    # Add 'audit' subcommand to 'drift'
    create_drift_audit_parser(drift_subparsers)

    # Add other commands here...

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(ExitCode.SUCCESS.value)

    if args.command == 'drift':
        if args.subcommand == 'audit':
            exit_code = run_drift_audit(args)
            sys.exit(exit_code.value)
        else:
            drift_parser.print_help()
            sys.exit(ExitCode.SUCCESS.value)

    # Add other command branches as needed...

    print("Unknown command. Use --help to see available options.")
    sys.exit(ExitCode.FAILURE.value)


if __name__ == '__main__':
    main()
