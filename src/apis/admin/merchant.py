import secrets
from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from apis.models.otp import OTP
from apis.models.lookup import Lookup
from apis.models.merchant import Merchant
from apis.forms.merchant import MerchantAdminForm
from apis.models.merchant_member import MerchantMember
from apis.models.member_role import RoleChoices, MemberRole

admin.site.register(Lookup)


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    form = MerchantAdminForm
    list_display = (
        "id",
        "otp",
        "name",
        "type",
        "code",
        "merchant_count",
        "owner_first_name",
    )
    exclude = ("owner",)
    ordering = ("name",)
    list_filter = ("type",)
    search_fields = ("name", "owner__first_name", "code")

    def get_queryset(self, request):
        # Annotate the queryset to include the count of related members
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("owner__profile__otp")
        queryset = queryset.annotate(member_count=Count("members"))
        return queryset

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to create a user, assign them to a merchant,
        and handle related processes after saving the Merchant object.
        """
        # Get the primary phone and email from the custom form data
        primary_phone = form.cleaned_data.get("primary_phone")
        email = form.cleaned_data.get("email", None)

        # Create a new user with the primary phone as the username and email
        user = User.objects.create_user(username=primary_phone, email=email)

        # Set a random password for the new user
        user.set_password(secrets.token_hex(7))

        # Assign the created user to the merchant as the owner
        obj.owner = user

        # Save the Merchant object with the new user as owner
        obj.save()

        # Call the parent save_model method to handle standard save operations
        super().save_model(request, obj, form, change)

        # Add the user to the "Merchant" group
        obj.owner.groups.add(Group.objects.get(name=RoleChoices.MERCHANT))

        # Create a MerchantMember instance linking the user and merchant
        member = MerchantMember.objects.create(
            user=user, merchant=obj, primary_phone=primary_phone
        )

        # Create an OTP record for the member and generate the OTP
        otp_record, _ = OTP.objects.get_or_create(member=member)
        otp_record.generate_otp()

        # Assign the "MERCHANT" role to the newly created member
        MemberRole.objects.create(member=member, role=RoleChoices.MERCHANT)

    def owner_first_name(self, obj):
        return obj.owner.first_name

    def otp(self, obj):
        return obj.owner.profile.otp.code

    owner_first_name.admin_order_field = "owner__first_name"
    owner_first_name.short_description = "Owner First Name"

    def merchant_count(self, obj):
        return obj.member_count

    merchant_count.short_description = "Number of Members"
