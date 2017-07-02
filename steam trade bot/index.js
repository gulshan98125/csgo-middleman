const SteamUser = require('steam-user');
const SteamTotp = require('steam-totp');
const SteamCommunity = require('steamcommunity');
const TradeOfferManager = require('steam-tradeoffer-manager');
const client = new SteamUser();
const community = new SteamCommunity();

var app = require('express')();

var http = require('http').Server(app);
var request = require('request');
var io = require('socket.io')(http);
var cookie_reader = require('cookie');
var cookieParser = require('cookie-parser');
var querystring = require('querystring');
 
var redis = require('redis');
var sub = redis.createClient();





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

       console.log("recieved message: "+ message);
       var itemsIdWithSteamIdArray = JSON.parse("[" + message + "]"); // Items array with array[0] as steamid

        

       //Below is create and send POST message to Django server

         form = {
            'comment': message,
            'sessionid': socket.request.cookie['sessionid'],
        }

        var options = {
            uri : 'http://localhost:4000/node_api',
            method : 'POST',
            form : form
        }
        
        

        request(options, function (error, response, body) {
            

              if (!error && response.statusCode == 200) {
                console.log(body);
              }
              else {console.log("error");}
            })
    });
});


const manager = new TradeOfferManager({
    steam: client,
    community: community,
    language: 'en'
});


const logOnOptions = {
    accountName: 'gulshan98127',
    password: 'Montyhanda1',
    twoFactorCode: SteamTotp.generateAuthCode('V03wm9pAENwd5HIv6DrX45xquk0=')
};

client.logOn(logOnOptions);

client.on('loggedOn', () => {
    console.log('Logged into Steam');
    client.setPersona(SteamUser.Steam.EPersonaState.Online);
    client.gamesPlayed(730);
});

client.on('webSession', (sessionid, cookies) => {
    manager.setCookies(cookies);

    community.setCookies(cookies);
    community.startConfirmationChecker(10000, 'your_identity_secret');
});

manager.on('newOffer', (offer) => {
                        if (offer.itemsToGive.length == 0 && offer.itemsToReceive.length > 0) {
                        offer.accept((err, status) => {
            if (err) {
                console.log(err);
            } else {
                console.log('Accepted offer. Status: ${status}.');
            }
        });
                                }
                        else {
                        
                            }
    
        
    
});



http.listen(3000, function(){
  console.log('listening on *:3000');
});