/////COLOR DISTORTION FILTER/////
//http://pixelshaders.com
#include std_head_fs.inc

varying vec2 texcoordout;

float wave(float x, float amount) {
  return (sin(x * amount) + 1.0) * 0.5;
}

void main(void) {
  vec4 color = texture2D(tex0, texcoordout);
  gl_FragColor.r = wave(color.r, unif[16][0]);
  gl_FragColor.g = wave(color.g, unif[16][1]);
  gl_FragColor.b = wave(color.b, unif[16][2]);
  gl_FragColor.a = 1.0;
}
