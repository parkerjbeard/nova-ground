#version 330

out vec4 fragColor;

uniform vec4 grid_color;

void main() {
    fragColor = grid_color;
}