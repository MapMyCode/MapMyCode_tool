import argparse
import os
import sys
from pathlib import Path
from mapmycode.main import main as analyze_codebase

def check_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.",file=sys.stderr)
        print("\nPlease set your GROQ API key:",file=sys.stderr)
        print(" Windows Powershell: $env:GROQ_API_KEY = 'your_api_key_here'",file=sys.stderr)
        print(" Windows CMD: set GROQ_API_KEY=your_api_key_here",file=sys.stderr)
        print(" Linux/macOS: export GROQ_API_KEY='your_api_key_here'",file=sys.stderr)
        sys.exit(1)

    return api_key

def main():
    parser = argparse.ArgumentParser(
        description="MapMyCode - Analyze Python codebases and generate documentation with dependency graphs.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
    Example usage:
    mapmycode .                  # Analyze current directory
    mapmycode . sample_output    # Analyze current directory and save in custom folder
        """
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the analyze (default: current directory)"
    )

    parser.add_argument(
        "--output",
        default="mapmycode_output",
        help="Output directory"
    )

    args = parser.parse_args()

    check_api_key()

    path = os.path.abspath(args.path)
    output_path = os.path.abspath(args.output)
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.",file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(output_path):
        os.makedirs(output_path,exist_ok=True)

    print(f"\n Analyzing codebase at: {path}")
    print("-" * 60)

    try : 
        analyze_codebase(path,output_path)
        print("\n" + "-" * 60)
        print("Analysis complete! Documentation and dependency graph generated.")
        print(f"\n Results saved to: {output_path}")
        print("\n Thank you for using MapMyCode!")

    except Exception as e:
        print(f"Error during analysis: {e}",file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()