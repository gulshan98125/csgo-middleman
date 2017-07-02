// const SteamUser = require('steam-user');
// const SteamTotp = require('steam-totp');
// const SteamCommunity = require('steamcommunity');
// const TradeOfferManager = require('steam-tradeoffer-manager');
// const client = new SteamUser();
// const community = new SteamCommunity();



var http = require('http');
var server = http.createServer().listen(80);
var io = require('socket.io')(http);
var cookie_reader = require('cookie');
var cookieParser = require('cookie-parser');
var querystring = require('querystring');
 
var redis = require('redis');
var sub = redis.createClient();

sub.subscribe('chat');
io.listen(server);
 
//Configure socket.io to store cookie set by Django
io.on('connection', function (socket) {
    console.log('\ngot a new connection from: ' + socket.id + '\n');
    
    //Grab message from Redis and send to client
    sub.on('message', function(channel, message){
        socket.send(message);
    });
    
    //Client is sending message through socket.io
    socket.on('send_message', function (message) {
        console.log(message);
        values = querystring.stringify({
            comment: message,
            sessionid: socket.handshake.cookie['sessionid'],
        });
        
        var options = {
            host: 'localhost',
            port: 3000,
            path: '/node_api',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': values.length
            }
        };
        
        //Send message to Django server
        var req = http.get(options, function(res){
            res.setEncoding('utf8');
            
            //Print out error message
            res.on('data', function(message){
                if(message != 'Everything worked :)'){
                    console.log('Message: ' + message);
                }
            });
        });
        
        req.write(values);
        req.end();
    });
});


io.use(function(socket, next) {
    var handshake = socket.request;

    if (!handshake) {
        return next(new Error('[[error:not-authorized]]'));
    }

    cookieParser(handshake, {}, function(err) {
        if (err) {
            return next(err);
        }

        var sessionID = handshake.signedCookies['express.sid'];

        db.sessionStore.get(sessionID, function(err, sessionData) {
            if (err) {
                return next(err);
            }
            console.log(sessionData);

            next();
        });
    });
});
 






// const manager = new TradeOfferManager({
// 	steam: client,
// 	community: community,
// 	language: 'en'
// });


// const logOnOptions = {
// 	accountName: 'gulshan98127',
// 	password: 'Montyhanda1',
// 	twoFactorCode: SteamTotp.generateAuthCode('V03wm9pAENwd5HIv6DrX45xquk0=')
// };

// client.logOn(logOnOptions);

// client.on('loggedOn', () => {
// 	console.log('Logged into Steam');
// 	client.setPersona(SteamUser.Steam.EPersonaState.Online);
// 	client.gamesPlayed(730);
// });

// client.on('webSession', (sessionid, cookies) => {
// 	manager.setCookies(cookies);

// 	community.setCookies(cookies);
// 	community.startConfirmationChecker(10000, 'your_identity_secret');
// });

// manager.on('newOffer', (offer) => {
// 						if (offer.itemsToGive.length == 0 && offer.itemsToReceive.length > 0) {
// 						offer.accept((err, status) => {
// 			if (err) {
// 				console.log(err);
// 			} else {
// 				console.log('Accepted offer. Status: ${status}.');
// 			}
// 		});
// 								}
// 						else {
						
// 							}
	
		
	
// });