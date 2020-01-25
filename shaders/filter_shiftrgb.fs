/////SHIFT RGB FILTER/////
//www.cloneproduction.net
#include std_head_fs.inc

varying vec2 uv;

vec3 HUEtoRGB(float H){
  H = fract(H);
  float R = abs(H * 6.0 - 3.0) - 1.0;
  float G = 2.0 - abs(H * 6.0 - 2.0);
  float B = 2.0 - abs(H * 6.0 - 4.0);
  return clamp(vec3(R, G, B), 0.0, 1.0);
}

vec3 HSVtoRGB(vec3 hsv){
  vec3 RGB = HUEtoRGB(hsv.x);
  return ((RGB-1.0) * hsv.y + 1.0) * hsv.z;
}

vec3 RGBtoHSV(vec3 RGB){
  vec3 hsv = vec3(0.0, 0.0, 0.0);
  hsv.z = max(RGB.r, max(RGB.g, RGB.b));
  float M = min(RGB.r, min(RGB.g, RGB.b));
  float C = hsv.z - M + 0.000000001; //min never > max so C always > 0
  vec3 Delta = (hsv.z - RGB) / C;
  Delta -= Delta.brg;
  Delta += vec3 (2.0, 4.0, 6.0);
  Delta.brg *= step(hsv.z, RGB);
  hsv.x = max(Delta.r, max(Delta.g, Delta.b));
  hsv.x = fract(hsv.x / 6.0);
  hsv.y = C / hsv.z;
  return hsv;
}

vec4 ts (sampler2D s, float distance){
  float direction = unif[16][0];
  float hue = unif[16][2];
  vec2 newuv = uv + vec2(cos(direction), sin(direction)) * distance;
  return vec4(HSVtoRGB(vec3(hue, 0.0, 0.0) + RGBtoHSV(texture2D(s, newuv).rgb)), 1.0);
}

void main(void){
  float hue = unif[16][2];
  float shift = unif[16][1];
  vec4 c = texture2D(tex0, uv);
  float pa = c.a;
  float sh = shift * texture2D(tex1, uv).x;
  c.r = ts(tex0, sh * 0.1).r;
  c.g = ts(tex0, 0.0).g;
  c.b = ts(tex0, sh * -0.1).b;
  gl_FragColor.rgb = HSVtoRGB(-vec3(hue, 0, 0) + RGBtoHSV(c.rgb));
  gl_FragColor.a = 1.0;//unif[5][2];
}