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
        queryset = queryset.annotate(member_count=Count("members"))
        return queryset

    def save_model(self, request, obj, form, change):
        """
        Jab Merchant save hoga toh phone number bhi save karenge MerchantMember ke andar.
        """
        primary_phone = form.cleaned_data.get("primary_phone")
        email = form.cleaned_data.get("email", None)

        user = User.objects.create_user(username=primary_phone, email=email)
        user.set_password(secrets.token_hex(7))
        obj.owner = user  # Attach the created user to the Merchant object
        obj.save()  # Save the Merchant object

        super().save_model(request, obj, form, change)

        obj.owner.groups.add(Group.objects.get(name=RoleChoices.MERCHANT))
        member = MerchantMember.objects.create(
            user=user, merchant=obj, primary_phone=primary_phone
        )
        otp_record, _ = OTP.objects.get_or_create(member=member)
        otp_record.generate_otp()
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
