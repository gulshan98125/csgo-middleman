var app = require('express')();

var http = require('http').Server(app);
var request = require('request');
var io = require('socket.io')(http);
var cookie_reader = require('cookie');
var cookieParser = require('cookie-parser');
var querystring = require('querystring');
 
var redis = require('redis');
var sub = redis.createClient();

app.get('/', function(req, res){
  res.send('<h1>test place</h1>');
});


io.use(function(socket,accept){
    var data = socket.request;
    if(data.headers.cookie){
        data.cookie = cookie_reader.parse(data.headers.cookie);
        return accept(null, true);
    }
    return accept('error', false);
});


io.on('connection', function (socket) {
    console.log('\ngot a new connection from: ' + socket.id + '\n');
    
    //Grab message from Redis and send to client
    sub.on('message', function(channel, message){
        socket.send(message);
    });
    
    //Client is sending message through socket.io
    socket.on('send_message', function (message) {
        console.log(message+"TROLOLNIGGA");
        // values = querystring.stringify({
        //     comment: message,
        //     sessionid: socket.request.cookie['sessionid'],
        // });
        
         form = {
            'comment': message,
            'sessionid': socket.request.cookie['sessionid'],
        }

        console.log(socket.request.cookie['sessionid']);

        // var options = {
        //     host: 'localhost',
        //     port: 3000,
        //     path: '/node_api',
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/x-www-form-urlencoded',
        //         'Content-Length': values.length
        //     }
        // };

        var options = {
        	uri : 'http://localhost:4000/node_api',
        	method : 'POST',
        	form : form
        }
        
        //Send message to Django server
        // var req = http.get(options, function(res){
        //     res.setEncoding('utf8');
            
        //     //Print out error message
        //     res.on('data', function(message){
        //         if(message != 'Everything worked :)'){
        //             console.log('Message: ' + message);
        //         }
        //     });
        // });
        
        // req.write(values);
        // req.end();

		request(options, function (error, response, body) {
			console.log(options);
			console.log("request sent");

			  if (!error && response.statusCode == 200) {
			    console.log(body)
			    console.log(response) // Print the google web page.
			  }
			  else {console.log("error");}
			})
    });
});




http.listen(3000, function(){
  console.log('listening on *:3000');
});