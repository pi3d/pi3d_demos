precision mediump float;

attribute vec3 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

uniform mat4 modelviewmatrix[2]; // [0] model movement in real coords, [1] in camera coords
uniform vec3 unib[4];
//uniform float ntiles => unib[0][0]
//uniform vec2 umult, vmult => unib[2]
//uniform vec2 u_off, v_off => unib[3]
uniform vec3 unif[20];
//uniform vec3 eye > unif[6]

varying float dist;
varying vec3 colour;
varying float lum;

void main(void) {
  vec4 relPosn = modelviewmatrix[0] * vec4(vertex,1.0);
  vec3 inray = vec3(relPosn - vec4(unif[6], 0.0)); // ----- vector from the camera to this vertex
  dist = length(inray);
  gl_Position = modelviewmatrix[1] * vec4(vertex, 1.0);
  float inv_dist = 1.0 / dist;
  gl_PointSize = unib[2][2] * inv_dist;
  if (gl_PointSize < 3.0) {
    lum = texcoord[0] * inv_dist * inv_dist * 8.0;
  } else {
    lum = texcoord[0] * 10.0;
  }
  lum = clamp(lum, 0.1, 1.0);
  gl_PointSize = clamp(gl_PointSize, 3.0, unib[2][2]);
  colour = normal;
}
