import urllib.request as urllib2
import json
import redis
from django.shortcuts import render
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
        print (user_id)
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
    return render(request, 'account/dashboard.html', {'user': request.user})

@login_required
def steam_login_dashboard(request):
    return render(request, 'account/steam_login_dashboard.html')

@login_required
def create_random_trade(request):
    randomString = get_random_string(length=8, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    trade.objects.create(user_giving_skins=request.user, random_string=randomString, created_by=request.user, money_submitted="false",skins_submitted="false", amount_submitted="0")
    return HttpResponseRedirect(reverse('trade_page', kwargs={'rString':randomString}))

@login_required
def trade_page(request, rString):
    tradeObject = trade.objects.get(random_string=rString)
    createdUser = tradeObject.created_by
    if createdUser == request.user.username:
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
                    itemslistNew.append(description['name'])
                    new_guns_icon_list.append(description['icon_url'])
                    idList.append(item['assetid'])
                    break

        print ("length of Id list")
        print (len(idList))

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
        return render(request, 'trade/tradepage.html', context)
    else:
        tradeObject.user_giving_money = request.user
        tradeObject.save()
        return render(request, 'trade/user2.html')

@login_required
def Login(request):
    return RedirectToSteamSignIn('/process')

@csrf_exempt
def tradeStatus(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.skins_submitted == "false" and tradeObject.money_submitted == "false":
            return HttpResponse("Nothing submitted")
        elif tradeObject.skins_submitted == "false" and tradeObject.money_submitted == "true":
            return HttpResponse("Money submitted")
        elif tradeObject.skins_submitted == "true" and tradeObject.money_submitted == "false":
            return HttpResponse("Skins submitted")
        else:
            return HttpResponse("Skins and Money Both submitted")
    else:
        return HttpResponse("error requested method doesn't exist")

@csrf_exempt
def submitSkins(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        assets = request.POST.get('assetids')
        tradeObject.skins_assetids = assets
        tradeObject.skins_submitted = "true"
        tradeObject.save()
        return HttpResponse("success skins submitted!")
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
            return HttpResponse("user "+tradeObject.user_giving_money.username+" connected")
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