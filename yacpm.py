import subprocess
import os
import sys
import toml
import shutil
import argparse
from urllib.parse import urlparse

PREFIX = "yacpm"
HOME_DIR = os.path.expanduser("~").replace('\\', '/')
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')

BUILD_DIR_PREFIX = f'{HOME_DIR}/.{PREFIX}'
INSTALL_DIR_PREFIX = f'{SCRIPT_DIR}/.{PREFIX}'

PACKAGES_NAMES = set()
PACKAGES_PATHS = set()

def invalid_folder(path):
    return (not os.path.exists(path)) or (not os.listdir(path))

def run_command(command, cwd=None, quiet=False):
    """Run a system command in a subprocess."""
    # cmd_display = ' '.join(command).replace(SCRIPT_DIR, ".").replace(HOME_DIR, "~")
    # cwd_display = cwd.replace(SCRIPT_DIR, ".").replace(HOME_DIR, "~") if cwd else '.'
    # print(f'[>] Running command: "{cmd_display}" @ "{cwd_display}"')
    try:
        if quiet:
            subprocess.check_call(command, stdout=subprocess.DEVNULL, cwd=cwd)
        else:
            subprocess.check_call(command, cwd=cwd)
    except subprocess.CalledProcessError as e:
        # print(f'Error: Command "{cmd_display}" exited with code {e.returncode}')
        print(f'Error: On last command, exited with code {e.returncode}')
        sys.exit(e.returncode)

def extract_repo_name(repo_url):
    path = ""
    # Is http[s] url
    if repo_url.startswith('http://') or repo_url.startswith('https://'):
        parsed_url = urlparse(repo_url)
        path = parsed_url.path.lstrip('/')
    # Is ssh url
    else:
        path = repo_url.split(':', 1)[1]
    # Remove.git if present
    if path.endswith('.git'):
        path = path[:-4]
    return path

def process_package(repo_url, tag, defines):

    # Folders
    repo_name = extract_repo_name(repo_url)

    project_name = repo_name.split('/')[-1]
    PACKAGES_NAMES.add(project_name)

    project_and_tag = f'{project_name}-{tag}'
    source_dir  = f'{BUILD_DIR_PREFIX}/{project_and_tag}/src'
    build_dir   = f'{BUILD_DIR_PREFIX}/{project_and_tag}/build'

    install_dir = f'{INSTALL_DIR_PREFIX}/{project_and_tag}'
    PACKAGES_PATHS.add(install_dir)

    print(f'\n[{PREFIX.upper()}] :: {project_and_tag} : {" ".join(defines)}')

    # Step 2: Check if the repository and tag combination is cloned or clone it
    if invalid_folder(source_dir):
        os.makedirs(source_dir, exist_ok=True)
        print(f'[+] Cloning repository {repo_url} at tag {tag} into {source_dir}')
        clone_cmd = ['git', 'clone', repo_url, '--branch', tag, '--depth', '1', source_dir]
        run_command(clone_cmd)

    if not invalid_folder(install_dir):
        shutil.rmtree(install_dir)
    os.makedirs(install_dir, exist_ok=True)

    for build_type in ['Debug', 'Release']:
        build_dir_type = f'{build_dir}/{build_type}'

        # Step 3: Build the project
        if invalid_folder(build_dir_type):
            print(f'[+] Building for :: {build_type}')
            os.makedirs(build_dir_type, exist_ok=True)

            # Run cmake configuration
            print('[++] Running configure step')
            cmake_cmd = ['cmake', source_dir, f'-DCMAKE_BUILD_TYPE={build_type}', *defines]
            run_command(cmake_cmd, cwd=build_dir_type)

            # Build the project
            print('[++] Running build step')
            build_cmd = ['cmake', '--build', '.', '-j', '16','--config', build_type]
            run_command(build_cmd, cwd=build_dir_type)

        # Step 4: Install the project
        print(f'[+] Installing for :: {build_type}')
        install_cmd = ['cmake', '--install', '.', '--config', build_type, '--prefix', install_dir]
        run_command(install_cmd, cwd=build_dir_type, quiet=True)

