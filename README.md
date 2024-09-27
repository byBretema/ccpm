# 📦 YACPM - Yet Another Cmake Package Manager

![YACPM Logo](https://i.imgur.com/A2KPcdK.jpeg)

Are you tired of watching time fade away as CMake recompiles Assimp for the sixth time today just because you had to do a rebuild of your own code?

Have you find yourself writing below code manually?
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

Create a simple `yacpm.toml` similar to this one
```toml
[[git]]
repo_url = "https://github.com/fmtlib/fmt"
tag = "11.0.2"
defines = ["FMT_TEST=OFF", "FMT_DOC=OFF"]

[[git]]
repo_url = "https://github.com/glfw/glfw"
tag = "3.4"
defines = [
    "GLFW_BUILD_DOCS=OFF",
    "GLFW_BUILD_TESTS=OFF",
    "GLFW_BUILD_EXAMPLES=OFF",
]

[[git]]
repo_url = "https://github.com/g-truc/glm"
tag = "1.0.1"
defines = ["GLM_BUILD_TESTS=OFF", "GLM_ENABLE_CXX_20=ON"]

```

### Donwload, Build and Install packages
```bash
# Requires the toml package : pip install toml
# Launch each time you modify the 'yacpm.toml'
python ./yacpm.py -i
```

### On your CMake
```cmake
add_executable(${PROJECT_NAME} main.cpp)
include(${CMAKE_SOURCE_DIR}/.yacpm/yacpm.cmake)
target_link_libraries(${YOUR_AWESOME_TARGET} PRIVATE ${YACPM_LINK_LIBRARIES})
```

### Just compile :)
```bash
# Just run the script with '-b <build_type>'
python ./yacpm.py -b 'Release'
# Or manually if the process is complex than this
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . -j 16 --config Release
```

## Notes

This script assumes that you have the following commands installed:
- cmake
- git

In the roadmap:
- [x] Other *git* providers [^1]
- [ ] Others VCS like *SVN* or *Hg*
- [ ] Zip files
- [ ] Automatic lib name and target gathering [^2]

[^1]: The first iteration was github only.
[^2]: For cases like glfw where its **find_package** is `glfw3` and its **link_library** is just `glfw` instead of `glfw::glfw` like the vast majority of the packages.
