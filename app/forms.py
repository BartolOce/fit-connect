from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import Job, UserProfile, TopUp, Bid
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Last name'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Confirm password'}))
    is_trainer = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'form-check-input', }), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_trainer']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            self.add_error(None, "This username is already taken.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            self.add_error(None, "This email address is already taken.")
        return email





class JobForm(forms.ModelForm):
    title = forms.ChoiceField(choices=Job.Title.choices, widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'What kind of job is it?'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Put a description'}))
    budget = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder': 'Your budget'}))
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Starting time', 'type': 'datetime-local'}), 
                                     input_formats=['%Y-%m-%dT%H:%M'])

    class Meta:
        model = Job
        fields = ['title', 'description', 'budget', 'start_time']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        if start_time and start_time <= timezone.now():
            self.add_error(field=None, error='Start time must be in the future.')

        return cleaned_data




class BidForm(forms.ModelForm):
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your budget'}))

    class Meta:
        model = Bid
        fields = ['price']

    def __init__(self, *args, **kwargs):
        self.budget = kwargs.pop('budget', None)  # Extract budget from kwargs
        self.start_time = kwargs.pop('start_time', None)  # Extract start_time from kwargs
        self.trainer_profile = kwargs.pop('trainer_profile', None)  # Extract trainer_profile from kwargs
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')

        job_start_time = self.job.start_time

        # Define the range of ±2 hours
        start_range = job_start_time - timedelta(hours=2)
        end_range = job_start_time + timedelta(hours=2)

        # Get all Bid instances within the specified range
        matching_bids = Bid.objects.filter(job__start_time__range=(start_range, end_range),bidder=self.trainer_profile)

        if matching_bids.exists():
            raise ValidationError("You already bidded on job in similar time frame")
        if self.budget is not None and price > self.budget:
            raise ValidationError("Bid price exceeds job budget.")
        return cleaned_data




#ispit
class TopUpForm(forms.ModelForm):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your TopUp code'}),
        label='Code',
        validators=[RegexValidator(regex=r'^\d{12}$', message='Code must be exactly 12 digits')]
    )

    class Meta:
        model = TopUp
        fields = ['code']

    def clean_code(self):
        code = self.cleaned_data['code']
        topup_instance = TopUp.objects.filter(code=code).first()  # Get the first instance or None if not found

        if topup_instance is None:
            raise ValidationError("No such code")

        if topup_instance.is_used:
            raise ValidationError("It's already used")

        if topup_instance.expiration_date < timezone.now().date():
            raise ValidationError("Code expired")

        return code
