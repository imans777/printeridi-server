function FileIO() {}

// NOTE: read form a link (or AJAX call :-?), e.g. 'https://....gcode'
FileIO.loadPath = function (path, callback) {
  let self = this;
  $.get(path, null, callback, 'text');
}

// NOTE: read from file, e.g. by drag and drop
FileIO.load = function (files, callback) {
  if (files.length) {
    for (i = 0; i < files.length; i++)
      FileIO.load(files[i], callback);
  }
  else {
    let reader = new FileReader(); // NOTE: built-in method!
    reader.onload = function () {
      callback(reader.result);
    };
    reader.readAsText(files);
  }
}

// NOTE: receives the result of FileIO and
// in its callback, the model creation, etc. comes
function GCodeImporter() {}

GCodeImporter.importPath = function (path, callback) {
  FileIO.loadPath(path, function (gcode) {
    GCodeImporter.importText(gcode, callback);
  });
}

GCodeImporter.importText = function (gcode, callback) {
  let gcodeModel = gcode;
  callback(gcodeModel);
}


module.exports = {
  FileIO,
  GCodeImporter,
};
