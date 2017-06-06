// http://www.henryalgus.com/reading-binary-files-using-jquery-ajax/
/**
 *
 * jquery.binarytransport.js
 *
 * @description. jQuery ajax transport for making binary data type requests.
 * @version 1.0
 * @author Henry Algus <henryalgus@gmail.com>
 *
 */

// use this transport for "binary" data type
$.ajaxTransport("+binary", function(options, originalOptions, jqXHR){
  // check for conditions and support for blob / arraybuffer response type
  if (window.FormData && ((options.dataType && (options.dataType == 'binary')) || (options.data && ((window.ArrayBuffer && options.data instanceof ArrayBuffer) || (window.Blob && options.data instanceof Blob)))))
  {
    return {
      // create new XMLHttpRequest
      send: function(headers, callback){
        // setup all variables
        var xhr = new XMLHttpRequest(),
          url = options.url,
          type = options.type,
          async = options.async || true,
          // blob or arraybuffer. Default is blob
          dataType = options.responseType || "blob",
          data = options.data || null,
          username = options.username || null,
          password = options.password || null;

        xhr.addEventListener('load', function(){
          var data = {};
          data[options.dataType] = xhr.response;
          // make callback and send data
          callback(xhr.status, xhr.statusText, data, xhr.getAllResponseHeaders());
        });

        xhr.open(type, url, async, username, password);

        // setup custom headers
        for (var i in headers ) {
          xhr.setRequestHeader(i, headers[i] );
        }

        xhr.responseType = dataType;
        xhr.send(data);
      },
      abort: function(){
        console.log('aborted')
        // jqXHR.abort();
      }
    };
  }
});


// https://stackoverflow.com/questions/2320069/jquery-ajax-file-upload
var Upload = function (file) {
  this.file = file;
};

Upload.prototype.getType = function() {
  return this.file.type;
};
Upload.prototype.getSize = function() {
  return this.file.size;
};
Upload.prototype.getName = function() {
  return this.file.name;
};
Upload.prototype.doUpload = function (success) {
  var that = this;
  var formData = new FormData();

  // add assoc key values, this will be posts values
  formData.append("file", this.file, this.getName());
  formData.append("upload_file", true);

  return $.ajax({
    type: "POST",
    url: "predict",
    xhr: function () {
      var myXhr = $.ajaxSettings.xhr();
      if (myXhr.upload) {
        myXhr.upload.addEventListener('progress', that.progressHandling, false);
      }
      return myXhr;
    },
    success: success,
    // async: true,
    data: formData,
    cache: false,
    contentType: false,
    processData: false,
    // timeout: 60000,
    dataType: "binary",
    responseType: 'arraybuffer',
  });
};

Upload.prototype.progressHandling = function (event) {
  var percent = 0;
  var position = event.loaded || event.position;
  var total = event.total;
  var progress_bar_id = "#progress-wrp";
  if (event.lengthComputable) {
    percent = Math.ceil(position / total * 100);
  }
  // update progressbars classes so it fits your code
  $(progress_bar_id + " .progress-bar").css("width", +percent + "%");
  $(progress_bar_id + " .status").text(percent + "%");
};

function fixExifOrientation($img) {
  EXIF.getData($img[0], function() {
    // console.log('Exif=', EXIF.getTag(this, "Orientation"));
    switch(parseInt(EXIF.getTag(this, "Orientation"))) {
      case 2:
        $img.addClass('flip'); break;
      case 3:
        $img.addClass('rotate-180'); break;
      case 4:
        $img.addClass('flip-and-rotate-180'); break;
      case 5:
        $img.addClass('flip-and-rotate-270'); break;
      case 6:
        $img.addClass('rotate-90'); break;
      case 7:
        $img.addClass('flip-and-rotate-90'); break;
      case 8:
        $img.addClass('rotate-270'); break;
    }
  });
}

$('.another').click(function() {
  $('.results, #img-form').toggleClass('hidden');
})
$('#img-form-img').change(function() {
  var input = this;
  $('.results, #img-form').toggleClass('hidden');
  var reader = new FileReader();
  reader.onload = function (e) {
    var $preview = $('#preview');
    $preview.attr('src', e.target.result);
    setTimeout(function() {
      fixExifOrientation($preview);
      var rect = $preview[0].getBoundingClientRect();
      // $preview.css({height: rect.height, width: rect.width})
    }, 0);
    var upload = new Upload(input.files[0]);
    upload.doUpload(function(response) {
      window.response = response;
      var blb = new Blob([response], {type: 'image/png'});
      var url = window.url = (window.URL || window.webkitURL).createObjectURL(blb);
      $preview[0].src = url;
      $preview.removeClass();
    });
  };
  reader.readAsDataURL(input.files[0]);

});