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

function sendItems(itemsArray, partnerid, tradeUrl) {
    console.log("sending items back");
    manager.loadInventory(730, 2, true, (err, inventory) => {
        if (err) {
            console.log(err);
        } else {
            const offer = manager.createOffer(tradeUrl);
            for(i=0; i<itemsArray.length; i++){
                     
                    var item = inventory.find((item) => item.assetid ==''+itemsArray[i]);
                    console.log("sending back item number" + i);
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



function depositSkinsUrlAndNames(itemsArray, partnerid, tradeUrl, randomString) {
	const partner = partnerid;
    const appid = 730;
    const contextid = 2;
    var skinsImageUrls = "";
    var skinsNames = "";
    manager.loadUserInventory(partner, appid, contextid, true, (err, theirInv) => {
    	for(i=0; i<itemsArray.length-1; i++){
    	var item = theirInv.find((item) => item.assetid ==''+itemsArray[i]);
        var url = item.getImageURL() + "128x128";
        skinsImageUrls += url + ";";
        skinsNames += item.market_hash_name +";";

    }
    var item = theirInv.find((item) => item.assetid ==''+itemsArray[itemsArray.length-1]);
    var url = item.getImageURL() + "128x128";
    skinsImageUrls += url;
    skinsNames = item.market_hash_name;
    console.log("item description array is:"+ item.descriptions);


	form = {
	            'skinsNames': skinsNames,
	            'skinsImages': skinsImageUrls,
	            'randomString':randomString,
	        }

    var options = {
            uri : 'http://www.csgomm.store/submitSkinsNamesAndImages/',
            method : 'POST',
            form : form
        }

			request(options, function (error, response, body) {


			          if (!error && response.statusCode == 200) {
			             // console.log(body);
			          }
			          else {console.log("error");}
			        })


    
    });
}




function depositItem(itemsArray, partnerid, tradeUrl) {
    console.log("idtotrade: "+ partnerid);
    const partner = partnerid;
    const appid = 730;
    const contextid = 2;

    const offer = manager.createOffer(tradeUrl);

    manager.loadInventory(appid, contextid, true, (err, myInv) => {
        if (err) {
            console.log(err);
        } else {
            manager.loadUserInventory(partner, appid, contextid, true, (err, theirInv) => {
                if (err) {
                    console.log(err);
                } else {
                    for(i=0; i<itemsArray.length; i++){
                     
                    var item = theirInv.find((item) => item.assetid ==''+itemsArray[i]);
                    console.log("added item number" + i);
                    offer.addTheirItem(item);    
                    
                    }

                    offer.setMessage(`from csgomm.store`);
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


    socket.on('send_inspectItemsAndRandomString', function (message) { 

        array_with_inspectItems_PLUS_randomString = message.split('$$$');
        randomString = array_with_inspectItems_PLUS_randomString[1];
        inspectItems = array_with_inspectItems_PLUS_randomString[0];

        if(array_with_inspectItems_PLUS_randomString.length >1){

            form = {
                                            'inspectLinks': inspectItems,
                                            'randomString':randomString,
                                        }

            var options = {
                uri : 'http://www.csgomm.store/submitInspectLinks/',
                method : 'POST',
                form : form
            }

            request(options, function (error, response, body) {
                // inspect links submitted
            })
        }

        });


    //Client is sending message through socket.io
    socket.on('send_skins', function (message) {

      // console.log("recieved message: "+ message);

       var itemsId_WithSteamId_and_RandomString = message.split(','); // Items array with array[0] as steamid

       offer_accepted = "false";
       
        
        msg = "";

        if(itemsId_WithSteamId_and_RandomString.length>3){
            var itemsOnlyArray = [];
                   for(j=3; j<itemsId_WithSteamId_and_RandomString.length; j++){
                    itemsOnlyArray.push(itemsId_WithSteamId_and_RandomString[j]);
                   }

        const tradeUrl = itemsId_WithSteamId_and_RandomString[0] +'';
        const partnerid = itemsId_WithSteamId_and_RandomString[2]+'';
        const randomString = itemsId_WithSteamId_and_RandomString[1]+'';
            depositItem(itemsOnlyArray, partnerid, tradeUrl);
            depositSkinsUrlAndNames(itemsOnlyArray, partnerid, tradeUrl, randomString);
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
                                            uri : 'http://www.csgomm.store/submitSkins/',
                                            method : 'POST',
                                            form : form
                                        }
                                form2 = {
                                    'randomString': randomString,
                                }

                                    var optionsP = {
                                        uri : 'http://www.csgomm.store/updateTradeCreatedTime/',
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
                    uri : 'http://www.csgomm.store/updateTradeReverted/',
                    method : 'POST',
                    form : form2
            }

           request(options2, function (error, response, body) {


                  if (!error && response.statusCode == 200) {
                     if(body=="Attempted trade scam"){
                        //Stop the trade and inform about scam
                     }
                  }
                  else {console.log("error2");}
                })

           var options3 = {
            uri : 'http://www.csgomm.store/isTradeReverted/',
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
                        sendItems(Array_of_assetids_received, partnerid, tradeUrl);
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

    }, 10000);    


	console.log("checking whether trade is completed or not ");
        var tradeStatusCompletedCheck = setInterval(function () {

            form5 = {
                        'randomString': randomString,
                    }

                    var optionsN = {
                    uri : 'http://www.csgomm.store/isTradeCompleted/',
                    method : 'POST',
                    form : form5
            }

            request(optionsN, function (errorN, responseN, bodyN) {
		
                if(bodyN=="true"){
		console.log("trade is accepted by both parties");		

                    var optionsP = {
                    uri : 'http://www.csgomm.store/tradeUrl_Steamid_AndAssetIds/',
                    method : 'POST',
                    form : form5
            }

                    request(optionsP, function (error2, response2, body2) {
			console.log("Sending the trade to the other user");

                        var array_assetidsAndtradeUrl_Plus_steamid = body2.split('&&&');
                        steamdIdofTheUser = array_assetidsAndtradeUrl_Plus_steamid[1]
                        var array_assetids_PLUS_tradeUrl = array_assetidsAndtradeUrl_Plus_steamid[0].split(';;;');
                        stringOfAssetIds = array_assetids_PLUS_tradeUrl[0];
                        tradeUrlOfTheUser = array_assetids_PLUS_tradeUrl[1];
                        arrayOfAssetIds = stringOfAssetIds.split(',');

                        sendItems(arrayOfAssetIds, steamdIdofTheUser, tradeUrlOfTheUser);

                        var optionsQ = {
                                                uri : 'http://www.csgomm.store/finishTrade/',
                                                method : 'POST',
                                                form : form5
                                        }

                        request(optionsQ, function (error3, response3, body3) {
                            //TRADE FINISHED AYE
                            clearInterval(tradeStatusCompletedCheck);
                            

                        })

                    })
                    //Send skins to the money sender



                }

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
