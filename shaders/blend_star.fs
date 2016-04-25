#include shaders/blend_include_fs.inc

  float tm = unif[14][2]; // 0.0 to 1.0
  vec2 mid = unif[14].xy + unif[15].xy * 0.5;

  // angle and radial distance from mid point
  float a = atan(tm * (coord.y - unif[16].y * 0.5), tm * (coord.x - unif[16].x * 0.5)) + tm;
  float r = length(coord - mid);
  float x = 0.001 * r; // these 'magic' numbers give a reasonble transition
  x *= 0.275 * (1.0 + cos(a * 40.0 + 3.0 * sin(tm + 0.05 * r)));
  
  gl_FragColor = mix(texb, texf, smoothstep(-0.45, 0.15, x - tm));
  gl_FragColor.a *= unif[5][2];
}


