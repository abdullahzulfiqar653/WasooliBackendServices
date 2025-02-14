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

        if email and User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered in the system.")

        return email

    def clean_primary_phone(self):
        primary_phone = self.cleaned_data.get("primary_phone")
        if len(primary_phone) != 10:
            raise ValidationError("Phone number must be exactly 10 digits long.")
        if not primary_phone.startswith("3"):
            raise ValidationError("Phone number must start with '3'.")

        if self.instance.pk:
            existing_member = MerchantMember.objects.filter(primary_phone=primary_phone).exclude(user=self.instance.owner).exists()
        else:  
            existing_member = MerchantMember.objects.filter(primary_phone=primary_phone).exists()

        if existing_member:
            raise ValidationError("This phone number is already in use.")

        return primary_phone
    

    