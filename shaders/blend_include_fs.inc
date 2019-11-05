#version 120
//precision mediump float;

uniform sampler2D tex0;
uniform sampler2D tex1;
uniform vec3 unib[4];
//uniform float blend ====> unib[0][2]
uniform vec3 unif[19];
//uniform vec2 (x, y) =========> unif[14] f ground 
//uniform vec2 (w, h, full_h) => unif[15] f ground 
//uniform vec2 (x, y) =========> unif[16] b ground 
//uniform vec2 (w, h, full_h) => unif[17] b ground 

varying vec2 pix_invf;
varying vec2 pix_invb;

//fragcolor

void main(void) {
  float edge_alpha = 0.2; // change how much the 'infill' shows <<<<<<<<<<<<<<<<<<<<<<<

  vec2 coord;
  vec2 coordsc;
  vec4 texf;
  vec4 texb;
  coord = vec2(gl_FragCoord);
  coord.y = unif[15][2] - coord.y; // top left convension though means flipping image!
  coordsc = coord - unif[14].xy; // offset
  coordsc *=  pix_invf; // really dividing to scale 0-1 i.e. (x/w, y/h)
  texf = texture2D(tex0, coordsc);
  if (coord.x <= unif[14][0] || coord.x > unif[14][0]+unif[15][0] ||
      coord.y <= unif[14][1] || coord.y > unif[14][1]+unif[15][1]) texf.a *= edge_alpha;
  coordsc = coord - unif[16].xy; // offset
  coordsc *=  pix_invb; // really dividing to scale 0-1 i.e. (x/w, y/h)
  texb = texture2D(tex1, coordsc);
  if (coord.x <= unif[16][0] || coord.x > unif[16][0]+unif[17][0] ||
      coord.y <= unif[16][1] || coord.y > unif[16][1]+unif[17][1]) texb.a *= edge_alpha;