def process_toml():
    # Load packages from TOML file
    toml_file = f'{SCRIPT_DIR}/yacpm.toml'
    if not os.path.exists(toml_file):
        print(f'Error: TOML file "{toml_file}" not found.')
        sys.exit(1)

    try:
        with open(toml_file, 'r') as f:
            config = toml.load(f)
    except Exception as e:
        print(f'Error reading TOML file: {e}')
        sys.exit(1)

    git_pkgs = config.get('git', [])
    if not git_pkgs:
        print('"[[git]]" found in the TOML file.')
        sys.exit(1)

    for pkg in git_pkgs:
        repo_url = pkg.get('repo_url')
        tag = pkg.get('tag')
        defines = pkg.get('defines', [])

        if not repo_url or not tag:
            print("Package definition must include 'repo_url' and 'tag'.")
            continue

        # Prepare defines
        cmake_defines = [f"-D{define}" for define in defines]

        # Process the package
        process_package(repo_url, tag, cmake_defines)

def gen_cmake_script():

    output_file = f"{INSTALL_DIR_PREFIX}/{PREFIX}.cmake"

    if os.path.exists(output_file) and os.path.isfile(output_file):
        os.remove(output_file)

    cmake_script = ""

    cmake_script += f"\n# Add to prefix path\n"
    for pkg_path in PACKAGES_PATHS:
        pkg_path_cmake = pkg_path.replace(SCRIPT_DIR, "${CMAKE_SOURCE_DIR}")
        cmake_script += f'set(CMAKE_PREFIX_PATH "{pkg_path_cmake}" ${{CMAKE_PREFIX_PATH}})\n'

    cmake_script += f"\n# Find packages\n"
    for pkg_name in PACKAGES_NAMES:
        # Known expceptions
        if (pkg_name == "glfw"):
            cmake_script += "find_package(glfw3 REQUIRED)\n"
        # Any other case
        else:
            cmake_script += f"find_package({pkg_name} REQUIRED)\n"

    cmake_script += f"\n# Put all the libraries on variable\n"
    to_link_libraries = set()
    for pkg_name in PACKAGES_NAMES:
        # Known expceptions
        if (pkg_name == "glfw"):
            to_link_libraries.add("glfw")
        # Any other case
        else:
            to_link_libraries.add(f"{pkg_name}::{pkg_name}")
    cmake_script += f"list(APPEND YACPM_LINK_LIBRARIES {' '.join(to_link_libraries)})\n"

    os.makedirs(f"{INSTALL_DIR_PREFIX}", exist_ok=True)
    with open(output_file, "w") as f:
        f.write(cmake_script)

def get_dependencies():
    process_toml()
    gen_cmake_script()

def do_project_build(project_build_dir, build_type):
    print('[YACPM] :: Building current project')
    run_command(['cmake', '-B', project_build_dir, f'-DCMAKE_BUILD_TYPE={build_type}'])
    run_command(['cmake', '--build', project_build_dir, '-j', '16', '--config', build_type])

if __name__ == '__main__':
    try:

        # ARGS ################################################################

        # Define arguments
        parser = argparse.ArgumentParser(description='Manage your Cmake project')
        parser.add_argument('-c', '--clear', action='store_true', default=False, help='Clear build and external dependencies')
        parser.add_argument('-i', '--install', action='store_true', default=False, help='Install dependencies (not needed if you don\'t change the TOML)')
        parser.add_argument('-b', '--build-type', type=str, default="", help='Specify build type: Debug or Release (case-insensitive)')
        # Parse arguments
        args = parser.parse_args()
        # Process 'clear'
        a_clear = args.clear
        ## Process 'install'
        a_install = args.install
        # Process 'build_type' to be case-insensitive and validate it
        a_build_type = args.build_type
        if a_build_type.lower() not in ["", "debug", "release"]:
            parser.error("Invalid build type specified. Must be 'Debug' or 'Release' (case-insensitive)")

        project_build_dir = f'{SCRIPT_DIR}/build'

        # CLEAR ALL ###########################################################

        # Deps
        if a_clear and not invalid_folder(INSTALL_DIR_PREFIX):
            shutil.rmtree(INSTALL_DIR_PREFIX)

        # Build
        if a_clear and not invalid_folder(project_build_dir):
            shutil.rmtree(project_build_dir)


        # INSTALL DEPS ########################################################

        if a_install:
            get_dependencies()
            print()

        # BUILD CURRENT PROJECT ###############################################

        if a_build_type != "":
            do_project_build(project_build_dir, a_build_type)
            print()

    except:
        exit(-1)
