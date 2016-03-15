#include shaders/blend_include_fs.inc

  float tm = unif[14][2];
  vec4 light = vec4(0.577, 0.577, 0.577, 1.0);

  float bfact = dot(light, texb);
  gl_FragColor = mix(texf * (1.0 + tm * (bfact - 1.0)), texb, clamp(2.0 * tm - 1.0, 0.0, 1.0));
  gl_FragColor.a *= unif[5][2];
}


