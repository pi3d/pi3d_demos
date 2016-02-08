precision mediump float;

uniform vec3 unib[4];
// see docstring Buffer
uniform vec3 unif[20];

varying float dist;
varying vec3 colour;
varying float lum;

void main(void) {
  vec4 texc = vec4(unib[1], 1.0); // ------ basic colour from material vector
  //if (texc.a < unib[0][2]) discard; // ------ to allow rendering behind the transparent parts of this object
  //float ffact = smoothstep(unif[5][0]/3.0, unif[5][0], dist); // ------ smoothly increase fog between 1/3 and full fogdist

  if (distance(gl_PointCoord, vec2(0.5)) > 0.5) discard; //circular points
  //gl_FragColor = (1.0 - ffact) * texc + ffact * vec4(unif[4], unif[5][1]); // ------ combine using factors
  gl_FragColor.rgb = colour * lum;
  gl_FragColor.a = 1.0;
}

