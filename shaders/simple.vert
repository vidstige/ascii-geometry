#version 330
uniform mat4 u_projection;
uniform mat4 u_modelView;
uniform vec3 u_light1;
uniform float u_ambient;

in vec3 in_vert;
in vec3 in_normal;

out vec4 color;

void main() {
  gl_Position = u_projection * u_modelView * vec4(in_vert, 1.0);
  vec4 normal = transpose(inverse(u_modelView)) * vec4(in_normal, 0.0);
  float gray = clamp(dot(normalize(u_light1), normalize(vec3(normal))), 0, 1) + u_ambient;
  color = vec4(gray, gray, gray, 1.0);
  //normal = vec4(in_normal, 0.0);
}
