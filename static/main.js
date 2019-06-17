$(document).ready(function(){

var received = $('#console-log');
var cam = document.getElementById("cam");

var socket;
var img_socket;

var sendMessage = function(message) {
  console.log("sending:" + message.data);
  socket.send(message.data);
};


// GUI Stuff

$("#ws-connect").click(function(ev){
  ev.preventDefault();
  var address = $('#ws-address').val();

  if(window.location.protocol == 'https:') {
      socket = new WebSocket("wss://" + address + "/ws");
      img_socket = new WebSocket("wss://" + address + "/camera");
  } else {
      socket = new WebSocket("ws://" + address + "/ws");
      img_socket = new WebSocket("ws://" + address + "/camera");
  }

  socket.onopen = function(){
    console.log("connected");
    $('#connection-status').removeClass('label-danger');
    $('#connection-status').addClass('label-success');
    $('#connection-status').text('connected');
  };

  socket.onmessage = function (message) {
    console.log("receiving: " + message.data);
    received.append(message.data);
    received.append($('<br/>'));
  };

  socket.onclose = function(){
    console.log("disconnected");
    $('#connection-status').removeClass('label-success');
    $('#connection-status').addClass('label-danger');
    $('#connection-status').text('disconnected');
  };

  img_socket.binaryType = 'arraybuffer';

  img_socket.onopen = function(){
    console.log("camera connected");
  };

  img_socket.onmessage = function (message) {
    if(typeof message.data == "object") {
        var arrayBuffer = message.data;
        var blob  = new Blob([new Uint8Array(arrayBuffer)], {type: "image/jpeg"});
        cam.src = window.URL.createObjectURL(blob);

        console.log(window.URL.createObjectURL(blob));
    } else {
        console.log("receiving: " + message.data);
    }
  };

  img_socket.onclose = function(){
    console.log("camera disconnected");
  };
});

// send a command to the serial port
$("#cmd_send").click(function(ev){
  ev.preventDefault();
  var cmd = $('#input-control-cmd').val();
  sendMessage({ 'data' : cmd});
  $('#input-control-cmd').val("");
});

$('#clear').click(function(){
  received.empty();
});


received.bind("DOMSubtreeModified",function(){
    received.animate({
        scrollTop: received.get(0).scrollHeight
    }, 0);
});

});
