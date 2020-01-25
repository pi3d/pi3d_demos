#include std_head_vs.inc

float width = 4.0; //charcoal line width

varying vec2 uv;
varying vec2 del;

void main(void) {
  uv = texcoord * unib[2].xy + unib[3].xy;
  uv.y = 1.0 - uv.y; // flip vertically
  del = vec2(width / unif[15][0], width / unif[15][1]);
  gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
}