import os
import sys
import argparse
from profiler.profiler_entrypoint import profile_dataset

def main():
    parser = argparse.ArgumentParser(description="Run Dataset Profiler on a file.")
    parser.add_argument("file", help="Path to the dataset file (.csv or .json)")
    parser.add_argument("--summary", action="store_true", help="Print summary only")
    parser.add_argument("--output", help="Save profile output to JSON file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)

    print(f"[INFO] Profiling: {args.file}")
    try:
        profile = profile_dataset(args.file)
    except Exception as e:
        print(f"[ERROR] Failed to profile file: {e}")
        sys.exit(1)

    if args.summary:
        print("\n=== Dataset Summary ===")
        for key, val in profile.get_summary().items():
            print(f"{key}: {val}")
    else:
        print("\n=== Full Profile ===")
        print(profile.to_json())

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(profile.to_json())
        print(f"\n[INFO] Profile saved to: {args.output}")

if __name__ == "__main__":
    main()
