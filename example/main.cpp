
#include <fmt/format.h>

#define GLM_FORCE_INLINE
#define GLM_ENABLE_EXPERIMENTAL
#define GLM_FORCE_SWIZZLE
#define GLM_FORCE_SILENT_WARNINGS
#define GLM_FORCE_RADIANS
#define GLM_FORCE_LEFT_HANDED
#define GLM_FORCE_DEPTH_ZERO_TO_ONE
#include <glm/glm.hpp>
#include <glm/gtx/string_cast.hpp>

int main()
{
    fmt::println("Vec2.x | {}", glm::vec2(2, 3).x);
    fmt::println("Vec3.y | {}", glm::vec3(1, 3.2345f, 4).y);
    fmt::println("Vec4   | {}", glm::to_string(glm::vec4(1, 3.2345f, 4, .25f)));
}
