# 📦 CCPM - Custom Cmake Package Manager

![CCPM Logo](https://i.imgur.com/A2KPcdK.jpeg)

🧑‍💻 Are you tired of watching time fade away as CMake recompiles Assimp for the sixth time today just because you had to do a rebuild of your own code?

🖖 Do you have your CMakeLists.txt full of `add_subdirectory` for code that is not yours?

```cmake
add_subdirectory(third_party/fmt)
find_package(fmt REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
```

⚡ **No worries, we’ve got the solution right here!**


## 🌊 Flow

### 🚀 Install the tool

```bash
pip install ccpm
```

### 📃 Define your dependencies

> The below example will install fmt, glfw and glm with custom defines.

Create a simple `ccpm.toml` ***in the same folder*** of main 'CMakeLists.txt' similar to this one:

```toml
[[git]]
repo_url = "https://github.com/fmtlib/fmt"
tag = "11.0.2"
defines = ["FMT_TEST=OFF", "FMT_DOC=OFF"]

[[git]]
repo_url = "https://github.com/glfw/glfw"
tag = "3.4"
defines = ["GLFW_BUILD_DOCS=OFF", "GLFW_BUILD_TESTS=OFF", "GLFW_BUILD_EXAMPLES=OFF"]

[[git]]
repo_url = "https://github.com/g-truc/glm"
tag = "1.0.1"
defines = ["GLM_BUILD_TESTS=OFF", "GLM_ENABLE_CXX_20=ON"]
```

### ✍️ On your CMake

```cmake
include(${CMAKE_SOURCE_DIR}/.ccpm/ccpm.cmake)  # This resolves modulepaths
add_executable(${AWESOME_TARGET} main.cpp)

# I'm working on simplify this stage but there is many differences between some packages
find_packge(fmt REQUIRED)
target_link_libraries(${AWESOME_TARGET} PRIVATE fmt::fmt)

# Goal syntax
include(${CMAKE_SOURCE_DIR}/.ccpm/ccpm.cmake)  # This will include the 'find_packge(fmt REQUIRED)'
target_link_libraries(${AWESOME_TARGET} PRIVATE ${CCPM_LINK_LIBRARIES})  # To include all of them
target_link_libraries(${AWESOME_TARGET} PRIVATE ${CCPM_LIB_fmt})         # For more granularity
```

### 🛠️ Donwload, Build and Install packages

```bash
ccpm -i   # To run download+build+installa process (only needed if you change the .toml file)
ccpm -b   # Builds the main 'CMakeLists.txt' (by default in debug, add -r for release)
```


## 📝 Notes

#### This script assumes that you have the following commands installed:

- cmake
- git

#### In the roadmap:

- [x] Other *git* providers [^1]
- [ ] Add option to choose CMake Generator
- [ ] Automatic lib name and target gathering [^2]
- [ ] Zip files
- [ ] Others VCS like *SVN* or *Hg*

#### Lectures / Inspiration:

- [It's Time To Do CMake Right](https://pabloariasal.github.io/2018/02/19/its-time-to-do-cmake-right/)

- [CPM.cmake](https://github.com/cpm-cmake/CPM.cmake)

- [Bootstrap](https://github.com/corporateshark/bootstrapping)


[^1]: The first iteration was github only.
[^2]: For cases like glfw where its **find_package** is `glfw3` and its **link_library** is just `glfw` instead of `glfw::glfw` like the vast majority of the packages.

