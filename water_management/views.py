from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from .models import *

# Create your views here.

def home(request):
    return render(request, 'homepage.html')

def adminlogin(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        login_type = data.get("loginas")

        # First, check if user exists
        if login_type == "admin":
            usercheck = User.objects.filter(username=username)
            if usercheck.exists():
                user = authenticate(username=username, password=password)  # check password and return User or none
                if user is None:
                    messages.error(request, "Invalid Credentials.")
                    return redirect('/portal/login')
                
                # User exists, log in and redirect
                messages.info(request, "Logged in successfully.")
                login(request, user)
                return redirect('/admin-panel')  # Redirect to admin panel after login
            
            else:
                # User doesn't exist
                messages.error(request, "Invalid username.")
                return redirect('/portal/login')
        
        else:
            person = Person.objects.filter(person_name=username, person_role=login_type).first()
            if person:
                if person.is_enabled and check_password(password, person.password):
                    messages.info(request, "Logged in successfully.")
                    if login_type == "panchayathead":
                        panchayat = person.gram_panchayat
                        consumers = panchayat.residents.filter(person_role='consumer')
                        context = {
                            'person': person,
                            'consumers': consumers,
                            'panchayat': panchayat
                        }
                        return render(request, 'panchayatheadpage.html', context)
                    elif login_type == "consumer":
                        context = {'person': person}
                        return render(request, 'consumer_panel.html', context)
                elif not person.is_enabled:
                    messages.error(request, "User is disabled. Please contact the administrator.")
                    return redirect('/portal/login')
                else:
                    messages.error(request, "Invalid credentials.")
                    return redirect('/portal/login')
            else:
                messages.error(request, "Invalid username or role.")
                return redirect('/portal/login')

    return render(request, 'userlogin.html')

def logoutuser(request):
    logout(request)
    return redirect('/portal/login')

@login_required(login_url="portal/login/")
def adminpage(request):
    return render(request, 'adminsite.html')


@login_required
def panchayatheadpage(request, panchayat_name):
    panchayat = get_object_or_404(GramPanchayat, panchayat_name=panchayat_name)
    consumers = panchayat.residents.filter(person_role='consumer')

    if request.method == "POST":
        person_name = request.POST.get("person_name")
        aadhaar = request.POST.get("aadhaar")
        contact = request.POST.get("contact")
        address = request.POST.get("address")
        photo = request.FILES.get("photo")
        password = request.POST.get("password")


        new_consumer = Person(
            person_name=person_name,
            aadhaar=aadhaar,
            contact=contact,
            address=address,
            photo=photo,
            person_role='consumer',
            password=password,
            gram_panchayat=panchayat
        )
        new_consumer.save()

        messages.success(request, "Consumer added successfully.")
        return redirect('panchayatheadpage', panchayat_name=panchayat_name)

    context = {
        'panchayat': panchayat,
        'consumers': consumers
    }
    return render(request, 'panchayatheadpage.html', context)

@login_required(login_url="portal/login/")
def toggle_consumer_status(request, consumer_id):
    consumer = get_object_or_404(Person, id=consumer_id)
    consumer.is_enabled = not consumer.is_enabled
    consumer.save()
    messages.success(request, f"Consumer { 'enabled' if consumer.is_enabled else 'disabled' } successfully.")
    return redirect('panchayatheadpage', panchayat_name=consumer.gram_panchayat.panchayat_name)

@csrf_exempt
def update_water_fee_rate(request):
    if request.method == 'POST':
        fee_rate = request.POST.get('fee_rate')
        if fee_rate:
            fee_rate, created = FeeRate.objects.update_or_create(
                id=1,
                defaults={'fee_rate': fee_rate}
            )
            return redirect('/admin-panel')  # Redirect to the admin panel or another appropriate view
    return HttpResponse(status=400)  # Bad request if something goes wrong

@login_required(login_url="portal/login/")
def panchayatheadmgmt(request):
    panchayats = GramPanchayat.objects.all()

    context = {
        'panchayats': panchayats
    }
    return render(request, 'panchayatheadmgmtpage.html', context)


@login_required(login_url="portal/login/")
def toggle_panchayat_head_status(request, head_id):
    head = get_object_or_404(Person, id=head_id, person_role='panchayathead')
    head.is_enabled = not head.is_enabled
    head.save()

    action = 'enabled' if head.is_enabled else 'disabled'
    messages.success(request, f"Panchayat Head {head.person_name} {action} successfully.")

    return redirect('panchayatheadmgmt')

@login_required(login_url="portal/login/")
def update_panchayat_head(request, panchayat_id):
    panchayat = get_object_or_404(GramPanchayat, id=panchayat_id)
    
    if request.method == 'POST':
        new_head_id = request.POST.get('new_head')
        new_password = request.POST.get('new_password')

        if new_head_id and new_password:
            new_head = get_object_or_404(Person, id=new_head_id)
            
            # Deactivate and delete current panchayat head if there is one
            if panchayat.panchayat_head:
                old_head = panchayat.panchayat_head
                old_head.is_enabled = False  # Deactivate old head
                old_head.save()
            
            # Create a new Panchayat head role for the selected person
            new_head_role = Person(
                person_name=new_head.person_name,
                photo=new_head.photo,
                aadhaar=new_head.aadhaar,
                contact=new_head.contact,
                address=new_head.address,
                gram_panchayat=panchayat,
                person_role='panchayathead',
                is_enabled=True,
                password=new_password
            )
            new_head_role.save()
            
            # Update the Panchayat's head reference
            panchayat.panchayat_head = new_head_role
            panchayat.save()
            
            messages.success(request, 'Panchayat head updated successfully.')
        else:
            messages.error(request, 'Please select a new head and provide a new password.')

        return redirect('panchayatheadmgmt')
    
    context = {
        'panchayat': panchayat
    }
    return render(request, 'update_panchayat_head.html', context)