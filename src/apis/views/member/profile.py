from rest_framework import generics
from rest_framework.response import Response

from apis.utils import get_customer_stats
from apis.permissions import IsMerchantOrStaff
from apis.serializers.member_profile import MemberProfileSerializer

from drf_spectacular.utils import extend_schema


class MemberProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
    This endpoint provides all the information for members profile cards.
    """

    permission_classes = [IsMerchantOrStaff]
    serializer_class = MemberProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        membership = request.membership
        response = get_customer_stats(membership)
        return Response(response)

    @extend_schema(
        description="""
        ### Retrieves a member's profile information:

        This view returns the profile information for the member associated with the authenticated merchant or staff user.
        The response includes detailed profile information, such as customer stats and other related data.

        **The response will include the following fields:**
        - `member_id`: Unique identifier for the member.
        - `name`: The full name of the member.
        - `email`: The email address of the member.
        - `phone_number`: The contact number of the member.
        - `total_orders`: Total number of orders made by the member.
        - `total_spent`: Total amount spent by the member.
        - `recent_activity`: Recent activity or interactions by the member.
        - `membership_status`: Current membership status of the member.

        **Response Example:**
        ```json
        {
            "member_id": "12345",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "total_orders": 50,
            "total_spent": 5000.00,
            "recent_activity": "Placed an order on 2025-02-15.",
            "membership_status": "Active"
        }
        ```

        **Authentication:**
        This view requires the user to be authenticated as either a merchant or staff member associated with the member whose profile is being requested.
        """,
        responses={
            200: MemberProfileSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
