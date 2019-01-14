from django.conf.urls import url
from tourism import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    url(r'^$', views.home, name='home'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.Login, name='Login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^account_activation_sent/$', views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    url(r'^user_profile/$', views.user_profile, name='user_profile'),
    url(r'^user_bookings/$', views.user_bookings, name='user_bookings'),
    url(r'^remove/(?P<pk>.+)/$', views.remove_booking, name='remove_booking'),

    url(r'^payment/(?P<pk>.+)/$', views.payment, name='payment'),
    url(r'^payment/success$', views.payment_success, name="payment_success"),
    url(r'^payment/failure$', views.payment_failure, name="payment_failure"),

]
