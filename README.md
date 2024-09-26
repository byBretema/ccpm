# YACPM - Yet Another Cmake Package Manager

Are you tired of watching time fade away as CMake recompiles Assimp for the sixth time today just because you had to do a rebuild of your own code?

Have you find yourself writing below code manully?
```cmake
add_subdirectory(third_party/fmt)
find_package(fmt REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
```

No worries, we’ve got the solution right here!

> Feel free to use this repository as template to init your awesome new project 😎

## Flow

### Define your dependencies

> The below example will install fmt, glfw and glm with your custom defines.
> Right now it requires a tag in order to not fall in the trap of use a development version of a lib.
> I'm open to reconsider that "desing decission" if someone expose me good reasons for it 😅.

```toml
[[git]]
repo_name = "fmtlib/fmt"
tag = "11.0.2"
defines = ["FMT_TEST=OFF", "FMT_DOC=OFF"]

[[git]]
repo_name = "glfw/glfw"
tag = "3.4"
defines = [
    "GLFW_BUILD_DOCS=OFF",
    "GLFW_BUILD_TESTS=OFF",
    "GLFW_BUILD_EXAMPLES=OFF",
]

[[git]]
repo_name = "g-truc/glm"
tag = "1.0.1"
defines = ["GLM_BUILD_TESTS=OFF", "GLM_ENABLE_CXX_20=ON"]
```

### Donwload, Build and Install packages
```bash
# Requires the toml package : pip install toml
# Launch each time you modify the 'yacpm_packages.toml'
python ./yacpm_cmake.py
```

### On your CMake
```cmake
# Dependencies
include(_yacpm/yacpm.cmake)
# ...
target_link_libraries(${YOUR_AWESOME_TARGET} PRIVATE ${YACPM_LINK_LIBRARIES})
```

### Just compile :)
```bash
# Do each time you change your source :)
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build . -j 16 --config Debug
```

## Notes

This script assumes that you have the following commands installed:
- cmake
- git

In the roadmap:
- [ ] Other *git* providers (**it's github only right now, just for tool validation**)
- [ ] Others VCS like *SVN* or *Hg*
- [ ] Zip files
