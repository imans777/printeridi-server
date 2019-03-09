
function GCodeViewModel(code) {
  this.code = code;
  this.vertexIndex = 0;
  this.vertexLength = 0;
}

function GCodeRenderer() {
  let self = this;

  this.viewModels = [];
  this.index = 0;
  this.baseObject = new THREE.Object3D();

  this.motionGeo = new THREE.Geometry();
  this.motionMat = new THREE.LineBasicMaterial({
    opacity: 0.2,
    transparent: true,
    linewidth: 1,
    vertexColors: THREE.VertexColors
  });

  this.motionIncGeo = new THREE.Geometry();
  this.motionIncMat = new THREE.LineBasicMaterial({
    opacity: 0.2,
    transparent: true,
    linewidth: 1,
    vertexColors: THREE.VertexColors
  });

  this.feedAllGeo = new THREE.Geometry();

  this.feedGeo = new THREE.Geometry();
  this.feedMat = new THREE.LineBasicMaterial({
    opacity: 0.8,
    transparent: true,
    linewidth: 2,
    vertexColors: THREE.VertexColors
  });

  this.feedIncGeo = new THREE.Geometry();
  this.feedIncMat = new THREE.LineBasicMaterial({
    opacity: 0.2,
    transparent: true,
    linewidth: 2,
    vertexColors: THREE.VertexColors
  });

  this.lastLine = {x: 0, y: 0, z: 0, e: 0, f: 0};
  this.relative = false;
  this.bounds = {
    min: {x: 100000, y: 100000, z: 100000},
    max: {x: -100000, y: -100000, z: -100000}
  };

  this.geometryHandlers = {
    G0: function (viewModel) {
      let newLine = {};
      viewModel.code.words.forEach(function (word) {
        switch (word.letter) {
          case 'X': case 'Y': case 'Z': case 'E': case 'F':
            let p = word.letter.toLowerCase();
            newLine[p] = self.absolute(self.lastLine[p], parseFloat(word.value));
            break;
        }
      });
      ['x', 'y', 'z', 'e', 'f'].forEach(function (prop) {
        if (newLine[prop] === undefined) {
          newLine[prop] = self.lastLine[prop];
        }
      });

      viewModel.vertexIndex = self.motionGeo.vertices.length;

      let color = GCodeRenderer.motionColors[viewModel.code.index % GCodeRenderer.motionColors.length];
      self.motionGeo.vertices.push(new THREE.Vector3(self.lastLine.x, self.lastLine.y, self.lastLine.z));
      self.motionGeo.vertices.push(new THREE.Vector3(newLine.x, newLine.y, newLine.z));

      self.motionGeo.colors.push(color);
      self.motionGeo.colors.push(color);

      viewModel.vertexLength = self.motionGeo.vertices.length - viewModel.vertexIndex;
      self.lastLine = newLine;
      return self.motionGeo;
    },
    G1: function (viewModel) {
      let newLine = {};
      viewModel.code.words.forEach(function (word) {
        switch (word.letter) {
          case 'X': case 'Y': case 'Z': case 'E': case 'F':
            let p = word.letter.toLowerCase();
            newLine[p] = self.absolute(self.lastLine[p], parseFloat(word.value));
            break;
        }
      });
      ['x', 'y', 'z', 'e', 'f'].forEach(function (prop) {
        if (newLine[prop] === undefined) {
          newLine[prop] = self.lastLine[prop];
        }
      });

      let color = GCodeRenderer.feedColors[viewModel.code.index % GCodeRenderer.feedColors.length];
      let p1 = new THREE.Vector3(self.lastLine.x, self.lastLine.y, self.lastLine.z);
      let p2 = new THREE.Vector3(newLine.x, newLine.y, newLine.z);
      viewModel.vertexIndex = self.feedAllGeo.vertices.length;

      if (viewModel.code.index <= self.index) {
        self.feedGeo.vertices.push(p1);
        self.feedGeo.vertices.push(p2);
        self.feedGeo.colors.push(color);
        self.feedGeo.colors.push(color);
      } else {
        self.feedIncGeo.vertices.push(p1);
        self.feedIncGeo.vertices.push(p2);
        self.feedIncGeo.colors.push(color);
        self.feedIncGeo.colors.push(color);
      }
      self.feedAllGeo.vertices.push(p1);
      self.feedAllGeo.vertices.push(p2);
      self.feedAllGeo.colors.push(color);
      self.feedAllGeo.colors.push(color);

      viewModel.vertexLength = self.feedAllGeo.vertices.length - viewModel.vertexIndex;
      self.lastLine = newLine;
      return self.feedGeo;
    },
    G2: function (viewModel) {
    }
  };

  this.materialHandlers = {
    G0: function (viewModel) {
      return this.motionMat;
    },
    G1: function (viewModel) {
      return this.feedMat;
    },
    G2: function (viewModel) {
      return this.feedMat;
    }
  };
};

