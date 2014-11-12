$(window).ready(function(){
  var api = new $.ApiWeb('apis');

  api.on('ready', function(a) {
    console.log("api started.");
    console.log(api);
  });

  api.on('event', function(a, value) {
    console.log('event:' + value);
  });
});
