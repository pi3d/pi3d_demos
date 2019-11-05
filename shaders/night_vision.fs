#version 120
//precision mediump float;

uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;
uniform vec3 unib[4];
// see docstring Buffer
uniform vec3 unif[20];
// 16,0 is time
// 16,1 is luminance threshold
// 16,2 is luminance applificaiton

varying vec2 texcoordout;
varying float dist;

//fragcolor

void main(void) {
  vec2 uv;
  uv.x = 0.4 * sin(unif[16][0] * 50.0);
  uv.y = 0.4 * cos(unif[16][0] * 50.0);
  float m = 1.0 - texture2D(tex1, texcoordout).a;
  vec3 n = texture2D(tex2, texcoordout * 3.5 + uv).rgb;
  vec3 c = texture2D(tex0, texcoordout + n.rg * 0.005).rgb;

  float lum = dot(vec3(0.30, 0.59, 0.11), c);
  if (lum < unif[16][1]) {
    c *= unif[16][2];
  }

  vec3 visionColor = vec3(0.1, 0.95, 0.2);
  gl_FragColor.rgb = (c + n * 0.2) * visionColor * m;

  gl_FragColor.a = unif[5][2];
}


