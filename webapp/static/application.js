Dropzone.autoDiscover = false;
var dropzone = new Dropzone('form', {
  previewTemplate: document.querySelector('#preview-template').innerHTML,
  parallelUploads: 1,
  thumbnailHeight: 120,
  thumbnailWidth: 120,
  maxFilesize: 3,
  filesizeBase: 1000,
  sending: function(file, xhr) {
    console.log('sending', xhr);
    xhr.responseType = 'arraybuffer';
    xhr.responseText = null
  },
  thumbnail: function(file, dataUrl) {
    if (file.previewElement) {
      file.previewElement.classList.remove("dz-file-preview");
      var images = file.previewElement.querySelectorAll("[data-dz-thumbnail]");
      for (var i = 0; i < images.length; i++) {
        var thumbnailElement = images[i];
        thumbnailElement.alt = file.name;
        thumbnailElement.src = dataUrl;
      }
      setTimeout(function() { file.previewElement.classList.add("dz-image-preview"); }, 1);
    }
  }

});

dropzone.on("complete", function(file) {
  var blb = new Blob([file.xhr.response], {type: 'image/png'});
  var url = window.url = (window.URL || window.webkitURL).createObjectURL(blb);
  var img = new Image();
  img.src = url;
  $('.results').append(img)

});


// Now fake the file upload, since GitHub does not handle file uploads
// and returns a 404

// var minSteps = 6,
//   maxSteps = 60,
//   timeBetweenSteps = 100,
//   bytesPerStep = 100000;
//
// dropzone.uploadFiles = function(files) {
//   var self = this;
//
//   for (var i = 0; i < files.length; i++) {
//
//     var file = files[i];
//     totalSteps = Math.round(Math.min(maxSteps, Math.max(minSteps, file.size / bytesPerStep)));
//
//     for (var step = 0; step < totalSteps; step++) {
//       var duration = timeBetweenSteps * (step + 1);
//       setTimeout(function(file, totalSteps, step) {
//         return function() {
//           file.upload = {
//             progress: 100 * (step + 1) / totalSteps,
//             total: file.size,
//             bytesSent: (step + 1) * file.size / totalSteps
//           };
//
//           self.emit('uploadprogress', file, file.upload.progress, file.upload.bytesSent);
//           if (file.upload.progress == 100) {
//             file.status = Dropzone.SUCCESS;
//             self.emit("success", file, 'success', null);
//             self.emit("complete", file);
//             self.processQueue();
//           }
//         };
//       }(file, totalSteps, step), duration);
//     }
//   }
// }
//
// }