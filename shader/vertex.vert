#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec3 normal;
layout(location = 3) in vec2 texcoord;

uniform mat4 projection;
uniform mat4 modelview;

out vec3 FragPos;
out vec3 Normal;
out vec3 Color;
out vec2 TexCoord;
out vec3 LocalPos;

void main() {
    gl_Position = projection * modelview * vec4(position, 1.0);
    FragPos = vec3(modelview * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(modelview))) * normal;
    Color = color;
    TexCoord = texcoord;
    LocalPos = position;
}