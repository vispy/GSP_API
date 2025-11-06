"""
Run all example scripts in this directory sequentially.
It helps testing that all examples run without errors.
"""

# stdlib imports
import subprocess
import sys
import os
import colorama

# pip imports
import argparse

__dirname__ = os.path.dirname(os.path.abspath(__file__))


# =============================================================================
# Colorama alias
# =============================================================================
def text_cyan(text: str) -> str:
    return colorama.Fore.CYAN + text + colorama.Style.RESET_ALL


def text_green(text: str) -> str:
    return colorama.Fore.GREEN + text + colorama.Style.RESET_ALL


def text_red(text: str) -> str:
    return colorama.Fore.RED + text + colorama.Style.RESET_ALL


# =============================================================================
# launch example script
# =============================================================================
def launch_example(cmdline_args: list[str]) -> bool:
    """
    Launches the example script with the given command line arguments.

    Arguments:
        cmdline_args: List of command line arguments to pass to the script.

    Returns:
        True if the script ran successfully, False otherwise.
    """
    try:
        # Add a environment variable to disable interactive mode in the example
        env = dict(**os.environ, GSP_UUID_COUNTER="True", GSP_INTERACTIVE_MODE="False")

        result = subprocess.run(
            cmdline_args,
            check=True,  # Raises CalledProcessError if script fails
            capture_output=True,
            text=True,  # Capture output as string instead of bytes
            env=env,
        )
        # print("Script B ran successfully.")
        # print("Output:", result.stdout)
        run_success = True if result.returncode == 0 else False

    except subprocess.CalledProcessError as e:
        # print("Script B failed!")
        # print("Error Output:", e.stderr)
        run_success = False

    return run_success


###############################################################################
# Main script logic
#


def split_argv():
    if "--" not in sys.argv:
        local_args = sys.argv[1:]
        example_args = []
    else:
        separator_index = sys.argv.index("--")
        local_args = sys.argv[1:separator_index]
        example_args = sys.argv[separator_index + 1 :]
    return local_args, example_args


def main() -> None:
    # Split local args and launcher.py args
    local_args, example_args = split_argv()

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Run all example scripts in this directory.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with more verbose output.")
    args = parser.parse_args(local_args)

    # Set debug mode
    if args.debug:
        print("Debug mode is enabled.")

    # get script paths in the examples folder
    examples_folder = f"{__dirname__}/../examples"
    basenames = [basename for basename in os.listdir(examples_folder) if os.path.isfile(os.path.join(examples_folder, basename))]
    basenames.sort()
    script_paths = [os.path.abspath(os.path.join(examples_folder, basename)) for basename in basenames if basename.endswith(".py")]

    print(f"Running {text_cyan(str(len(script_paths)))} example scripts to verify they execute without exceptions.")

    project_rootpath = os.path.abspath(os.path.join(__dirname__, ".."))
    for script_path in script_paths:
        # display the basename of the script without new line, and flush the output
        basename_script = os.path.basename(script_path)
        script_relpath = os.path.relpath(script_path, start=project_rootpath)

        print(f"Running {text_cyan(script_relpath)} ... ", end="", flush=True)

        # launch the example script
        run_success = launch_example([sys.executable, script_path, *example_args])

        # display X in red if failed, or a check in green if successful
        if run_success:
            print(f"{text_green('OK')}")
        else:
            print(f"{text_red('Failed')}")

        if not run_success:
            sys.exit(1)

    print(f"All {text_cyan(str(len(script_paths)))} example scripts ran successfully. {text_green('OK')}")


if __name__ == "__main__":
    main()
