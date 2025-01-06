from django import forms
from django.contrib import admin
from .models import Merchant


class CommissionStructureForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = "__all__"

    # For simplicity, we handle commission_structure as a JSON field manually
    cash_commission_1 = forms.DecimalField(
        label="Commission for Cash (Tier 1)", required=False, min_value=0
    )
    cash_commission_2 = forms.DecimalField(
        label="Commission for Cash (Tier 2)", required=False, min_value=0
    )
    cash_commission_3 = forms.DecimalField(
        label="Commission for Cash (Tier 3)", required=False, min_value=0
    )
    online_commission_1 = forms.DecimalField(
        label="Commission for Online (Tier 1)", required=False, min_value=0
    )
    online_commission_2 = forms.DecimalField(
        label="Commission for Online (Tier 2)", required=False, min_value=0
    )
    online_commission_3 = forms.DecimalField(
        label="Commission for Online (Tier 3)", required=False, min_value=0
    )

    def __init__(self, *args, **kwargs):
        super(CommissionStructureForm, self).__init__(*args, **kwargs)

        # If the merchant already has a commission structure, populate the form fields with the data
        if self.instance.pk:
            commission_structure = self.instance.commission_structure
            if "cash" in commission_structure:
                self.fields["cash_commission_1"].initial = commission_structure["cash"][
                    0
                ].get("commission", 0)
                self.fields["cash_commission_2"].initial = commission_structure["cash"][
                    1
                ].get("commission", 0)
                self.fields["cash_commission_3"].initial = commission_structure["cash"][
                    2
                ].get("commission", 0)
            if "online" in commission_structure:
                self.fields["online_commission_1"].initial = commission_structure[
                    "online"
                ][0].get("commission", 0)
                self.fields["online_commission_2"].initial = commission_structure[
                    "online"
                ][1].get("commission", 0)
                self.fields["online_commission_3"].initial = commission_structure[
                    "online"
                ][2].get("commission", 0)

    def save(self, commit=True):
        # Modify the saved instance based on form inputs
        if self.is_valid():
            data = {
                "cash": [
                    {
                        "max_credit": 1000,
                        "commission": self.cleaned_data["cash_commission_1"],
                    },
                    {
                        "max_credit": 3000,
                        "commission": self.cleaned_data["cash_commission_2"],
                    },
                    {
                        "max_credit": 5000,
                        "commission": self.cleaned_data["cash_commission_3"],
                    },
                ],
                "online": [
                    {
                        "max_credit": 1000,
                        "commission": self.cleaned_data["online_commission_1"],
                    },
                    {
                        "max_credit": 3000,
                        "commission": self.cleaned_data["online_commission_2"],
                    },
                    {
                        "max_credit": 5000,
                        "commission": self.cleaned_data["online_commission_3"],
                    },
                ],
            }
            self.instance.commission_structure = data
            return super().save(commit)
        return super().save(commit)
