from auditlog.registry import auditlog
from apis.models.otp import OTP
from apis.models.lookup import Lookup
from apis.models.invoice import Invoice
from apis.models.merchant import Merchant
from apis.models.member_role import MemberRole
from apis.models.supply_record import SupplyRecord
from apis.models.merchant_member import MerchantMember
from apis.models.merchant_membership import MerchantMembership
from apis.models.transaction_history import TransactionHistory


__all__ = [
    "OTP",
    "Lookup",
    "Invoice",
    "Merchant",
    "MemberRole",
    "SupplyRecord",
    "MerchantMember",
    "MerchantMembership",
    "TransactionHistory",
]

auditlog.register(OTP)
auditlog.register(Lookup)
auditlog.register(Invoice)
auditlog.register(Merchant)
auditlog.register(MemberRole)
auditlog.register(SupplyRecord)
auditlog.register(MerchantMember)
auditlog.register(MerchantMembership)
auditlog.register(TransactionHistory)
