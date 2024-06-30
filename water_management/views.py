from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import *
import razorpay
from django.http import HttpResponseBadRequest



# Create your views here.

def home(request):
    return render(request, 'homepage.html')

def adminlogin(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        login_type = data.get("loginas")

        if login_type == "admin":
            usercheck = User.objects.filter(username=username)
            if usercheck.exists():
                user = authenticate(username=username, password=password)
                if user is None:
                    messages.error(request, "Invalid Credentials.")
                    return redirect('/portal/login')
                messages.info(request, "Logged in successfully.")
                login(request, user)
                return redirect('/admin-panel')
            else:
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
                        fee_rate = FeeRate.objects.first() 
                        
                        context = {
                            'person': person,
                            'fee_rate': fee_rate,
                        }
                        return render(request, 'consumer_panel.html', context)
                    elif login_type == "pumpoperator":
                        pump_operator = PumpOperator.objects.get(operator=person)
                        records = TimeEntry.objects.filter(pump_operator=pump_operator)
                        context = {
                            'pump_operator': pump_operator,
                            'records': records
                        }
                        return render(request, 'pump_operator_panel.html', context)
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
    fee_rate = FeeRate.objects.first()  # Assuming there's only one FeeRate object
    context = {
        'fee_rate': fee_rate.fee_rate if fee_rate else 'N/A'
    }
    return render(request, 'adminsite.html', context)


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

def toggle_contractor(request, panchayat_id):
    if request.method == 'POST':
        panchayat = get_object_or_404(GramPanchayat, id=panchayat_id)
        contractor_detail = panchayat.contractor.contractor_detail
        if request.POST['action'] == 'disable':
            contractor_detail.is_enabled = False
            messages.success(request, 'Contractor disabled successfully.')
        else:
            contractor_detail.is_enabled = True
            messages.success(request, 'Contractor enabled successfully.')
        contractor_detail.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def toggle_committee_head(request, committee_id):
    if request.method == 'POST':
        committee = get_object_or_404(WaterUserCommittee, id=committee_id)
        committee_head = committee.committee_head
        if request.POST['action'] == 'disable':
            committee_head.is_enabled = False
            messages.success(request, 'Committee head disabled successfully.')
        else:
            committee_head.is_enabled = True
            messages.success(request, 'Committee head enabled successfully.')
        committee_head.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def toggle_pump_operator(request, operator_id):
    if request.method == 'POST':
        operator = get_object_or_404(Person, id=operator_id)
        if request.POST['action'] == 'disable':
            operator.is_enabled = False
            messages.success(request, 'Pump operator disabled successfully.')
        else:
            operator.is_enabled = True
            messages.success(request, 'Pump operator enabled successfully.')
        operator.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
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

@login_required(login_url="portal/login/")
def gram_panchayat_management(request):
    panchayats = GramPanchayat.objects.all()
    context = {
        'panchayats': panchayats
    }
    return render(request, 'gram_panchayat_management.html', context)

@login_required(login_url="portal/login/")
def add_panchayat(request):
    if request.method == 'POST':
        # Panchayat details
        panchayat_name = request.POST.get('panchayat_name')
        panchayat_address = request.POST.get('panchayat_address')

        # Panchayat Head details
        head_name = request.POST.get('head_name')
        head_aadhaar = request.POST.get('head_aadhaar')
        head_contact = request.POST.get('head_contact')
        head_address = request.POST.get('head_address')
        head_password = request.POST.get('head_password')
        head_photo = request.FILES.get('head_photo')

        # Contractor details
        contractor_name = request.POST.get('contractor_name')
        contractor_aadhaar = request.POST.get('contractor_aadhaar')
        contractor_contact = request.POST.get('contractor_contact')
        contractor_address = request.POST.get('contractor_address')
        contractor_password = request.POST.get('contractor_password')
        contractor_photo = request.FILES.get('contractor_photo')

        # Water User Committee details
        committee_name = request.POST.get('committee_name')
        committee_head_name = request.POST.get('committee_head_name')
        committee_head_aadhaar = request.POST.get('committee_head_aadhaar')
        committee_head_contact = request.POST.get('committee_head_contact')
        committee_head_address = request.POST.get('committee_head_address')
        committee_head_password = request.POST.get('committee_head_password')
        committee_head_photo = request.FILES.get('committee_head_photo')

        # Create Panchayat
        new_panchayat = GramPanchayat.objects.create(
            panchayat_name=panchayat_name,
            panchayat_address=panchayat_address,
        )

        # Create Panchayat Head as a Consumer
        panchayat_head = Person.objects.create(
            person_name=head_name,
            aadhaar=head_aadhaar,
            contact=head_contact,
            address=head_address,
            password=head_password,
            person_role='panchayathead',
            is_enabled=True,
            photo=head_photo,
            gram_panchayat=new_panchayat,  # Assigning the created panchayat to the head
            due_days=0,  # Default value for due days
            enable_date=timezone.now(),  # Default value for enable date
        )

        # Create Consumer role for Panchayat Head
        consumer_for_head = Person.objects.create(
            person_name=head_name,
            aadhaar=head_aadhaar,
            contact=head_contact,
            address=head_address,
            password=head_password,
            person_role='consumer',
            is_enabled=True,
            photo=head_photo,
            gram_panchayat=new_panchayat,  # Assigning the created panchayat to the consumer
            due_days=0,  # Default value for due days
            enable_date=timezone.now(),  # Default value for enable date
        )

        # Create Contractor
        contractor_person = Person.objects.create(
            person_name=contractor_name,
            aadhaar=contractor_aadhaar,
            contact=contractor_contact,
            address=contractor_address,
            password=contractor_password,
            person_role='contractor',
            is_enabled=True,
            photo=contractor_photo,
            gram_panchayat=new_panchayat,  # Assigning the created panchayat to the contractor
        )

        contractor = Contractor.objects.create(contractor_detail=contractor_person)

        # Create Water Committee Head if provided
        if committee_head_name and committee_head_aadhaar:
            committee_head = Person.objects.create(
                person_name=committee_head_name,
                aadhaar=committee_head_aadhaar,
                contact=committee_head_contact,
                address=committee_head_address,
                password=committee_head_password,
                person_role='watercommitteehead',
                is_enabled=True,
                photo=committee_head_photo,
                gram_panchayat=new_panchayat,  # Assigning the created panchayat to the committee head
            )
        else:
            committee_head = None

        # Create Water User Committee if committee_head is provided
        if committee_head:
            water_committee = WaterUserCommittee.objects.create(
                committee_name=committee_name,
                committee_head=committee_head,
                committee_panchayat=new_panchayat,
            )

        # Update Panchayat with head, contractor, and committee
        new_panchayat.panchayat_head = panchayat_head
        new_panchayat.contractor = contractor
        new_panchayat.save()

        messages.success(request, 'New Panchayat added successfully.')
        return redirect('gram_panchayat_management')

    return render(request, 'add_panchayat.html')

@login_required(login_url="portal/login/")
def assign_panchayat_head(request, panchayat_id):
    panchayat = get_object_or_404(GramPanchayat, id=panchayat_id)

    if request.method == 'POST':
        head_name = request.POST.get('head_name')
        head_aadhaar = request.POST.get('head_aadhaar')
        head_contact = request.POST.get('head_contact')
        head_address = request.POST.get('head_address')
        head_password = request.POST.get('head_password')
        head_photo = request.FILES.get('head_photo')

        # Create Panchayat Head as 'panchayathead'
        head_panchayathead = Person.objects.create(
            person_name=head_name,
            aadhaar=head_aadhaar,
            contact=head_contact,
            address=head_address,
            password=head_password,
            person_role='panchayathead',
            is_enabled=True,
            photo=head_photo,
            gram_panchayat=panchayat,
        )

        # Create Consumer role for Panchayat Head
        head_consumer = Person.objects.create(
            person_name=head_name,
            aadhaar=head_aadhaar,
            contact=head_contact,
            address=head_address,
            password=head_password,
            person_role='consumer',
            is_enabled=True,
            photo=head_photo,
            gram_panchayat=panchayat,
            due_days=0,  # Default value for due days
            enable_date=timezone.now(),  # Default value for enable date
        )

        # Update Panchayat with new head
        panchayat.panchayat_head = head_panchayathead
        panchayat.save()

        messages.success(request, 'Panchayat Head assigned successfully.')
        return redirect('gram_panchayat_management')

    context = {
        'panchayat': panchayat,
    }
    return render(request, 'assign_panchayat_head.html', context)

@login_required(login_url="portal/login/")
def assign_water_user_committee(request, panchayat_id):
    panchayat = get_object_or_404(GramPanchayat, id=panchayat_id)

    if request.method == 'POST':
        committee_name = request.POST.get('committee_name')
        head_name = request.POST.get('head_name')
        head_aadhaar = request.POST.get('head_aadhaar')
        head_contact = request.POST.get('head_contact')
        head_address = request.POST.get('head_address')
        head_password = request.POST.get('head_password')
        head_photo = request.FILES.get('head_photo')

        # Create Water User Committee Head as 'watercommitteehead'
        committee_head = Person.objects.create(
            person_name=head_name,
            aadhaar=head_aadhaar,
            contact=head_contact,
            address=head_address,
            password=head_password,
            person_role='watercommitteehead',
            is_enabled=True,
            photo=head_photo,
            gram_panchayat=panchayat,
            due_days=0,  # Default value for due days
            enable_date=timezone.now(),  # Default value for enable date
        )

        # Create Water User Committee
        water_committee = WaterUserCommittee.objects.create(
            committee_name=committee_name,
            committee_head=committee_head,
            committee_panchayat=panchayat,
        )

        messages.success(request, 'Water User Committee assigned successfully.')
        return redirect('gram_panchayat_management')

    context = {
        'panchayat': panchayat,
    }
    return render(request, 'assign_water_user_committee.html', context)

def assign_contractor(request, panchayat_id):
    panchayat = get_object_or_404(GramPanchayat, id=panchayat_id)

    if request.method == 'POST':
        # Get form data
        contractor_name = request.POST.get('contractor_name')
        contractor_aadhaar = request.POST.get('contractor_aadhaar')
        contractor_contact = request.POST.get('contractor_contact')
        contractor_address = request.POST.get('contractor_address')
        contractor_password = request.POST.get('contractor_password')
        contractor_photo = request.FILES.get('contractor_photo')

        if contractor_name and contractor_password:
            # Create a new Person instance (contractor)
            contractor_person = Person.objects.create(
                person_name=contractor_name,
                aadhaar=contractor_aadhaar,
                contact=contractor_contact,
                address=contractor_address,
                password=contractor_password,
                person_role='contractor',
                is_enabled=True,
                photo=contractor_photo,
                gram_panchayat=panchayat  # Assigning the created panchayat to the contractor
            )

            # Create a Contractor instance and associate with the GramPanchayat
            contractor_instance = Contractor.objects.create(contractor_detail=contractor_person)
            panchayat.contractor = contractor_instance
            panchayat.save()

            messages.success(request, 'Contractor assigned successfully.')
            return redirect('gram_panchayat_management')

        else:
            messages.error(request, 'Please provide contractor name and password.')

    context = {
        'panchayat': panchayat,
    }
    return render(request, 'assign_contractor.html', context)

@login_required(login_url="portal/login/")
def view_consumers(request):
    consumers = Person.objects.filter(person_role='consumer').order_by('gram_panchayat__panchayat_name')
    return render(request, 'view_consumers.html', {'consumers': consumers})

def assign_pump_operator(request, panchayat_id):
    panchayat = get_object_or_404(GramPanchayat, id=panchayat_id)
    water_committee = WaterUserCommittee.objects.filter(committee_panchayat=panchayat).first()

    if request.method == 'POST':
        operator_name = request.POST.get('operator_name')
        operator_aadhaar = request.POST.get('operator_aadhaar')
        operator_contact = request.POST.get('operator_contact')
        operator_address = request.POST.get('operator_address')
        operator_password = request.POST.get('operator_password')
        operator_photo = request.FILES.get('operator_photo')

        # Create a new Person object for the Pump Operator
        operator_person = Person.objects.create(
            person_name=operator_name,
            aadhaar=operator_aadhaar,
            contact=operator_contact,
            address=operator_address,
            password=operator_password,
            person_role='pumpoperator',
            is_enabled=True,
            photo=operator_photo,
        )

        # Create a new PumpOperator object
        pump_operator = PumpOperator.objects.create(
            operator=operator_person,
            water_user_committee=water_committee,
        )

        return redirect('gram_panchayat_management')  # Redirect to your main page after creation

    context = {
        'panchayat': panchayat,
    }
    return render(request, 'assign_pump_operator.html', context)

def mark_attendance(request):
    if request.method == "POST":
        operator_id = request.POST.get("operator_id")
        in_time = request.POST.get("in_time")
        out_time = request.POST.get("out_time")
        
        # Handle supply_enabled checkbox correctly
        supply_enabled = request.POST.get("supply_enabled") == 'on'

        pump_operator = PumpOperator.objects.get(id=operator_id)

        # Create a new TimeEntry for the pump operator
        time_entry = TimeEntry.objects.create(
            pump_operator=pump_operator,
            in_time=in_time,
            out_time=out_time,
            supply_enabled=supply_enabled  # Save supply_enabled in TimeEntry
        )

        pump_operator.working_days += 1
        pump_operator.save()
        
        # Update due days for consumers if supply_enabled is True
        if supply_enabled:
            consumers = Person.objects.filter(gram_panchayat=pump_operator.water_user_committee.committee_panchayat, person_role='consumer')
            for consumer in consumers:
                consumer.due_days += 1
                consumer.save()

        messages.info(request, "Attendance marked successfully.")
        records = TimeEntry.objects.filter(pump_operator=pump_operator)
        context = {
            'pump_operator': pump_operator,
            'records': records
        }
        return render(request, 'pump_operator_panel.html', context)

    return render(request, 'pump_operator_panel.html')

def manage_water_committees(request):
    committees = WaterUserCommittee.objects.all()

    context = {
        'committees': committees,
    }
    return render(request, 'manage_water_committees.html', context)

from django.conf import settings    
def pay_bill(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    fee_rate = FeeRate.objects.first()
    total_bill = person.due_days * fee_rate.fee_rate * 100  # Convert to paise

    minimum_amount = 100  # Minimum amount in paise (equivalent to 1 INR)

    if total_bill < minimum_amount:
        return HttpResponseBadRequest("Order amount less than minimum amount allowed")

    payment = None
    if request.method == 'POST':
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            'amount': total_bill,
            'currency': 'INR',
            'payment_capture': '1'
        })

        if 'razorpay_payment_id' in request.POST and 'razorpay_signature' in request.POST:
            payment_id = request.POST['razorpay_payment_id']
            payment_signature = request.POST['razorpay_signature']

            # Save the payment details
            Payment.objects.create(
                person=person,
                payment_id=payment_id,
                payment_signature=payment_signature,
                amount=total_bill / 100  # Convert back to INR
            )

            # Reset due days after payment
            person.due_days = 0
            person.save()

            messages.success(request, f'Bill of amount {total_bill / 100} has been paid successfully.')

    context = {
        'person': person,
        'fee_rate': fee_rate,
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'total_bill': total_bill
    }
    return render(request, 'consumer_panel.html', context)