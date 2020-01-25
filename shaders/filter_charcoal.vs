#include std_head_vs.inc
///// charcoal line width
#define WIDTH 4.0

varying vec2 uv;
varying vec2 d;

void main(void) {
  uv = texcoord * unib[2].xy + unib[3].xy;
  uv.y = 1.0 - uv.y; // flip vertically
  d = vec2(WIDTH / unif[15][0], WIDTH / unif[15][1]);
  gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
}
