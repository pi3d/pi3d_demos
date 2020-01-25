/////HATCH FILTER/////
//www.cloneproduction.net
#include std_head_fs.inc

varying vec2 uv;
varying vec2 del;

void main(void){
  vec4 c1 = texture2D(tex0, uv);
  vec4 c2 = texture2D(tex0, uv + vec2(del.x, 0));
  vec4 c3 = texture2D(tex0, uv + vec2(0, del.y));
  float f = distance(c1.rgb, c2.rgb) + distance(c1.rgb, c3.rgb) - 0.2;
  float d = 0.2;
  float r = length(c1.rgb) * 0.4;
  float h = step(r, fract((gl_FragCoord.y - gl_FragCoord.x) * d));
  f = clamp(f + 1.0 - h, 0.0, 1.0);
  gl_FragColor = mix(vec4(1.0, 1.0, 1.0, 1.0), vec4(unif[16], 1.0), f);
  gl_FragColor.a = unif[5][2];
}