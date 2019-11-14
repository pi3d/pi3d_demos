#version 120
//precision mediump float;

attribute vec3 vertex;
attribute vec3 normal; // x component used to hold texture number

uniform mat4 modelviewmatrix[2]; // [0] model movement in real coords, [1] in camera coords
uniform vec3 unib[5];
//uniform float ntiles => unib[0][0]
//uniform vec2 umult, vmult => unib[2]
//uniform vec2 u_off, v_off => unib[3]

varying float texnum;

void main(void) {
  texnum = normal[0];
  gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
  gl_PointSize = unib[2][2] / vertex[2];
}
