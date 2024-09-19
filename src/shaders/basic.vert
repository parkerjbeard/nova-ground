#version 130

in vec4 vertex_position;
in vec4 vertex_color;

out vec4 color;

uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * vertex_position;
    color = vertex_color;
}