#include <metal_stdlib>
using namespace metal;

struct VertexIn {
    float3 position [[attribute(0)]];
    float4 color [[attribute(1)]];
};

struct VertexOut {
    float4 position [[position]];
    float4 color;
};

vertex VertexOut vertex_shader(const VertexIn vertex_in [[stage_in]]) {
    VertexOut vertex_out;
    vertex_out.position = float4(vertex_in.position, 1.0);
    vertex_out.color = vertex_in.color;
    return vertex_out;
}

fragment float4 fragment_shader(VertexOut interpolated [[stage_in]]) {
    return interpolated.color;
}