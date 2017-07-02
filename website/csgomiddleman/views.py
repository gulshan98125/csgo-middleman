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
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.publish('chat', user.username + ': ' + request.POST.get('comment'))
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
    trade.objects.create(user_giving_skins=request.user,trade_status="active", random_string=randomString, created_by=request.user)
    return HttpResponseRedirect(reverse('trade_page', kwargs={'randomString':randomString}))

@login_required
def trade_page(request, randomString):
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
    response2 = urllib2.urlopen('http://steamcommunity.com/profiles/'+steam64id+'/inventory/json/730/2')
    data2 = json.loads(response2.read())
    DictListofitems = data2['rgDescriptions']
    itemslist = []
    guns_icon_list = []
    for guns in DictListofitems:
        itemslist.append(DictListofitems[guns]['name'])
        guns_icon_list.append(DictListofitems[guns]['icon_url'])
    Dictidofitems = data2['rgInventory']
    idList =[]
    for itemsid in Dictidofitems:
        idList.append(itemsid)
    tupleList = list(zip(itemslist, idList, guns_icon_list))
    for (items,itemsid,guns) in tupleList:
        print (items+"----===---"+itemsid+guns)
    context = {'itemslist':itemslist,
    'profile_image_url_medium': profile_image_url_medium,
    'profile_image_url_large': profile_image_url_large,
    'profile_image_url_small': profile_image_url_small,
    'randomString': randomString,
    'username': username,
    'itemsidlist': idList,
    'tupleList': tupleList,
    'steamid': steam64id,
    }
    return render(request, 'trade/tradepage.html', context)

def Login(request):
    return RedirectToSteamSignIn('/process')

# /process
def LoginProcess(request):
    steamid = GetSteamID64(request.GET)
    if steamid == False:
        # login failed
        return HttpResponseRedirect('/login_failed')
    else:
        # login success
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