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

var ActiveTradeOffersMap = {};  


 
 // STEAM BOT
const manager = new TradeOfferManager({
    steam: client,
    community: community,
    language: 'en'
});


const logOnOptions = {
    accountName: 'gulshan98127',
    password: 'Csgommbot12345',
    twoFactorCode: SteamTotp.generateAuthCode('V03wm9pAENwd5HIv6DrX45xquk0=')
};

client.logOn(logOnOptions);

client.on('loggedOn', () => {
    console.log('Logged into Steam');
    client.setPersona(SteamUser.Steam.EPersonaState.Online);
});

function sendItems(itemsArray, partnerid) {
    console.log("sending items back");
    manager.loadInventory(730, 2, true, (err, inventory) => {
        if (err) {
            console.log(err);
        } else {
            const offer = manager.createOffer(partnerid);
            for(i=0; i<itemsArray.length; i++){
                     
                    const item = inventory.find((item) => item.assetid ==''+itemsArray[i]);
                    console.log("got item number" + i);
                    offer.addMyItem(item);    
                    
                    }

            offer.setMessage(`you got items back :)`);
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
                    offer.addTheirItem(item);    
                    
                    }

                    console.log("reached here 3");

                    offer.setMessage(`Offer id: `+offer.id);
                    console.log("reached here 4");
                    offer.send((err, status) => {
                        if (err) {
                            console.log(err);
                        } else {
                            ActiveTradeOffersMap[parseInt(partnerid)] = offer.id;
                           
                            
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
    community.startConfirmationChecker(10000, 'oo7tg89iJEAEDFF5TwtKxTIpdiE=');

    
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



// SOCKETS

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

    socket.on('send_namesAndImages', function (message) { 

    // when skins names are send then send post message to django
        //server about submitting the skins names
        var Array_With_namesPLUSimage_And_RandomString = message.split('&&&');
        random_string = Array_With_namesPLUSimage_And_RandomString[1];
        var Array_skinsNamePlusImages = Array_With_namesPLUSimage_And_RandomString[0].split('$$$');
        skinsNames = Array_skinsNamePlusImages[0];
        console.log("names of guns: "+ skinsNames);
        skinsImages = Array_skinsNamePlusImages[1];
        console.log("image urls of guns: "+ skinsImages);

        if(Array_With_namesPLUSimage_And_RandomString.length>1){

            //submitting post request
             form = {
                                            'skinsNames': skinsNames,
                                            'skinsImages': skinsImages,
                                            'randomString':random_string,
                                        }

                                    var options = {
                                            uri : 'http://localhost:4000/submitSkinsNamesAndImages/',
                                            method : 'POST',
                                            form : form
                                        }

                    // update skins_submitted field of trade object
                                       request(options, function (error, response, body) {


                                              if (!error && response.statusCode == 200) {
                                                 console.log(body);
                                              }
                                              else {console.log("error");}
                                            })


        }
    });

    //Client is sending message through socket.io
    socket.on('send_skins', function (message) {

       console.log("recieved message: "+ message);

       var itemsId_WithSteamId_and_RandomString = message.split(','); // Items array with array[0] as steamid

       offer_accepted = "false";
       
        
        msg = "";

        if(itemsId_WithSteamId_and_RandomString.length>2){
            var itemsOnlyArray = [];
                   for(j=2; j<itemsId_WithSteamId_and_RandomString.length; j++){
                    itemsOnlyArray.push(itemsId_WithSteamId_and_RandomString[j]);
                   }

        const partnerid = itemsId_WithSteamId_and_RandomString[1]+'';
        const randomString = itemsId_WithSteamId_and_RandomString[0]+'';

            depositItem(itemsOnlyArray, partnerid);
            var refreshIntervalId = setInterval(function () {
                                manager.getOffer(ActiveTradeOffersMap[parseInt(partnerid)],(err,body) =>{
                                if (err) {
                                            console.log(err);
                                        } 
                                        else
                                        {
                                            if(body.state==7){
                                                console.log("Offer declined, Offer id: "+ ActiveTradeOffersMap[parseInt(partnerid)]);

                                                delete ActiveTradeOffersMap[parseInt(partnerid)];

                                                msg += "trade declined"
                                                socket.emit('message', msg, function(data){
                                                                console.log(data);
                                                           });
                                                msg = "";
                                                clearInterval(refreshIntervalId);
                                            }
                            else if (body.state==3){
                                console.log("Offer accepted,Offer id: "+ ActiveTradeOffersMap[parseInt(partnerid)]);
                            
                                body.getExchangeDetails(false,(err, status, tradeInitTime, recievedItems, sendItems) =>{
                                    if(err){
                                        
                                    }
                                    else {// WHEN THE TRADE OFFER IS ACCEPTED
                                        offer_accepted = "true";
                                        
                                        assetids = "";
                                        for(i=0;i<recievedItems.length-1;i++){
                                            assetids += recievedItems[i]['new_assetid'] + ",";
                                            
                                        }
                                        assetids += recievedItems[recievedItems.length-1]['new_assetid'];
                                        
                                        

                                form = {
                                            'assetids': assetids,
                                            'randomString': randomString,
                                        }

                                    var options = {
                                            uri : 'http://localhost:4000/submitSkins/',
                                            method : 'POST',
                                            form : form
                                        }
                                form2 = {
                                    'randomString': randomString,
                                }

                                    var optionsP = {
                                        uri : 'http://localhost:4000/updateTradeCreatedTime/',
                                            method : 'POST',
                                            form : form2
                                    }


                                    request(optionsP, function (error1, response1, body1) {


                                              if (!error1 && response1.statusCode == 200) {
                                                 
                                //when trade created time is update then send the skins ids

                                                 request(options, function (error, response, body) {


                                              if (!error && response.statusCode == 200) {
                                                 console.log(body);
                                              }
                                              else {console.log("error");}
                                            })
                                                    


                                              }
                                              else {console.log("error");}
                                            })



                    // update skins_submitted field of trade object
                                           //For every item in recievedItems do item.new_assetid


                                   



//Trade offer accepted last bracket below
                                                    }
                                                });
                                            

                                            
                                                delete ActiveTradeOffersMap[parseInt(partnerid)];
                                                msg += "trade Accepted!"
                                                socket.emit('message', msg, function(data){
                                                                console.log(data);
                                                           });
                                                msg = "";
                                                clearInterval(refreshIntervalId);



 console.log("checking and updating offer: "+randomString);

        var tradeRevertedUpdate_and_check = setInterval(function () {
        //send POST MESSAGE every 5 seconds TO update trade_reverted field

            form2 = {
                        'randomString': randomString,
                    }

            var options2 = {
                    uri : 'http://localhost:4000/updateTradeReverted/',
                    method : 'POST',
                    form : form2
            }

           request(options2, function (error, response, body) {


                  if (!error && response.statusCode == 200) {
                     // console.log(body);
                  }
                  else {console.log("error2");}
                })

           var options3 = {
            uri : 'http://localhost:4000/isTradeReverted/',
                    method : 'POST',
                    form : form2
           }

//SEND MESSAGE TO GET STATUS OF TRADE_REVERTED
           request(options3, function (error, response, body) {


                  if (!error && response.statusCode == 200) {
                     if(body=="false"){
                        //do nothing
                     }
                     else if(body != "false"){
                        //SEND BACK TRADE OFFER HERE RECEIVED BODY IS string of assetids
                        var Array_of_assetids_received = body.split(',');
                        sendItems(Array_of_assetids_received, partnerid);
                        //END THE INTERVAL
                        clearInterval(tradeRevertedUpdate_and_check);
                        // NOTIFY USER THROUGH SOCKET
                        socket.emit('message', "Trade has been sent back to you (time limit exceeded)", function(data){
                                                                console.log(data);
                                                           });
                     }
                  }
                  else {console.log("error3");}
                })

    }, 4000);    










                                            }
                                            else if (body.state==6){
                                                console.log("Offer cancelled");
                                                delete ActiveTradeOffersMap[parseInt(partnerid)];
                                                msg += "trade cancelled!"
                                                socket.emit('message', msg, function(data){
                                                                console.log(data);
                                                           });
                                                msg = "";
                                                clearInterval(refreshIntervalId);
                                            }
                                            else {console.log("waiting for offer accept");}
                                            
                                        }  
                                        });                                                    


                                                }, 10000);

        }
            else {
                    msg += "error empty offer"
                    socket.emit('message', msg, function(data){
                                                                console.log(data);
                                                           });
                    msg = "";
            }

if(offer_accepted=="true"){
      console.log("lel");



}
        
       
        

       //Below is create and send POST message to Django server

       
       

         
    });
});




http.listen(3000, function(){
  console.log('listening on *:3000');
});