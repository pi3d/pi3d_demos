precision mediump float;

uniform sampler2D tex0;
uniform sampler2D tex1;
uniform sampler2D tex2;
uniform vec3 unib[4];
// see docstring Buffer
uniform vec3 unif[20];
// see docstring Shape

varying vec2 texcoordout;
varying vec2 bumpcoordout;
varying vec3 inray;
varying vec3 normout;
varying vec3 lightVector;
varying float dist;
varying float lightFactor;

void main(void) {
// ----- boiler-plate code for fragment shaders with uv textures

// NB previous define: tex0, texcoordout, unib, unif, dist

  vec4 texc = texture2D(tex0, texcoordout); // ------ material or basic colour from texture
  if (texc.a < unib[0][2]) discard; // ------ to allow rendering behind the transparent parts of this object
  float ffact = smoothstep(unif[5][0]/3.0, unif[5][0], dist); // ------ smoothly increase fog between 1/3 and full fogdist
  vec3 bump = normalize(texture2D(tex1, bumpcoordout).rgb * 2.0 - 1.0);
// ----- boiler-plate code for fragment shader to get lighting with additional normal mapping
//       look up normal map value as a vector where each colour goes from -100% to +100% over its range so
//       0xFF7F7F is pointing right and 0X007F7F is pointing left. This vector is then rotated relative to the rotation
//       of the normal at that vertex.

// NB previous define: bump, dist, lightVector, lightFactor, texc, unif

  bump.y *= -1.0;

  float bfact = 1.0 - smoothstep(100.0, 600.0, dist); // ------ attenuate smoothly between 100 and 600 units
  float intensity = clamp(dot(lightVector, normalize(vec3(0.0, 0.0, 1.0) + bump * bfact)) * lightFactor, 0.0, 1.0); // ------ adjustment of colour according to combined normal
  texc.rgb = (texc.rgb * unif[9]) * intensity + (texc.rgb * unif[10]); // ------ directional lightcol * intensity + ambient lightcol
// ----- boiler-plate code for fragment shader to get mapping for use
//       with reflected image

// NB previous define: inray, normout, bfact, bump

  vec3 refl = normalize(reflect(inray, normout + 0.2 * bfact * bump)); // ----- reflection direction from this vertex
  vec2 shinecoord = vec2(atan(refl.x, -refl.z)/ 6.2831854 - 0.5,
                          acos(refl.y) / 3.1415927); // ------ potentially need to clamp with bump included in normal
  vec4 shinec = vec4(0.0, 0.0, 0.0, 0.0);
  //shinec = texture2D(tex2, shinecoord); // ------ get the reflection for this pixel
  //float shinefact = clamp(unib[0][1]*length(shinec)/length(texc), 0.0, unib[0][1]);// ------ reduce the reflection where the ground texture is lighter than it

  //gl_FragColor = (1.0 - ffact) * ((1.0 - shinefact) * texc + shinefact * shinec) + ffact * vec4(unif[4], unif[5][1]); // ------ combine using factors
  gl_FragColor =  (1.0 - ffact) * texc + ffact * vec4(unif[4], unif[5][1]); // ------ combine using factors
  gl_FragColor.a *= unif[5][2];
}
