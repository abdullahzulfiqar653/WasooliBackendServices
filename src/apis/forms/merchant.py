from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apis.models.merchant_member import MerchantMember


class MerchantAdminForm(forms.ModelForm):
    primary_phone = forms.CharField(max_length=10, required=True, label="Primary Phone")
    email = forms.EmailField(max_length=255, required=False, label="Primary Email")
    first_name = forms.CharField(
        max_length=10, required=True, label="Merchant First Name"
    )
    last_name = forms.CharField(
        max_length=10, required=False, label="Merchant Last Name"
    )
    cnic = forms.CharField(max_length=13, required=True, label="National ID card")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # If email is provided, it should be valid
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered in the system.")

        return email

    def clean_primary_phone(self):
        primary_phone = self.cleaned_data.get("primary_phone")

        # Check if phone number is 10 digits long
        if len(primary_phone) != 10:
            raise ValidationError("Phone number must be exactly 10 digits long.")

        # Check if phone number starts with '3'
        if not primary_phone.startswith("3"):
            raise ValidationError("Phone number must start with '3'.")

        # Check if phone number already exists in MerchantMember model
        if MerchantMember.objects.filter(primary_phone=primary_phone).exists():
            raise ValidationError("This phone number is already in use.")

        return primary_phone
