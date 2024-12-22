from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic
from .forms import RegistrationForm, JobForm, BidForm, TopUpForm
from django.views.generic import View, FormView
from django.shortcuts import get_object_or_404, redirect
from .models import TrainerProfile, UserProfile
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from .models import Job, Bid, TopUp, Dispute
from django.forms import ValidationError
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q

def dispute_job(request):
    if request.method == 'POST':
        bidder_id = request.POST.get('bidder_id')
        reason = request.POST.get('reason')

        try:
            bid = Bid.objects.get(id=bidder_id)
        except Bid.DoesNotExist:
            messages.error(request, 'Bid does not exist.')
            return redirect('jobs')

        existing_dispute = Dispute.objects.filter(bid=bid).first()
        if existing_dispute:
            messages.error(request, 'A dispute for this bid already exists.')
            return redirect('jobs')

        user_profile = request.user.userprofile   
        dispute = Dispute(bid=bid, reason=reason, user=user_profile)
        try:
            dispute.save()
            messages.success(request, 'Dispute opened successfully.')

            bid.disputed = True
            bid.save()

        except Exception as e:
            messages.error(request, f'Error occurred while opening dispute: {str(e)}')

        return redirect('jobs')

    else:
        return HttpResponse('Method not allowed', status=405)


def home(request):
    # Count of all TopUp instances
    total_topups_count = TopUp.objects.all().count()
    
    # Count of used TopUp instances
    topups_used_count = TopUp.objects.filter(is_used=True).count()
    
    return render(request, 'app/home.html', {'total_topups_count': total_topups_count, 'topups_used_count': topups_used_count})

def profile(request):
    return render(request, 'app/profile.html')

def jobs(request):
    if request.method == 'POST':
        if 'accept_bid' in request.POST:
            bid_id = request.POST.get('bid_id')
            bid = get_object_or_404(Bid, pk=bid_id) 

            bid.job.status = 'ACCEPTED'  # Corrected status value
            bid.job.save()  # Save the bid's associated job

            other_bids = Bid.objects.filter(job=bid.job).exclude(id=bid.id)
            other_bids.update(declined=True)

            bid.accepted = True
            bid.save()
        elif 'rate_job' in request.POST:
            input_value = Decimal(request.POST.get('rating'))  # Convert input value to Decimal
            bid_id_rating = request.POST.get('bidder_id')
            bid_rating = get_object_or_404(Bid, pk=bid_id_rating) 

            bidder = bid_rating.bidder
            if bidder:
                if bidder.rating == 0:
                    bidder.rating = input_value
                else:
                    # Calculate new rating as an average
                    bidder.rating = (bidder.rating*bidder.number_of_jobs + input_value) / Decimal(bidder.number_of_jobs+1)

                bidder.number_of_jobs += 1
                bidder.balance += bid_rating.price
                bidder.save()

                bid_rating.completed = True
                bid_rating.save()

    user_profile = UserProfile.objects.get(user=request.user)
    jobs = Job.objects.filter(user=user_profile).order_by('start_time')
    bids = Bid.objects.filter(job__user=user_profile).order_by('-job__start_time')
    accepted_completed_bids = Bid.objects.filter(
        Q(job__user=user_profile, accepted=True, completed=True) | 
        Q(job__user=user_profile, accepted=True, disputed=True)
    ).count()
    any_job_is_published = any(job.status=='published' for job in jobs)
    for job in jobs:
        job.has_bid = job.bid_set.filter(job=job).exists()
    has_accepted_bid = False
    for bid in bids:
        if bid.accepted == True and bid.completed == False and bid.disputed == False:
            has_accepted_bid = True

    context = {'jobs': jobs, 'bids': bids, 'accepted_completed_bids': accepted_completed_bids, 'any_job_is_published': any_job_is_published, 'has_accepted_bid':has_accepted_bid}
    return render(request, 'app/jobs.html', context)


