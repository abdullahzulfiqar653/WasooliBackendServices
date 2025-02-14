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

    def get_form(self, request, obj=None, **kwargs):
        """
        Ensure fields are only pre-filled when editing an existing merchant.
        New merchant creation should have empty fields.
        """
        form = super().get_form(request, obj, **kwargs)

        if obj and obj.pk:
            if obj.owner:
                form.base_fields["primary_phone"].initial = obj.owner.username or ""
                form.base_fields["email"].initial = obj.owner.email or ""
                form.base_fields["first_name"].initial = obj.owner.first_name or ""
                form.base_fields["last_name"].initial = obj.owner.last_name or ""

            member = MerchantMember.objects.filter(merchant=obj).first()
            if member:
                form.base_fields["cnic"].initial = member.cnic or ""
            if obj.city:
                form.base_fields["city"].initial = obj.city or ""

        else:
            form.base_fields["primary_phone"].initial = ""
            form.base_fields["email"].initial = ""
            form.base_fields["first_name"].initial = ""
            form.base_fields["last_name"].initial = ""
            form.base_fields["cnic"].initial = ""

        return form

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("owner__profile__otp")
        queryset = queryset.annotate(member_count=Count("members"))
        return queryset

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to update an existing user
        or create a new one, and ensure all related records are updated instead of creating duplicates.
        """
        primary_phone = form.cleaned_data.get("primary_phone")
        email = form.cleaned_data.get("email", None)
        cnic = form.cleaned_data.get("cnic")
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")

        user = obj.owner if hasattr(obj, "owner") else None

        if user:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        else:
            user = User.objects.create_user(
                username=primary_phone,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=secrets.token_hex(7),
            )

        obj.owner = user
        obj.save()

        super().save_model(request, obj, form, change)
        merchant_group, _ = Group.objects.get_or_create(name=RoleChoices.MERCHANT)
        user.groups.add(merchant_group)
        member = MerchantMember.objects.filter(user=user, merchant=obj).first()
        if member:
            member.primary_phone = primary_phone
            member.cnic = cnic
            member.save()
        else:
            member = MerchantMember.objects.create(
                user=user, merchant=obj, primary_phone=primary_phone, cnic=cnic
            )
        otp_record, _ = OTP.objects.get_or_create(member=member)
        otp_record.generate_otp()
        if not MemberRole.objects.filter(
            member=member, role=RoleChoices.MERCHANT
        ).exists():

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
