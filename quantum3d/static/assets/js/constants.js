function Constants() {
}

// the dimension and coefficient of render area
Constants.width = 360;
Constants.height = 360;
Constants.dimensionCoef = 1.5;

// the color(s) of hollowed
Constants.motionColors = [
  new THREE.Color(0xdddddd)
];

// the color(s) of the lines themselves
Constants.feedColors = [
  // new THREE.Color(0xffcc66), // canteloupe // yellow
  new THREE.Color(0x66ccff), // sky        // blue
  // new THREE.Color(0x22bb22), // honeydew   // green
  // new THREE.Color(0x00ff00),
  // new THREE.Color(0xff70cf), // carnation  // pink
  // new THREE.Color(0xcc66ff), // lavender   // purple
  // new THREE.Color(0xfffe66), // banana     // yellow - light
  // new THREE.Color(0xff6666), // salmon      // red
  // new THREE.Color(0x66ffcc), // spindrift  // blue - light
  // new THREE.Color(0x66ff66), // flora      // green - light
  // new THREE.Color(0x000000),
  // new THREE.Color(0x0000FF),
  new THREE.Color(0xFFFFFF),
];


module.exports = Constants;
