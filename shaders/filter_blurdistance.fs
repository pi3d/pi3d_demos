#include std_head_fs.inc

varying vec2 texcoordout;

//fragcolor

void main(void) {
  vec4 texc = vec4(0.0, 0.0, 0.0, 1.0); // we don't save the alpha value of the rendering so set this here to 1.0
  vec2 fcoord = vec2(0.0, 0.0);
  // because the for loops cant run over variable size we have to use a 5 x 5 grid and vary the spread that is sampled
  // obviously this will lead to grainy effects with large amounts of blur
  // unif[14][0] the focus distance
  // unif[14][1] the depth of focus (how narrow or broad a band in focus)
  // unif[14][2] the amount of blurring to apply
  // unif[16][0] distance at which objects stop being visible
  float depth = texture2D(tex1, texcoordout)[0]; //TODO correct dist formula
  float spread = clamp(unif[14][2] * abs((depth - unif[14][0]) / unif[14][1]), 0.0, unif[14][2]);
  for (float i = -2.0; i < 3.0; i += 1.0) {
    for (float j = -2.0; j < 3.0; j += 1.0) {
      fcoord = (texcoordout + vec2(i, j) * spread);
      texc += texture2D(tex0, fcoord);
    }
  }
  gl_FragColor = texc * 0.04;
  if (unif[16][0] > 0.0 && depth > unif[16][0]) gl_FragColor.a = 0.0;
  else gl_FragColor.a = 1.0;
}