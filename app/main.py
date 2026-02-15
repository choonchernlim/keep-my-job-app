import sys
import subprocess
from pathlib import Path


def main():
    # The directory where main.py is located (app/)
    app_dir = Path(__file__).parent
    
    # The directory where the agent is located (app/adk/)
    # adk web expects to be run from here to pick up .env and agent definitions correctly
    adk_dir = app_dir / "adk"

    print(f"Starting ADK Web Server in {adk_dir}...")
    
    try:
        # Run 'adk web' with any additional arguments passed to this script
        # check=True ensures we catch non-zero exit codes
        subprocess.run(["adk", "web"] + sys.argv[1:], cwd=adk_dir, check=True)
    except KeyboardInterrupt:
        print("\nStopping ADK Web Server...")
    except FileNotFoundError:
        print("Error: 'adk' command not found. Ensure dependencies are installed and you are running in the virtual environment.")
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
