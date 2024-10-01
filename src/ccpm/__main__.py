import subprocess
import os
import sys
import toml
import shutil
import argparse
import hashlib
from urllib.parse import urlparse

PREFIX = "ccpm"


def invalid_folder(path):
    return (not os.path.exists(path)) or (not os.listdir(path))


def run_command_silent_unchecked(command):
    out = subprocess.DEVNULL
    return subprocess.call(command, shell=True, stdout=out, stderr=out)


def run_command(command, cwd=None, quiet=False):
    # print(f"[>] Running cmd: {' '.join(command)}")
    out = None if not quiet else subprocess.DEVNULL
    try:
        subprocess.check_call(command, stdout=out, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error: On last command, exited with code {e.returncode}")
        sys.exit(e.returncode)


def extract_repo_name(repo_url):
    path = ""
    # Is http[s] url
    if repo_url.startswith("http://") or repo_url.startswith("https://"):
        parsed_url = urlparse(repo_url)
        path = parsed_url.path.lstrip("/")
    # Is ssh url
    else:
        path = repo_url.split(":", 1)[1]
    # Remove.git if present
    if path.endswith(".git"):
        path = path[:-4]
    return path


def process_package(repo_url, tag, defines, download_prefix, install_prefix):

    repo_name = extract_repo_name(repo_url)

    project_name = repo_name.split("/")[-1]

    to_hash = [repo_url, tag, *defines]
    build_hash = hashlib.sha1("_".join(to_hash).encode("utf-8")).hexdigest()

    source_dir = f"{download_prefix}/{project_name}/{tag}"  # the clone happens here
    build_dir = f"{download_prefix}/{project_name}/__{build_hash}"
    install_dir = f"{install_prefix}/{project_name}"

    print(f'\n[{PREFIX.upper()}] :: {project_name}/{tag} : {" ".join(defines)}')

    # 1) Check if the repository and tag combination is cloned or clone it
    if invalid_folder(source_dir):
        os.makedirs(source_dir, exist_ok=True)
        print(f"[+] Cloning repository {repo_url} at tag {tag} into {source_dir}")
        clone_cmd = [
            "git",
            "clone",
            "--recurse-submodules",
            repo_url,
            "--branch",
            tag,
            "--depth",
            "1",
            source_dir,
        ]
        run_command(clone_cmd)

    if not invalid_folder(install_dir):
        shutil.rmtree(install_dir)
    os.makedirs(install_dir, exist_ok=True)

    for build_type in ["Debug", "Release"]:
        build_dir_type = f"{build_dir}/{build_type}"
        install_dir_type = f"{install_dir}/{build_type}"

        # 2) Build the project
        if invalid_folder(build_dir_type):
            print(f"[+] Building for :: {build_type}")
            os.makedirs(build_dir_type, exist_ok=True)

            # Run cmake configuration
            print("[++] Running configure step")
            cmake_cmd = [
                "cmake",
                source_dir,
                f"-DCMAKE_BUILD_TYPE={build_type}",
                *defines,
            ]
            run_command(cmake_cmd, cwd=build_dir_type)

            # Build the project
            print("[++] Running build step")
            build_cmd = [
                "cmake",
                "--build",
                ".",
                "-j",
                "16",
                "--config",
                build_type,
            ]
            run_command(build_cmd, cwd=build_dir_type)

        # 3) Install the project
        print(f"[+] Installing for :: {build_type}")
        install_cmd = [
            "cmake",
            "--install",
            ".",
            "--config",
            build_type,
            "--prefix",
            install_dir_type,
        ]
        run_command(install_cmd, cwd=build_dir_type, quiet=True)

    return install_dir


def process_toml(root_dir, download_prefix, install_prefix):
    # Load packages from TOML file
    toml_file = f"{root_dir}/{PREFIX}.toml"
    if not os.path.exists(toml_file):
        print(f'Error: TOML file "{toml_file}" not found.')
        sys.exit(1)

    try:
        with open(toml_file, "r") as f:
            config = toml.load(f)
    except Exception as e:
        print(f"Error reading TOML file: {e}")
        sys.exit(1)

    git_pkgs = config.get("git", [])
    if not git_pkgs:
        print('"[[git]]" not found in the TOML file.')
        sys.exit(1)

    packages_path = []

    for pkg in git_pkgs:
        repo_url = pkg.get("repo_url")
        tag = pkg.get("tag")
        defines = pkg.get("defines", [])

        if not repo_url or not tag:
            print("Package definition must include 'repo_url' and 'tag'.")
            continue

        # Prepare defines
        cmake_defines = [f"-D{define}" for define in defines]

        # Process the package
        packages_path.append(
            process_package(
                repo_url, tag, cmake_defines, download_prefix, install_prefix
            )
        )

    return packages_path


def gen_cmake_script(root_dir, install_dir, packages_path):

    output_file = f"{install_dir}/{PREFIX}.cmake"

    if os.path.exists(output_file) and os.path.isfile(output_file):
        os.remove(output_file)

    cmake_script = ""

    cmake_script += """
string(TOLOWER "${CMAKE_BUILD_TYPE}" CCPM_BUILD_TYPE_LOWER)
if(BUILD_TYPE_LOWER MATCHES "debug")
    SET(CCPM_BUILD_ID Debug)
else()
    SET(CCPM_BUILD_ID Release)
endif()
"""

    cmake_script += "\n# Add to prefix path\n"
    for pkg_path in packages_path:
        pkg_path_cmake = pkg_path.replace(root_dir, "${CMAKE_SOURCE_DIR}")
        cmake_script += (
            f'list(APPEND CMAKE_PREFIX_PATH "{pkg_path_cmake}/${{CCPM_BUILD_ID}}")\n'
        )

    # cmake_script += f"\n# Find packages\n"
    # for pkg_name in PACKAGES_NAMES:
    #     # Known expceptions
    #     if (pkg_name == "glfw"):
    #         cmake_script += "find_package(glfw3 REQUIRED)\n"
    #     # Any other case
    #     else:
    #         cmake_script += f"find_package({pkg_name} REQUIRED)\n"

    # cmake_script += f"\n# Put all the libraries on variable\n"
    # to_link_libraries = set()
    # for pkg_name in PACKAGES_NAMES:
    #     # Known expceptions
    #     if (pkg_name == "glfw"):
    #         to_link_libraries.add("glfw")
    #     # Any other case
    #     else:
    #         to_link_libraries.add(f"{pkg_name}::{pkg_name}")
    # cmake_script += f"list(APPEND CCPM_LINK_LIBRARIES {' '.join(to_link_libraries)})\n"

    os.makedirs(f"{install_dir}", exist_ok=True)
    with open(output_file, "w") as f:
        f.write(cmake_script)


def do_project_build(root_dir, project_build_dir, build_type):
    print(f"[{PREFIX.upper()}] :: Building current project")
    run_command(
        [
            "cmake",
            "-S",
            root_dir,
            "-B",
            project_build_dir,
            f"-DCMAKE_BUILD_TYPE={build_type}",
        ]
    )
    run_command(
        [
            "cmake",
            "--build",
            project_build_dir,
            "-j",
            "16",
            "--config",
            build_type,
        ]
    )


def main():

    # ARGS ################################################################

    # Define arguments
    parser = argparse.ArgumentParser(description="Manage your Cmake project")
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=".",
        help=f"Where the {PREFIX}.toml is and install will be",
    )
    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        default=False,
        help="Clear build and external dependencies",
    )
    parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        default=False,
        help="Install dependencies (not needed if you don't change the TOML)",
    )
    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        default=False,
        help="Specify if you want to build your CMakeList.txt (default Debug)",
    )
    parser.add_argument(
        "-r",
        "--release",
        action="store_true",
        default=False,
        help="If build process is requested, build type will be Release",
    )

    # Check cli commands
    if run_command_silent_unchecked("cmake --version") != 0:
        parser.error("Install CMake first")

    if run_command_silent_unchecked("git --version") != 0:
        parser.error("Install Git first")

    # Parse arguments
    args = parser.parse_args()

    a_clear = args.clear
    a_install = args.install

    a_path = args.path
    if invalid_folder(a_path) or (not os.path.exists(f"{a_path}/{PREFIX}.toml")):
        parser.error(
            f"Invalid path, folder doesn't exist or not contains a '{PREFIX}.toml' file"
        )

    a_build = args.build
    a_build_type = "Release" if args.release else "Debug"

    home_dir = os.path.expanduser("~").replace("\\", "/")
    download_dir_prefix = f"{home_dir}/.{PREFIX}"

    root_dir = os.path.abspath(a_path).replace("\\", "/")
    install_dir_prefix = f"{root_dir}/.{PREFIX}"

    project_build_dir = f"{root_dir}/build"
    print(f"project_build_dir :: {project_build_dir}")

    # CLEAR ALL ###########################################################

    # Deps
    if a_clear and not invalid_folder(install_dir_prefix):
        shutil.rmtree(install_dir_prefix)

    # Build
    if a_clear and not invalid_folder(project_build_dir):
        shutil.rmtree(project_build_dir)

    # INSTALL DEPS ########################################################

    if a_install:
        packages_path = process_toml(root_dir, download_dir_prefix, install_dir_prefix)
        gen_cmake_script(root_dir, install_dir_prefix, packages_path)
        print()

    # BUILD CURRENT PROJECT ###############################################

    if a_build:
        do_project_build(root_dir, project_build_dir, a_build_type)
        print()


if __name__ == "__main__":
    main()
