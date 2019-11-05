#version 120
//precision mediump float;

varying vec3 colour;
varying float lum;

//fragcolor

void main(void) {
  if (distance(gl_PointCoord, vec2(0.5)) > 0.5) discard; //circular points
  gl_FragColor.rgb = colour * lum;
  gl_FragColor.a = 1.0;
}

