precision mediump float;

uniform sampler2D tex0;
uniform vec3 unib[4];

varying float dist;

void main(void) {
  vec4 texc = texture2D(tex0, gl_PointCoord); // ------ material or basic colour from texture
  if (dist < 1.0 || texc.a < unib[0][2]) discard; // ------ to allow rendering behind the transparent parts of this object
  gl_FragColor = texc;
}


