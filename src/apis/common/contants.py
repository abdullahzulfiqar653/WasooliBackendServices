MODEL_CODES = {
    "OTP": "108",
    "Lookup": "100",
    "Invoice": "101",
    "Merchant": "102",
    "MemberRole": "103",
    "SupplyRecord": "104",
    "MerchantMember": "105",
    "TransactionHistory": "106",
    "MerchantMembership": "107",
}


MERCHANT_PERMISSIONS = {
    "transactionhistory": ["view_transactionhistory"],
    "invoice": ["add_invoice", "change_invoice", "view_invoice"],
    "merchantmember": [
        "add_merchantmember",
        "view_merchantmember",
        "change_merchantmember",
        "delete_merchantmember",
    ],
    # "merchantmembership": [
    #     "add_merchantmembership",
    #     "change_merchantmembership",
    #     "view_merchantmembership",
    #     "delete_merchantmembership",
    # ],
    "supplyrecord": [
        "add_supplyrecord",
        "view_supplyrecord",
        "change_supplyrecord",
        "delete_supplyrecord",
    ],
}

STAFF_PERMISSIONS = {
    "transactionhistory": ["view_transactionhistory"],
    "invoice": ["add_invoice", "change_invoice", "view_invoice"],
    "merchantmember": [
        "add_merchantmember",
        "view_merchantmember",
        "change_merchantmember",
    ],
    # "merchantmembership": [
    #     "add_merchantmembership",
    #     "change_merchantmembership",
    #     "view_merchantmembership",
    # ],
    "supplyrecord": [
        "add_supplyrecord",
        "view_supplyrecord",
        "change_supplyrecord",
    ],
}
