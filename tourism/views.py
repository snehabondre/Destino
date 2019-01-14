# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Mobile
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .forms import SignUpForm, MobileForm
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import AuthenticationForm
import smtplib
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from .models import Packages, Bookings
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging, traceback
from django.core.urlresolvers import reverse
import hashlib
from random import randint
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

PAID_FEE_AMOUNT = 0

# Create your views here.
def home(request):
    return render(request, 'tourism/index.html')


# ------------For Users -------------
def signup(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        mobile_form = MobileForm(request.POST)
        if user_form.is_valid() and mobile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()

            user.mobile.Mobile_Number = mobile_form.cleaned_data.get('Mobile_Number')
            user.mobile.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Destino Account'
            message = render_to_string('tourism/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request, 'tourism/account_activation_sent.html')
        else:
            print(user_form)
            redirect(request.META['HTTP_REFERER'])

    else:
        user_form = SignUpForm()
        mobile_form = MobileForm()
    context = {
        "user_form": user_form,
        "Mobile_form": mobile_form,
        'errors': user_form.errors,
    }
    return render(request, 'tourism/account_registrations.html', context)


def account_activation_sent(request):
    return render(request, 'tourism/account_activation_sent.html')


def activate(request, uidb64, token, ):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.mobile.email_confirmed = True
        user.mobile.save()
        user.save()
        login(request, user, backend='django.core.mail.backends.smtp.EmailBackend')
        return redirect('tourism:home')
    else:
        return render(request, 'tourism/account_activation_invalid.html')


def Login(request):
    error_message = ""

    if request.method == 'POST':
        login_form = AuthenticationForm(request.POST or None)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('tourism:user_profile')
        else:

            error_message = "Incorrect username or password."
            messages.error(request, error_message)
            login_form = AuthenticationForm(request.POST or None)

    else:
        login_form = AuthenticationForm()
    return render(request, 'tourism/account_registrations.html', {'login_form': login_form, 'error_message': error_message})

def user_profile(request):
    query = request.GET.get("q")
    queryset_list = Packages.objects.all().order_by('Price')
    if query:
        queryset_list = queryset_list.filter(Q(location__icontains=query)).distinct().order_by('Price')

   
    paginator = Paginator(queryset_list, 3)
    page_change_var = 'page'  # change=request
    page = request.GET.get(page_change_var)
    try:
        queryset_list = paginator.page(page)
    except PageNotAnInteger:
        queryset_list = paginator.page(1)
    except EmptyPage:
        queryset_list = paginator.page(paginator.num_pages)

    context = {
        'page_change_var':page_change_var,
        'packages':queryset_list,
    }
    return render(request, 'tourism/user_profile.html', context)


def user_bookings(request):
    bookings = Bookings.objects.filter(user=request.user)

    context = {
        'bookings': bookings
    }
    return render(request, 'tourism/user_bookings.html', context)

def remove_booking(request,pk):
    instance = Bookings.objects.get(pk=pk)
    instance.delete()
    return redirect('tourism:user_bookings')

@login_required
def payment(request, pk):
    get_package = Packages.objects.get(pk=pk)
    global PAID_FEE_AMOUNT
    PAID_FEE_AMOUNT=get_package.Price
    user = request.user
    get_user = get_object_or_404(User, username=user)
    data = {}
    txnid = get_transaction_id(request)
    hash_ = generate_hash(request, txnid)
    hash_string = get_hash_string(request, txnid)
    
    # use constants file to store constant values.
    # use test URL for testing
    data["action"] = settings.PAYMENT_URL_LIVE #LIVE for production
    data["productinfo"] = settings.PAID_FEE_PRODUCT_INFO
    data["key"] = settings.KEY
    data["txnid"] = txnid
    data["hash"] = hash_
    data["hash_string"] = hash_string
    data["amount"] = float(PAID_FEE_AMOUNT)
    data["firstname"] = get_user.first_name
    if get_user.email:
        data["email"] = get_user.email
    try:
        if get_user.mobile.Mobile_Number:
            data["phone"] = get_user.mobile.Mobile_Number
    except:
        print("Mobile number not present")
    data["service_provider"] = settings.SERVICE_PROVIDER
    data["furl"] = request.build_absolute_uri(reverse("tourism:payment_failure"))
    data["surl"] = request.build_absolute_uri(reverse("tourism:payment_success"))
    instance = Bookings.objects.create(user=get_user, package=get_package, is_Paid=False)
    instance.save()
    return render(request, "tourism/success.html", data)


# generate the hash
@login_required
def generate_hash(request, txnid):
    try:
        # get keys and SALT from dashboard once account is created.
        #hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_string = get_hash_string(request, txnid)
        #print(hash_string)
        generated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
        return generated_hash
    except Exception as e:
        # log the error here.
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


# create hash string using all the fields
@login_required
def get_hash_string(request, txnid):
    get_user = get_object_or_404(User, username=request.user)

    get_socialauth_user=get_user
   
    hash_string = settings.KEY + "|" + txnid + "|" + str(
        float(PAID_FEE_AMOUNT)) + "|" + settings.PAID_FEE_PRODUCT_INFO + "|"

    if get_user.email:
        hash_string += get_user.first_name + "|" + get_user.email + "|"
    else:
        hash_string += get_user.first_name + "|" + get_socialauth_user.uid + "|"

    hash_string += "||||||||||" + settings.SALT

    return hash_string


# generate a random transaction Id.
@login_required
def get_transaction_id(request):
    hash_object = hashlib.sha256(str(randint(0, 9999)).encode("utf-8"))
    # take approprite length
    txnid = hash_object.hexdigest().lower()[0:32]
    return txnid


# no csrf token require to go to Success page.
# This page displays the success/confirmation message to user indicating the completion of transaction.
@csrf_exempt
@login_required
def payment_success(request):
   return render(request, "tourism/paysuccess.html")


# no csrf token require to go to Failure page. This page displays the message and reason of failure.
@login_required
@csrf_exempt
def payment_failure(request):
    return render(request, "tourism/payfail.html")
