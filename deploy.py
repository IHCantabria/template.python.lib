import os
import argparse
from pathlib import Path

project_name = "templatelib"


def _check_args(args):
    """Check if any of the arguments is passed"""
    if not any([args.major, args.minor, args.patch]):
        raise Exception("Please specify a version type to update.")
        exit(1)


def parse_args():
    """Parse the arguments passed to the script"""

    parser = argparse.ArgumentParser()

    # Add a new argument to the parser for major version
    parser.add_argument("--major", action="store_true")

    # Add a new argument to the parser for minor version
    parser.add_argument("--minor", action="store_true")

    # Add a new argument to the parser for patch version
    parser.add_argument("--patch", action="store_true")

    args = parser.parse_args()
    _check_args(args)
    return args


def calculate_new_version(old_version: str):

    version = old_version.split(".")
    if args.major:
        version[0] = str(int(version[0]) + 1)
        version[1] = "0"
        version[2] = "0"
        return ".".join(version)
    if args.minor:
        version[1] = str(int(version[1]) + 1)
        version[2] = "0"
        return ".".join(version)
    if args.patch:
        version[2] = str(int(version[2]) + 1)
        return ".".join(version)


def validate_all_is_ok():
    """Validate that all is ok before deploying"""

    # Check if there are any changes in the repository
    if os.system("git diff-index --quiet HEAD --") != 0:
        raise Exception(
            "There are changes in the repository. Please commit them before deploying."
        )
        exit(1)

    # Run tests

    if os.system("pytest") != 0:
        raise Exception("Tests failed. Please fix them before deploying.")
        exit(1)


def write_new_version(init_path, version):
    """Write new version to __init__.py"""

    with open(init_path, "r") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if "__version__" in line:
            line = f'__version__ = "{version}"'
        new_lines.append(line)

    with open(init_path, "w") as f:
        f.writelines(new_lines)


# Commit changes and create a new tag
def run_git_commands(init_path, version):
    commands = [
        f"git add {init_path.as_posix()}",
        "git commit -m 'Bump version to {0}'".format(version),
        "git tag -a v{0} -m 'Version {0}'".format(version),
        "git push origin tag v{0}".format(version),
        "git push",
    ]
    for command in commands:
        os.system(command)


def get_version(init_path: Path, args):
    """Find the current version of the package"""
    with open(init_path, "r") as f:
        for line in f:
            if "__version__" in line:
                return line.split("=")[1].strip().strip('"')


def find_init_file():
    """Find all __init__.py files in the project"""
    init_files = []
    entries = os.listdir("src")
    for entry in entries:
        entry_path = Path("src", entry)
        if entry_path.is_dir():
            init_path = Path(entry_path, "__init__.py")
            if init_path.exists():
                init_files.append(init_path)

    if not init_files:
        raise Exception("No __init__.py files found in the project.")
    elif len(init_files) > 1:
        raise Exception(
            f"Multiple __init__.py files found in the project: {init_files}"
        )
    return init_files[0]


if __name__ == "__main__":
    args = parse_args()
    validate_all_is_ok()
    init_path = find_init_file()
    original_version = get_version(init_path, args)
    new_version = calculate_new_version(original_version)
    write_new_version(init_path, new_version)
    run_git_commands(init_path, new_version)