def all_jobs(request):
    jobs = Job.objects.all().order_by('start_time')  # Define jobs variable outside the conditional statement
    bids = Bid.objects.all().order_by('-job__start_time')
    current_user = request.user
    accepted_completed_bids = Bid.objects.filter(bidder__user__id=current_user.id).count()
    for job in jobs:
        job.has_bid = job.bid_set.filter(bidder=request.user.trainerprofile).exists()
    any_job_has_bid = any(not job.has_bid for job in jobs)
    
    if request.method == 'POST':
        # If it's a POST request, handle the form submission
        job_id = request.POST.get('job_id')
        job = get_object_or_404(Job, pk=job_id)
        form = BidForm(request.POST, budget=job.budget, start_time=job.start_time, trainer_profile=request.user.trainerprofile, job=job)

        if form.is_valid():
            price = form.cleaned_data['price']

            new_bid = Bid(bidder=request.user.trainerprofile, job=job, price=price)
            new_bid.save()

            # Redirect to jobs_trainer URL upon successful form submission
            return HttpResponseRedirect(reverse('jobs_trainer'))
        else:
            form_without_data = BidForm()
            context = {'jobs': jobs, 'bids': bids, 'form': form, 'job_id': job_id, 'form_without_data': form_without_data, 'accepted_completed_bids': accepted_completed_bids, 'any_job_has_bid':any_job_has_bid}
        
    else:
        form_without_data = BidForm()
        context = {'jobs': jobs, 'bids': bids, 'form_without_data': form_without_data, 'accepted_completed_bids': accepted_completed_bids, 'any_job_has_bid':any_job_has_bid}

    if 'form' in context and isinstance(context['form'], BidForm):
        errors = context['form'].errors.as_data()
        error_messages = [field_error.message for field_errors in errors.values() for field_error in field_errors]
        context['error_messages'] = error_messages

    return render(request, 'app/jobs_trainer.html', context)


def RegisterView(request):
    context = {}
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']
            user.set_password(raw_password)                
            user.save()
            # Create user profile
            is_trainer = form.cleaned_data['is_trainer']
            if is_trainer:
                TrainerProfile.objects.create(user=user, name=username)
            else:
                UserProfile.objects.create(user=user, name=username)
            # Authenticate and login user
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            if not form.errors:
                form.add_error(field=None, error='Passwords do not match.')
    else:
        form = RegistrationForm()
    
    context['form'] = form
    return render(request, 'registration/register.html', context)


def post_job(request):
    context = {}
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            account = get_object_or_404(UserProfile, user=request.user)
            budget = form.cleaned_data['budget']
            if account.balance is not None and account.balance >= budget:
                saved_job = form.save(commit=False)
                saved_job.user = account
                saved_job.save()
                account.balance -= budget
                account.save()
                return HttpResponseRedirect(reverse('home'))
            else:
                form.add_error(field=None, error='Not enough tokens on your balance.')
    else:
        form = JobForm(request=request)
    
    context['form'] = form
    return render(request, 'app/post_job.html', context)
    

def decline_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    job.status = Job.Status.DECLINED
    job.save()
    
    return HttpResponseRedirect(reverse('jobs_trainer'))
# Create your views here.


def top_up(request):
    context = {}
    
    if request.method == 'POST':
        form = TopUpForm(request.POST)
        if form.is_valid():
            ValidationError("isValid")
            # Get the logged-in user's profile
            if hasattr(request.user, 'userprofile'):
                profile = request.user.userprofile
            elif hasattr(request.user, 'trainerprofile'):
                profile = request.user.trainerprofile
            else:
                # Handle the case where user doesn't have any profile
                return redirect('home')  # Redirect to an error page or handle it appropriately

            code=form.cleaned_data.get('code')

            topup_instance = TopUp.objects.filter(code=code).first()
            topup_amount = topup_instance.amount

            profile.balance += topup_amount
            profile.save()

            topup_instance.is_used=True
            topup_instance.user=profile
            topup_instance.used_date=timezone.now().date()
            topup_instance.save()

            # Save the topup record

            return redirect('home')

    else:
        form = TopUpForm()
    
    context['form'] = form

    # Handling ValidationError messages
    if 'form' in context:
        if isinstance(context['form'], TopUpForm):
            errors = context['form'].errors.as_data()
            error_messages = []
            for field, field_errors in errors.items():
                for field_error in field_errors:
                    error_messages.append(field_error.message)
            context['error_messages'] = error_messages

    return render(request, 'app/top_up.html', context)


def all_top_ups(request):
    top_ups = TopUp.objects.all().order_by('-used_date')
    return render(request, 'app/top_up_list.html', {'top_ups': top_ups})


def admin_top_up(request):
    # Count of all TopUp instances
    total_topups_count = TopUp.objects.all().count()
    
    # Count of used TopUp instances
    topups_used_count = TopUp.objects.filter(is_used=True).count()
    
    # Retrieve used TopUp instances
    used_topups = TopUp.objects.filter(is_used=True)

    # Retrieve unused TopUp instances
    unused_topups = TopUp.objects.filter(is_used=False)

    return render(request, 'app/admin_top_up.html', {'used_topups': used_topups, 'unused_topups': unused_topups, 'total_topups_count': total_topups_count, 'topups_used_count': topups_used_count})