GCodeRenderer.motionColors = Constants.motionColors;
GCodeRenderer.feedColors = Constants.feedColors;

GCodeRenderer.prototype.absolute = function (v1, v2) {
  return this.relative ? v1 + v2 : v2;
}

GCodeRenderer.prototype.render = function (model) {
  this.model = model;

  // 'this.model.codes' are the parsed-gcodes!
  this.model.codes.forEach(code => this.renderGCode(code));
  this.updateLines();

  // Center
  this.feedAllGeo.computeBoundingBox();
  this.bounds = this.feedAllGeo.boundingBox;

  // the center of the object model itself
  this.center = new THREE.Vector3(
    ((this.bounds.max.x + this.bounds.min.x) / 2),
    ((this.bounds.max.y + this.bounds.min.y) / 2),
    ((this.bounds.max.z + this.bounds.min.z) / 2)
  );

  let width = Constants.width, height = Constants.height;
  let zScale = height / (this.bounds.max.z - this.bounds.min.z),
    yScale = width / (this.bounds.max.y - this.bounds.min.y),
    xScale = width / (this.bounds.max.x - this.bounds.min.x);
  let scale = Math.min(zScale, Math.min(xScale, yScale));
  this.baseObject.position = this.center.multiplyScalar(-scale);
  this.baseObject.scale.multiplyScalar(scale * Constants.dimensionCoef);

  return this.baseObject;
};

GCodeRenderer.prototype.updateLines = function (renderHover = true) {
  while (this.baseObject.children.length)
    this.baseObject.remove(this.baseObject.children[0]);

  if (renderHover)
    this.baseObject.add(new THREE.Line(this.motionGeo, this.motionMat, THREE.LinePieces)); // hover around
  this.baseObject.add(new THREE.Line(this.feedGeo, this.feedMat, THREE.LinePieces)); // the shape itself (the colored lines, etc.)
  this.baseObject.add(new THREE.Line(this.feedIncGeo, this.feedIncMat, THREE.LinePieces)); // the hollowed-hover around :-?
};

GCodeRenderer.prototype.renderGCode = function (code) {
  let cmd = code.words[0].letter + code.words[0].value;
  let viewModel = new GCodeViewModel(code);

  try {
    this.geometryHandlers[cmd](viewModel);
    this.materialHandlers[cmd](viewModel);
  }
  catch (err) {
    console.info("not G command: ", cmd, err);
  }

  if (viewModel.vertexLength)
    this.viewModels.push(viewModel);
};

// this decides till which index should we render the model
GCodeRenderer.prototype.setIndex = function (index, renderHover = true) {
  index = Math.floor(index);
  if (this.index == index) return;
  if (index < 0 || index >= this.viewModels.length) return;

  let vm = this.viewModels[index];
  this.feedGeo = new THREE.Geometry();

  let vertices = this.feedAllGeo.vertices.slice(0, vm.vertexIndex + vm.vertexLength);

  // THIS CAUSED STACK OVERFLOW!
  // Array.prototype.push.apply(this.feedGeo.vertices, vertices);
  console.log("vertices to add: ", vertices.length);
  for (item in vertices)
    this.feedGeo.vertices.push(vertices[item]);

  let colors = this.feedAllGeo.colors.slice(0, vm.vertexIndex + vm.vertexLength);
  // Array.prototype.push.apply(this.feedGeo.colors, colors);
  for (item in colors)
    this.feedGeo.colors.push(colors[item]);

  this.updateLines(renderHover);
  this.index = index;
};


module.exports = {
  GCodeViewModel,
  GCodeRenderer,
};
