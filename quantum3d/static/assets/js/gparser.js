
// Base semi-classes
function GCodeModel() {
  this.codes = [];
};

function GCode() {
  this.words = [];
  this.comments = [];
  this.index = 0;
};

function GWord(letter, value, raw) {
  this.letter = letter;
  this.value = value;
  this.raw = raw;
};

// main parser
function GCodeParser() {
  this.model = new GCodeModel();
}

GCodeParser.prototype.parseComments = function (line) {
  var self = this;
  let comments = [];

  // comments: full-line/in-line parenthesis or semicolon
  addComments(line.match(/\((.*)\)$/g, ''));
  addComments(line.match(/\((.*?)\)/g, ''));
  addComments(line.match(/;(.*$)/g, ''));

  function addComments(matches) {
    if (matches) matches.forEach(comment => comments.push(comment));
  }
  return comments;
}

GCodeParser.prototype.parseWord = function (word) {
  if (!word.length) return;

  let letter = word[0].toUpperCase();
  let value = word.slice(1);

  if (letter < 'A' || letter > 'Z') return;
  return new GWord(letter, value);
};

GCodeParser.prototype.parseLine = function (line) {
  let self = this;
  let pLine = new GCode();
  pLine.comments = self.parseComments(line);
  pLine.comments.forEach(comment => line = line.replace(comment, ''));

  let words = line.trim().split(' ');
  for (let i = 0; i < words.length; i++) {
    if (!words[i] || words[i].length <= 0) continue;

    let pWord = this.parseWord(words[i]);
    if (!pWord) continue;

    pLine.words.push(pWord);
  }
  return pLine;
};

GCodeParser.prototype.parse = function (gcode) {
  let self = this;
  let current = new GCode();
  let currentIndex = 0;

  let lines = gcode.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim().startsWith(';')) continue;

    let lineCode = self.parseLine(lines[i]);
    // Trying to auto-group words across multiple lines and split single lines
    // Detect new code group, add current group to model & start a new group
    lineCode.words.forEach(word => {
      if (['G', 'M'].some(l => word.letter === l)) {
        if (current.words.length) {
          self.model.codes.push(current);
          current = new GCode();
          current.index = ++currentIndex;
        }
      }
      current.words.push(word);
    });
  }
  self.model.codes.push(current);
  return self.model;
};

GCodeParser.prototype.centerizeGCodes = function (gcode) {
  let newg = [];
  let sum = [0, 0, 0],
    num = [0, 0, 0],
    mean = [0, 0, 0];

  // remove useless data
  gcode.codes.forEach(g => {
    // it is G and has some X and Y values
    // and X and Y values are not both 0
    let cond1 = ['G', 'X', 'Y'].every(l => g.words.map(el => el.letter).includes(l))
      && !['X', 'Y'].every(l => g.words.find(el => el.letter === l).value == 0)
    // also accept if only includes Z
    let cond2 = ['G', 'Z'].every(l => g.words.map(el => el.letter).includes(l));
    if (cond1 || cond2)
      newg.push(g);
  });

  gcode.codes = newg;
  newg = [];

  // center around (0, 0, 0)
  gcode.codes.forEach(g => {
    ['X', 'Y', 'Z'].forEach((letter, index) => {
      if (g.words.map(el => el.letter).includes(letter)) {
        sum[index] += parseFloat(g.words.find(el => el.letter === letter).value);
        num[index]++;
      }
    });
  });

  mean = [
    sum[0] / num[0],
    sum[1] / num[1],
    sum[2] / num[2]
  ];

  gcode.codes.forEach(g => {
    // ['X', 'Y', 'Z'] // -> no need to center around Z, I suppose :-?
    // TODO2: think about Z to see whether it's good to centerize that too
    ['X', 'Y']
      .forEach((letter, index) => {
        if (g.words.map(el => el.letter).includes(letter)) {
          let obj = g.words.find(el => el.letter === letter);
          obj.value = '' + (parseFloat(obj.value) - mean[index]);
        }
      });
  });

  return gcode;
}


module.exports = {
  GCodeModel,
  GCode,
  GWord,
  GCodeParser,
};
