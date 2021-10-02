from core.models import Item
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import fields
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
class SignUpForm(UserCreationForm):
    email=forms.EmailField(max_length=250)
    first_name=forms.CharField(max_length=150)
    last_name=forms.CharField(max_length=150)

    class Meta:
        model=User
        fields=('email','first_name','last_name','password1','password2')
    def clean_email(self):
        email=self.cleaned_data['email'].lower()
        if User.objects.filter(email=email):
            raise ValidationError("This email address already exixts.")
        return email
class BasicUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=('first_name','last_name') 
class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '1234 Main St'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment or suite'
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False) 
class ItemForm(forms.ModelForm):
    class Meta:
        model=Item
        fields=('item_name','price','discount_price','category','label','description','photo','sellercom')
