#include std_head_vs.inc

varying vec2 uv;

void main(void) {
  uv = texcoord * unib[2].xy + unib[3].xy;
  uv.y = 1.0 - uv.y;
  gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
}