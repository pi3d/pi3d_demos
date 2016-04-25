#include shaders/blend_include_fs.inc

  float tm = unif[14][2]; // countdown tm 1 to 0

  vec4 texm = vec4(texf.b, 1.0 - texb.r, max(1.0 - texf.g, texb.g), 1.0);
  gl_FragColor = mix(texf, mix(texb, texm, clamp(2.0 - tm * 2.0, 0.0, 1.0)), clamp(tm * 2.0, 0.0, 1.0));
  gl_FragColor.a *= unif[5][2];
}


