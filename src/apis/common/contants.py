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

ALLOWED_IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
    ".heif",
    ".raw",
    ".ico",
)
ALLOWED_FILE_TYPES = (
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/webp",
    "image/heif",
    "image/x-icon",
    "image/vnd.adobe.photoshop",
)

MERCHANT_PERMISSIONS = {
    "transactionhistory": [
        "view_transactionhistory"
    ],  # If this permission is not available, the transaction page button will not appear and the page won't be accessible.
    "invoice": [
        "view_invoice",  # If this permission is not available, the invoice section will not be visible in the customer profile.
        "change_invoice",  # If this permission is not available, the "change" button in the popup will not be visible.
        "add_invoice",  # If this permission is not available, the "add invoice" button will not be visible.
    ],
    "merchantmember": [
        "view_staff",  # If this permission is not available, the staff listing page will not be visible, nor will the button in the left panel.
        "add_staff",  # If this permission is not available, the "add staff" button will not be visible on the staff page.
        "change_staff",  # If this permission is not available, the "update staff" button will not be visible.
        "add_customers",  # If this permission is not available, the "add customer" button will not be visible.
        "change_customers",  # If this permission is not available, the "update customer" button will not be visible.
        "view_dashboard",  # If this permission is not available, the dashboard will not be visible, meaning the user will be redirected to the customers list after login.
        "view_pdf",
        "view_excel",
    ],
    "supplyrecord": [
        "add_supplyrecord",  # If this permission is not available, the "add supply record" button will not be visible.
        "view_supplyrecord",  # If this permission is not available, the option to view the supply record in the popup will not be visible.
    ],
}


STAFF_PERMISSIONS = {
    "transactionhistory": ["view_transactionhistory"],
    "invoice": ["view_invoice"],
    "merchantmember": [
        "view_customers",
    ],
    "supplyrecord": [
        "view_supplyrecord",
    ],
}
