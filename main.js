$(document).ready(function(){

var received = $('#console-log');


var socket = new WebSocket("ws://" + window.location.hostname + ":8080/ws");

socket.onopen = function(){
  console.log("connected");
};

socket.onmessage = function (message) {
  console.log("receiving: " + message.data);
  received.append(message.data);
  received.append($('<br/>'));
};

socket.onclose = function(){
  console.log("disconnected");
};

var sendMessage = function(message) {
  console.log("sending:" + message.data);
  socket.send(message.data);
};


// GUI Stuff


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
