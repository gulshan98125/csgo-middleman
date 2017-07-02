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
 
// var redis = require('redis');
// var sub = redis.createClient();




const manager = new TradeOfferManager({
    steam: client,
    community: community,
    language: 'en'
});


const logOnOptions = {
    accountName: 'gulshan98126',
    password: 'MAAchuda12345',
    twoFactorCode: SteamTotp.generateAuthCode('UA7FQ4kdg\/YTI2TjpYdunoeRPm4=')
};

client.logOn(logOnOptions);

client.on('loggedOn', () => {
    console.log('Logged into Steam');
    client.setPersona(SteamUser.Steam.EPersonaState.Online);
    client.gamesPlayed(730);
});

function depositItem(itemsArray, partnerid) {
    console.log("idtotrade: "+ partnerid);
    const partner = partnerid;
    const appid = 730;
    const contextid = 2;

    const offer = manager.createOffer(partner);

    manager.loadInventory(appid, contextid, true, (err, myInv) => {
        if (err) {
            console.log("reached here 0");
            console.log(err);
        } else {
            console.log("reached here 1");
            manager.loadUserInventory(partner, appid, contextid, true, (err, theirInv) => {
                if (err) {
                    console.log(err);
                } else {
                    console.log("reached here 2");
                    for(i=0; i<itemsArray.length; i++){
                     
                    const item = theirInv.find((item) => item.assetid ==''+itemsArray[i]);
                    console.log("got item number" + i);
                    console.log("added item: "+item);
                    offer.addTheirItem(item);    
                    
                    }

                    console.log("reached here 3");

                    offer.setMessage(`trade lelo :P`);
                    console.log("reached here 4");
                    offer.send((err, status) => {
                        if (err) {
                            console.log(err);
                        } else {
                            console.log(`Sent offer. Status: ${status}.`);
                        }
                    });
                }
            });
        }
    });
}


client.on('webSession', (sessionid, cookies) => {
    manager.setCookies(cookies);

    community.setCookies(cookies);
    community.startConfirmationChecker(10000, 'fkuKQSh352aYXGkR82Rh3fXEHA0=');

    
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
    // sub.on('message', function(channel, message){
    //     socket.send(message);
    // });
    
    //Client is sending message through socket.io
    socket.on('send_message', function (message) {

       console.log("recieved message: "+ message);

       var itemsIdWithSteamIdArray = message.split(','); // Items array with array[0] as steamid

       
       var itemsOnlyArray = [];
       for(j=1; j<itemsIdWithSteamIdArray.length; j++){
        itemsOnlyArray.push(itemsIdWithSteamIdArray[j]);
       }

        const partnerid = itemsIdWithSteamIdArray[0]+'';
        depositItem(itemsOnlyArray, partnerid);
        

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




http.listen(3000, function(){
  console.log('listening on *:3000');
});