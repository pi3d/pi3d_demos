/////SPATIAL DISTORTION FILTER/////
//http://pixelshaders.com
#include std_head_fs.inc

varying vec2 uv;

void main(void) {
  float t = unif[16][0];
  vec2 newuv = uv + vec2(sin(uv.y * 80.0 + t * 6.0) * 0.03, 0.0);
  gl_FragColor = texture2D(tex0, newuv);
  gl_FragColor.a = 1.0;
  //gl_FragColor = vec4(1.0,1.0,0.0,1.0);
}
