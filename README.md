# yacpm
Yet Another Cmake Package Manager

> This script assumes that you have the following commands installed:
> - cmake
> - git

> Right now this the script works in a solid way with github repositiories,
> I plan to continue working on the script to add GitLab, Bitbucket, and any other platforms in the most convenient way possible.
> Additionally, support for Files, SVN, and HG will be added in the future.

### Python dependencies
```bash
# Do once (if you don't have this package already)
pip install toml
```

### Donwload, Build and Install packages
```bash
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
cmake .. -DCMAKE_BUILD_TYPE=Debug;
cmake --build . -j 16 --config Debug;
```
