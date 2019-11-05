#version 120
//precision mediump float;

uniform sampler2D tex0;
uniform vec3 unib[4];

varying float dist;
varying mat2 rotn;

void main(void) {
  vec2 centre = vec2(0.5, 0.5);
  vec2 rot_coord = rotn * (gl_PointCoord - centre) + centre;
  vec4 texc = texture2D(tex0, rot_coord); // ------ material or basic colour from texture
  if (dist < 1.0 || texc.a < unib[0][2]) discard; // ------ to allow rendering behind the transparent parts of this object
  gl_FragColor = texc;
}


