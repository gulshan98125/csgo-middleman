from django.conf.urls import url, include
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done
from django.contrib.auth.decorators import login_required
from . import views
from django.contrib.auth.decorators import user_passes_test

login_forbidden =  user_passes_test(lambda u: u.is_anonymous(), '/dashboard/')

urlpatterns = [
url(r'^node_api$', views.node_api, name='node_api'),
url(r'^$', login_forbidden(views.login), name='login'),
url(r'^register/$', views.register, name='register'),
url(r'^registerPost/$', views.registerPost, name='registerPost'),
url(r'^confirm_mail/$', views.confirmMail, name='confirmMail'),
url(r'^logout/$', logout, name='logout'),
url(r'^afterLogin/$', views.afterLogin, name='afterLogin'),
url(r'^dashboard/$', views.dashboard, name='dashboard'),
url(r'^steam_login_dashboard/$', views.steam_login_dashboard, name='steam_login_dashboard'),
url(r'^create_random_trade_skins/$', views.create_random_trade_skins, name='create_random_trade_skins'),
url(r'^create_random_trade_paytm/$', views.create_random_trade_paytm, name='create_random_trade_paytm'),
url(r'^trade_page/(?P<rString>[a-z A-Z 0-9]+)$', views.trade_page, name='trade_page'),
url(r'^steamlogin/$', views.Login, name='steamLogin'),
url(r'^process', views.LoginProcess, name='login_process'),
url(r'^submitSkins/$', views.submitSkins, name='submitSkins'),
url(r'^getSkinsNames/$', views.getSkinsNames, name='getSkinsNames'),
url(r'^getSkinsUrls/$', views.getSkinsUrls, name='getSkinsUrls'),
url(r'^getInspectLinks/$', views.getInspectLinks, name='getInspectLinks'),
url(r'^getAmount/$', views.getAmount, name='getAmount'),
url(r'^updateTradeCreatedTime/$', views.updateTradeCreatedTime, name='updateTradeCreatedTime'),
url(r'^submitSkinsNamesAndImages/$', views.submitSkinsNamesAndImages, name='submitSkinsNamesAndImages'),
url(r'^submitNumberAndMoney/$', views.submitNumberAndMoney, name='submitNumberAndMoney'),
url(r'^tradeAccepted/$', views.tradeAccepted, name='tradeAccepted'),
url(r'^isUser2connected/$', views.isUser2connected, name='isUser2connected'),
#user2 is user giving money
url(r'^isUser1connected/$', views.isUser1connected, name='isUser1connected'),
#user1 is user giving skins
url(r'^tradeStatus/$', views.tradeStatus, name='tradeStatus'),
url(r'^isTradeReverted/$', views.isTradeReverted, name='isTradeReverted'),
url(r'^updateTradeReverted/$', views.updateTradeReverted, name='updateTradeReverted'),
url(r'^faq/$', views.faq, name='faq'),
url(r'^updateTradeUrl/$', views.updateTradeUrl, name='updateTradeUrl'),
url(r'^checkTradeUrl/$', views.checkTradeUrl, name='checkTradeUrl'),
url(r'^acceptTradedSkins/$', views.acceptTradedSkins, name='acceptTradedSkins'),
url(r'^sentMoney/$', views.sentMoney, name='sentMoney'),
url(r'^receivedMoney/$', views.receivedMoney, name='receivedMoney'),
url(r'^isTradeCompleted/$', views.isTradeCompleted, name='isTradeCompleted'),
url(r'^tradeUrl_Steamid_AndAssetIds/$', views.tradeUrl_Steamid_AndAssetIds, name='tradeUrl_Steamid_AndAssetIds'),
url(r'^finishTrade/$', views.finishTrade, name='finishTrade'),
url(r'^submitInspectLinks/$', views.submitInspectLinks, name='submitInspectLinks'),
url(r'^parseJson/$', views.parseJson, name='parseJson'),
]
