$(document).ready(function(){

var received = $('#console-log');


var socket;

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
  } else {
      socket = new WebSocket("ws://" + address + "/ws");
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
