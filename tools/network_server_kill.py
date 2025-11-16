# Kill any process using port 5000 (commonly used for flask server)
# in shell: `lsof -ti tcp:5000 | xargs kill`

# stdlib imports
import os
import signal
import subprocess
import sys

# pip imports
import argparse

# =============================================================================
#
# =============================================================================


def main() -> int:

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Kill any process using port 5000 (commonly used for flask server).")
    args = parser.parse_args()

    port = 5000

    try:
        # Get the list of process IDs using the specified port
        result = subprocess.run(["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True)
        pids = result.stdout.strip().split("\n")

        if pids == [""]:
            print(f"No processes found using port {port}.")
            return 0

        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)
            print(f"Killed process with PID: {pid} using port {port}.")

        return 0

    except Exception as error:
        print(f"An error occurred: {error}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
