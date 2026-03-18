import argparse
import os
import sys
from pathlib import Path
from mapmycode.main import main as analyze_codebase

def check_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.")
        print("\nPlease set your GROQ API key:")
        print(" Windows Powershell: $env:GROQ_API_KEY = 'your_api_key_here'")
        print(" Windows CMD: set GROQ_API_KEY=your_api_key_here")
        print(" Linux/macOS: export GROQ_API_KEY='your_api_key_here'")
        sys.exit(1)

    return api_key

def main():
    parser = argparse.ArgumentParser(
        description="MapMyCode - Analyze Python codebases and generate documentation with dependency graphs.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
    Example usage:
    mapmycode .                  # Analyze current directory
    mapmycode /path/to/project   #Analyze specific path
        """
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the analyze (default: current directory)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    check_api_key()

    path = os.path.abspath(args.path)
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        sys.exit(1)

    print(f"\n Analyzing codebase at: {path}")
    print("-" * 60)

    try : 
        analyze_codebase(path)
        print("\n" + "-" * 60)
        print("Analysis complete! Documentation and dependency graph generated.")
        print(f"\n Results saved to: {path}")
        print("\n Thank you for using MapMyCode!")

    except Exception as e:
        print(f"\n Error : {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()