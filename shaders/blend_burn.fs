#include shaders/blend_include_fs.inc

  float mt = 1.0 - unif[14][2]; // countdown tm 1 to 0

  float y = 1.0 - smoothstep(mt, mt * 1.2, length(texb.rgb) * 0.577 + 0.01);
  gl_FragColor = mix(texb, texf * y, step(1.0, y));
  gl_FragColor.a *= unif[5][2];
}


