import urllib.request as urllib2
import json
import redis
from django.shortcuts import render
import datetime
from django.utils.timezone import utc
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.core.urlresolvers import reverse_lazy, reverse
from .models import trade, Profile, Comments
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from steamauth import RedirectToSteamSignIn, GetSteamID64

# Create your views here.
@login_required
def afterLogin(request):
    if Profile.objects.filter(user=request.user).exists():
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('steam_login_dashboard'))

@csrf_exempt
def updateTradeCreatedTime(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        tradeObject.time_posted = datetime.datetime.utcnow().replace(tzinfo=utc)
        tradeObject.save()
        return HttpResponse("success")
    else:
        return HttpResponse("error requested method doesn't exist")

@login_required
def home(request):
    comments = Comments.objects.select_related().all()[0:100]
    return render(request, 'chat/index.html', locals())

@csrf_exempt
def node_api(request):
    if request.method == "POST":
        #Get User from sessionid
        session = Session.objects.get(session_key=request.POST.get('sessionid'))

        # print (request.session.session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        #Create comment
        Comments.objects.create(user=user, text=request.POST.get('comment'))
        #Once comment has been created post it to the chat channel
        # r = redis.StrictRedis(host='localhost', port=6379, db=0)
        # r.publish('chat', user.username + ': ' + request.POST.get('comment'))
        return HttpResponse("recieved trade from: "+user.username+"("+user_id+"), msg = "+ request.POST.get('comment'))
    else:
        return HttpResponse("error :(")

@login_required
def dashboard(request):
    Profile_user_object = Profile.objects.get(user=request.user)
    steam64id = Profile_user_object.steam_id
    response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
    data = json.load(response)
    for jo in data:
        object = data[jo]['players']
    for oj in object:
        profile_image_url_medium = oj['avatarmedium']
        profile_image_url_large = oj['avatarfull']
        profile_image_url_small = oj['avatar']
    context = {'steamid': steam64id,
    'profile_image_url_medium': profile_image_url_medium,
    'profile_image_url_large': profile_image_url_large,
    'profile_image_url_small': profile_image_url_small,
    }
    return render(request, 'account/dashboard.html', context)

@login_required
def steam_login_dashboard(request):
    return render(request, 'account/steam_login_dashboard.html')

@login_required
def create_random_trade_skins(request):
    randomString = get_random_string(length=8, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    trade.objects.create(user_giving_skins=request.user, random_string=randomString, created_by=request.user, money_submitted="false",skins_submitted="false", amount_submitted="0", trade_reverted="false", money_reverted="false")
    return HttpResponseRedirect(reverse('trade_page', kwargs={'rString':randomString}))

@login_required
def create_random_trade_paytm(request):
    randomString = get_random_string(length=8, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    trade.objects.create(user_giving_money=request.user, random_string=randomString, created_by=request.user, money_submitted="false",skins_submitted="false", amount_submitted="0", trade_reverted="false", money_reverted="false")
    return HttpResponseRedirect(reverse('trade_page', kwargs={'rString':randomString}))

@csrf_exempt
def isTradeReverted(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.trade_reverted=="false":
            return HttpResponse("false")
        elif tradeObject.trade_reverted=="true":
            return HttpResponse(tradeObject.skins_assetids)
        else:
            return HttpResponse("false")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
@login_required
def submitNumberAndMoney(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.user_giving_skins == request.user:
            if len(request.POST.get('mobileNumber')) == 10 and len(request.POST.get('expectedAmount')) > 0:
                tradeObject.mobileNumber = request.POST.get('mobileNumber')
                amountInFloat = float(request.POST.get('expectedAmount'))
                amountAfterCut = amountInFloat + (amountInFloat*0.0069)
                # FinalamountInInt = int(amountAfterCut)
                tradeObject.expectedAmount = str(amountAfterCut)
                tradeObject.save()
                return HttpResponse("successfully updated")
            else:
                return HttpResponse("error! invalid fields value")
        else:
            return HttpResponse("error")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def updateTradeReverted(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        postedTime = tradeObject.time_posted
        timediff = datetime.datetime.utcnow().replace(tzinfo=utc) - postedTime
        timediff_inSeconds = timediff.total_seconds()
        if timediff_inSeconds > 120 and tradeObject.money_submitted=="false":
            tradeObject.trade_reverted = "true"
            tradeObject.skins_submitted = "0"
            tradeObject.save()
            return HttpResponse("success trade_reverted changed")
        else:
            return HttpResponse("no change made to trade_reverted")
    else:
        return HttpResponse("error requested method doesn't exist")


@login_required
def trade_page(request, rString):
    tradeObject = trade.objects.get(random_string=rString)
    createdUser = tradeObject.created_by
    if createdUser == request.user.username and tradeObject.user_giving_skins==request.user:
        #tradelink created by user giving skins
        Profile_user_object = Profile.objects.get(user=request.user)
        steam64id = Profile_user_object.steam_id
        response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
        data = json.load(response)
        for jo in data:
            object = data[jo]['players']
        for oj in object:
            username = oj['personaname']
            profile_image_url_large = oj['avatarfull']
            profile_image_url_small = oj['avatar']
            profile_image_url_medium = oj['avatarmedium']
        response2 = urllib2.urlopen('http://steamcommunity.com/inventory/'+steam64id+'/730/2?l=english&count=5000')
        data2 = json.loads(response2.read())
        DictListofitems = data2['descriptions']
        guns_icon_list = []
        itemsToSkipList= []
        itemslistNew = []
        new_guns_icon_list = []

        Dictidofitems = data2['assets']
        idList =[]
        for item in Dictidofitems:
            classid = item['classid']
            instanceid = item['instanceid']
            
            for description in DictListofitems:
                if description['instanceid']==instanceid and description['classid']==classid and description['tradable']==1:
                    itemslistNew.append(description['market_hash_name'])
                    new_guns_icon_list.append(description['icon_url'])
                    idList.append(item['assetid'])
                    break


        tupleList = list(zip(itemslistNew, idList, new_guns_icon_list))
        context = {'profile_image_url_medium': profile_image_url_medium,
        'profile_image_url_large': profile_image_url_large,
        'profile_image_url_small': profile_image_url_small,
        'randomString': rString,
        'username': username,
        'itemsidlist': idList,
        'tupleList': tupleList,
        'steamid': steam64id,
        }
        return render(request, 'trade/tradepage_skins.html', context)
    
    elif createdUser == request.user.username and tradeObject.user_giving_money==request.user:
        #tradelink created by user giving money
        Profile_user_object = Profile.objects.get(user=request.user)
        steam64id = Profile_user_object.steam_id
        response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
        data = json.load(response)
        for jo in data:
            object = data[jo]['players']
        for oj in object:
            username = oj['personaname']
            profile_image_url_large = oj['avatarfull']
        context = {'username':username,'randomString':rString,'steamid':steam64id,'profile_image_url_large': profile_image_url_large}
        return render(request, 'trade/tradepage_money.html', context)
    else:
        if createdUser != request.user.username:
            if tradeObject.user_giving_money is None or tradeObject.user_giving_money==request.user:
                tradeObject.user_giving_money = request.user
                tradeObject.save()
                Profile_user_object = Profile.objects.get(user=request.user)
                steam64id = Profile_user_object.steam_id
                response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
                data = json.load(response)
                for jo in data:
                    object = data[jo]['players']
                for oj in object:
                    username = oj['personaname']
                    profile_image_url_large = oj['avatarfull']
                context = {'username':username,'randomString':rString,'steamid':steam64id,'profile_image_url_large': profile_image_url_large}
                return render(request, 'trade/tradepage_money.html', context)
            elif tradeObject.user_giving_skins is None or tradeObject.user_giving_skins==request.user:    
                #when user came from tradelink created by money submitter
                tradeObject.user_giving_skins = request.user
                tradeObject.save()
                Profile_user_object = Profile.objects.get(user=request.user)
                steam64id = Profile_user_object.steam_id
                response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
                data = json.load(response)
                for jo in data:
                    object = data[jo]['players']
                for oj in object:
                    username = oj['personaname']
                    profile_image_url_large = oj['avatarfull']
                    profile_image_url_small = oj['avatar']
                    profile_image_url_medium = oj['avatarmedium']
                response2 = urllib2.urlopen('http://steamcommunity.com/inventory/'+steam64id+'/730/2?l=english&count=5000')
                data2 = json.loads(response2.read())
                DictListofitems = data2['descriptions']
                guns_icon_list = []
                itemsToSkipList= []
                itemslistNew = []
                new_guns_icon_list = []

                Dictidofitems = data2['assets']
                idList =[]
                for item in Dictidofitems:
                    classid = item['classid']
                    instanceid = item['instanceid']
                    
                    for description in DictListofitems:
                        if description['instanceid']==instanceid and description['classid']==classid and description['tradable']==1:
                            itemslistNew.append(description['market_hash_name'])
                            new_guns_icon_list.append(description['icon_url'])
                            idList.append(item['assetid'])
                            break


                tupleList = list(zip(itemslistNew, idList, new_guns_icon_list))
                context = {'profile_image_url_medium': profile_image_url_medium,
                'profile_image_url_large': profile_image_url_large,
                'profile_image_url_small': profile_image_url_small,
                'randomString': rString,
                'username': username,
                'itemsidlist': idList,
                'tupleList': tupleList,
                'steamid': steam64id,
                }
                return render(request, 'trade/tradepage_skins.html', context)


@login_required
def Login(request):
    return RedirectToSteamSignIn('/process')

@csrf_exempt
def tradeStatus(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.skins_submitted == "false" and tradeObject.money_submitted == "false":
            return HttpResponse("waiting for skins/keys")
        elif tradeObject.skins_submitted == "false" and tradeObject.money_submitted == "true":
            return HttpResponse("Money submitted not the skins")
        elif tradeObject.skins_submitted == "true" and tradeObject.money_submitted == "false":
            return HttpResponse("Skins submitted waiting for money")
        elif tradeObject.skins_submitted == "0":
            return HttpResponse("Trade Expired please create new")
        else:
            return HttpResponse("Skins and Money Both submitted")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def getSkinsNames(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        return HttpResponse(tradeObject.skins_submitted_name)
    else:
        return HttpResponse("error requested method doesn't exist")
@csrf_exempt
def getSkinsUrls(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        return HttpResponse(tradeObject.skins_submitted_icons)
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def getAmount(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        return HttpResponse(tradeObject.expectedAmount)
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def submitSkins(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        assets = request.POST.get('assetids')
        if tradeObject.skins_assetids is None:
            tradeObject.skins_assetids = assets
        else:
            tradeObject.skins_assetids = tradeObject.skins_assetids + ","+assets
        tradeObject.skins_submitted = "true"
        tradeObject.save()
        return HttpResponse("success skins submitted!")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def submitSkinsNamesAndImages(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        tradeObject.skins_submitted_name = request.POST.get('skinsNames')
        tradeObject.skins_submitted_icons = request.POST.get('skinsImages')
        tradeObject.save()
        return HttpResponse("success")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
@login_required
def isUser2connected(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.user_giving_money is None:
            return HttpResponse('error')
        else:
            return HttpResponse(tradeObject.user_giving_money.username+" connected")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
@login_required
def isUser1connected(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.user_giving_skins is None:
            return HttpResponse('error')
        else:
            return HttpResponse(tradeObject.user_giving_skins.username+" connected")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def tradeAccepted(request):
    if request.method == "POST":
        return HttpResponse("Success :)")
    else:
        return HttpResponse("error! GET Request")


@login_required
def LoginProcess(request):
    steamid = GetSteamID64(request.GET)
    if steamid == False:
        # login failed
        return HttpResponse("ERROR! Login failed")
    else:
        # login success
        if Profile.objects.filter(user=request.user).exists():
            print ("")
        else:
            Profile.objects.create(user = request.user,steam_id=steamid)
        Profile_user_object = Profile.objects.get(user=request.user)
        Profile_user_object.steam_id = steamid
        Profile_user_object.save()
        print ("userwa is="+Profile_user_object.user.username+" with steamid = "+Profile_user_object.steam_id)
        response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steamid)
        data = json.load(response)
        for jo in data:
            object = data[jo]['players']
        for oj in object:
            profile_image_url_medium = oj['avatarmedium']
            profile_image_url_large = oj['avatarfull']
            profile_image_url_small = oj['avatar']
        context = {'steamid': steamid,
        'profile_image_url_medium': profile_image_url_medium,
        'profile_image_url_large': profile_image_url_large,
        'profile_image_url_small': profile_image_url_small,
        }
    return render(request, 'account/dashboard.html', context)