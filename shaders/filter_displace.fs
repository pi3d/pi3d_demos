/////DISPLACEMENT FILTER/////
//http://pixelshaders.com
#include std_head_fs.inc

varying vec2 uv;

float stripes(vec2 p, float steps) {
  return fract(p.x * steps);
}

void main(void) {
  float t = unif[16][0];

  vec4 color = texture2D(tex0, uv);

  float brightness = stripes(uv + vec2(color.r * 0.1 * sin(t), 0.0), 10.0);
  gl_FragColor.rgb = vec3(brightness);
  gl_FragColor.a = unif[5][2];
}
