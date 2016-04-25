#include shaders/blend_include_fs.inc

  float tm = unif[14][2]; // countdown tm 1 to 0
  float n = 40.0; ///// NB if you increase this to make bigger holes you need to reduce * 0.02 in line 41 proportionately

  float x = length(coord - floor(coord / n + 0.5) * n) * 0.02;
  gl_FragColor = mix(texf, texb, smoothstep(-0.2, 0.2, tm - x));
  gl_FragColor.a *= unif[5][2];
}


