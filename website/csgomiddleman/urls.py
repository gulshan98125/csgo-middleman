from django.conf.urls import url, include
from django.contrib.auth.views import login, logout, logout_then_login, password_change, password_change_done
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
url(r'^$', views.home, name='home'),
url(r'^node_api$', views.node_api, name='node_api'),
url(r'^login/$', login, name='login'),
# url(r'^register/$', views.register, name='register'),
url(r'^logout/$', logout, name='logout'),
url(r'^dashboard/$', views.dashboard, name='dashboard'),
url(r'^steam_login_dashboard/$', views.steam_login_dashboard, name='steam_login_dashboard'),
url(r'^create_random_trade/$', views.create_random_trade, name='create_random_trade'),
url(r'^trade_page/(?P<rString>[a-z A-Z 0-9]+)$', views.trade_page, name='trade_page'),
url(r'^steamlogin/$', views.Login, name='steamLogin'),
url(r'^process', views.LoginProcess, name='login_process'),
url(r'^submitSkins/$', views.submitSkins, name='submitSkins'),
url(r'^tradeAccepted/$', views.tradeAccepted, name='tradeAccepted'),
url(r'^isUser2connected/$', views.isUser2connected, name='isUser2connected'),
url(r'^tradeStatus/$', views.tradeStatus, name='tradeStatus'),
url(r'^isTradeReverted/$', views.isTradeReverted, name='isTradeReverted'),
url(r'^updateTradeReverted/$', views.updateTradeReverted, name='updateTradeReverted'),
]