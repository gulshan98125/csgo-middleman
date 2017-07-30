import urllib.request as  urllib2
import json
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
from django.conf import settings
from django.core.mail import send_mail, EmailMessage, get_connection
from django.contrib import messages
from django.contrib.auth import login as auth_login

# Create your views here.
@login_required
def afterLogin(request):
    profile = Profile.objects.get(user=request.user)
    if profile.steam_id:
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('steam_login_dashboard'))

@login_required
@csrf_exempt
def updateTradeUrl(request):
    if request.method == "POST":
        Profile_user_object = Profile.objects.get(user=request.user)
        Profile_user_object.tradeUrl = request.POST.get('tradeUrl')
        Profile_user_object.save()
        return HttpResponse("successfully updated trade url")
    else:
        return HttpResponse("error requested method doesn't exist")

@login_required
@csrf_exempt
def acceptTradedSkins(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.user_giving_money == request.user:
            tradeObject.trade_accepted_by_user_giving_money = True
            tradeObject.save()
            return HttpResponse(tradeObject.mobileNumber + ";" +tradeObject.expectedAmount)
        else:
            return HttpResponse("error invalid user")
    else:
        return HttpResponse("error requested method doesn't exist")

@login_required
@csrf_exempt
def sentMoney(request):
    if request.method == "POST":
        tradeObject = trade.objects.get(random_string=request.POST.get('randomString'))
        if tradeObject.user_giving_money == request.user:
            tradeObject.money_submitted = "true"
            tradeObject.money_received_accepted_by_user_giving_money = True
            tradeObject.save()
            return HttpResponse('success')
        else:
            return HttpResponse("error invalid user")
    else:
        return HttpResponse("error requested method doesn't exist")

@login_required
@csrf_exempt
def checkTradeUrl(request):
    if request.method == "POST":
        Profile_user_object = Profile.objects.get(user=request.user)
        if Profile_user_object.tradeUrl is None:
            return HttpResponse("error")
        elif len(Profile_user_object.tradeUrl) == 0:
            return HttpResponse("error")
        else:
            return HttpResponse("success")
    else:
        return HttpResponse("error requested method doesn't exist")

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
def faq(request):
    return render(request, 'questions/faq.html')

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

def registerPost(request):
    if(request.method=='POST'):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if(password==confirm_password):
            if(User.objects.filter(username=username).exists()):
                return HttpResponse('Username Already exists')
            if(User.objects.filter(email=email).exists()):
                return HttpResponse('Email Already exists')
            
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            randomString = get_random_string(length=15, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            Profile.objects.create(user=user, confirm_email_token=randomString)
        else:
            return HttpResponse('Passwords dont match.')
        from_email = settings.EMAIL_HOST_USER
        to_list = [email]
        subject = "csgomm store confirmation"
        message = "Hello "+ username +", you requested the email confirmation on csgomm.store. Click on the link below to confirm\n \n"
        message += '' + settings.DOMAIN + '/confirm_mail?user='+username+'&token='+randomString+'\n'
        message += 'If it is not done by you then ignore this mail.'
        print("sending mail")
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        print("mail sent")
        return HttpResponse("Confirmation Email has been sent to you")

def confirmMail(request):
    username = request.GET.get('user')
    token = request.GET.get('token')
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    if(profile.confirm_email_token == token):
        profile.isConfirmed = True
        profile.save()
        # messages.success(request,'Successfully confirmed')
        html = '<!DOCTYPE html><html><head></head><body>Your email has been confirmed <a href="'+settings.DOMAIN+'">login here</a></body></html>'
        return HttpResponse(html)
    else:
        # messages.warning(request,'Invalid Token')
        html2 = '<!DOCTYPE html><html><head></head><body> Error! Invalid token </body></html>'
        return HttpResponse(html2)
    return HttpResponseRedirect(reverse('login'))

def register(request):
    return render(request, 'registration/register.html')

def login(request):
    if(request.method == 'POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if(user is not None):
            profile = Profile.objects.get(user=user)
            if(profile.isConfirmed==True):
                auth_login(request, user)
                return HttpResponseRedirect(reverse('afterLogin'))
            else:
                return HttpResponse('Email Confirmation pending')
        else:
            return HttpResponse('Invalid Username/password')
    else:
        return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    Profile_user_object = Profile.objects.get(user=request.user)
    tradeUrl = Profile_user_object.tradeUrl
    steam64id = Profile_user_object.steam_id
    response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
    str_response = response.read().decode('utf-8')
    data = json.loads(str_response)
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
    'tradeUrl':tradeUrl,
    'domain':settings.DOMAIN,}
    return render(request, 'account/dashboard.html', context)

@login_required
def steam_login_dashboard(request):
    return render(request, 'account/steam_login_dashboard.html')

@login_required
def create_random_trade_skins(request):
    randomString = get_random_string(length=8, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    trade.objects.create(user_giving_skins=request.user, random_string=randomString, created_by=request.user, money_submitted="false",skins_submitted="false", trade_reverted="false")
    return HttpResponseRedirect(reverse('trade_page', kwargs={'rString':randomString}))

@login_required
def create_random_trade_paytm(request):
    randomString = get_random_string(length=8, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    trade.objects.create(user_giving_money=request.user, random_string=randomString, created_by=request.user, money_submitted="false",skins_submitted="false", trade_reverted="false")
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
                # FinalamountInInt = int(amountAfterCut)
                tradeObject.expectedAmount = str(amountInFloat)
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
        if timediff_inSeconds > 1200 and tradeObject.money_submitted=="false":
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
    Profile_user_object = Profile.objects.get(user=request.user)
    tradeUrl = Profile_user_object.tradeUrl
    if createdUser == request.user.username and tradeObject.user_giving_skins==request.user:
        #tradelink created by user giving skins
        Profile_user_object = Profile.objects.get(user=request.user)
        steam64id = Profile_user_object.steam_id
        response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
        str_response = response.read().decode('utf-8')
        data = json.loads(str_response)
        for jo in data:
            object = data[jo]['players']
        for oj in object:
            username = oj['personaname']
            profile_image_url_large = oj['avatarfull']
            profile_image_url_small = oj['avatar']
            profile_image_url_medium = oj['avatarmedium']
        response2 = urllib2.urlopen('http://steamcommunity.com/inventory/'+steam64id+'/730/2?l=english&count=5000')
        data2 = json.loads(response2.read().decode('utf-8'))
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
        'tradeUrl': tradeUrl,
        'domain':settings.DOMAIN}
        return render(request, 'trade/tradepage_skins.html',context)
    
    elif createdUser == request.user.username and tradeObject.user_giving_money==request.user:
        #tradelink created by user giving money
        Profile_user_object = Profile.objects.get(user=request.user)
        steam64id = Profile_user_object.steam_id
        response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
        data = json.loads(response.read().decode('utf-8'))
        for jo in data:
            object = data[jo]['players']
        for oj in object:
            username = oj['personaname']
            profile_image_url_large = oj['avatarfull']
        context = {'username':username,'randomString':rString,'domain':settings.DOMAIN,'steamid':steam64id,'tradeUrl':tradeUrl,'profile_image_url_large': profile_image_url_large}
        return render(request, 'trade/tradepage_money.html', context)
    else:
        if createdUser != request.user.username:
            if tradeObject.user_giving_money is None or tradeObject.user_giving_money==request.user:
                tradeObject.user_giving_money = request.user
                tradeObject.save()
                Profile_user_object = Profile.objects.get(user=request.user)
                steam64id = Profile_user_object.steam_id
                response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
                data = json.loads(response.read().decode('utf-8'))
                for jo in data:
                    object = data[jo]['players']
                for oj in object:
                    username = oj['personaname']
                    profile_image_url_large = oj['avatarfull']
                context = {'username':username,'randomString':rString,'domain':settings.DOMAIN,'steamid':steam64id,'tradeUrl':tradeUrl,'profile_image_url_large': profile_image_url_large}
                return render(request, 'trade/tradepage_money.html', context)
            elif tradeObject.user_giving_skins is None or tradeObject.user_giving_skins==request.user:    
                #when user came from tradelink created by money submitter
                tradeObject.user_giving_skins = request.user
                tradeObject.save()
                Profile_user_object = Profile.objects.get(user=request.user)
                steam64id = Profile_user_object.steam_id
                response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steam64id)
                data = json.loads(response.read().decode('utf-8'))
                for jo in data:
                    object = data[jo]['players']
                for oj in object:
                    username = oj['personaname']
                    profile_image_url_large = oj['avatarfull']
                    profile_image_url_small = oj['avatar']
                    profile_image_url_medium = oj['avatarmedium']
                response2 = urllib2.urlopen('http://steamcommunity.com/inventory/'+steam64id+'/730/2?l=english&count=5000')
                data2 = json.loads(response2.read().decode('utf-8'))
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
                'tradeUrl':tradeUrl,
                'domain':settings.DOMAIN}
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
            if tradeObject.trade_accepted_by_user_giving_money = True:
                return HttpResponse("user accepted submitted skins, waiting for his money sending")
            else:
                return HttpResponse("Skins submitted waiting for money")
        
        elif tradeObject.skins_submitted == "0":
            return HttpResponse("Trade Expired please create new")
        
        else:
            return HttpResponse("Skins depositor has sent the money")
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
        Profile_user_object = Profile.objects.get(user=request.user)
        Profile_user_object.steam_id = steamid
        Profile_user_object.save()
        print ("userwa is="+Profile_user_object.user.username+" with steamid = "+Profile_user_object.steam_id)
        response = urllib2.urlopen('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=7EC66869C567554434C440CFAD2BCEDB&steamids='+steamid)
        str_response = response.read().decode('utf-8')
        data = json.loads(str_response)
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
        'tradeUrl': "",
        'domain': settings.DOMAIN,}
    return render(request, 'account/dashboard.html', context)
