import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerContact:
    """Contact details for a customer, owned by the User Service."""

    customer_id: uuid.UUID
    name: str
    email: str
    phone_number: str


class UserServiceClient:
    """Client for the User Service.

    Stub implementation: returns placeholder contact details so notification
    messages can be composed without a live User Service. Replace
    :meth:`get_contact` with a real ``GET /users/{id}`` call when available.
    """

    def get_contact(self, customer_id: uuid.UUID) -> CustomerContact:
        return CustomerContact(
            customer_id=customer_id,
            name=f"Customer {str(customer_id)[:8]}",
            email="customer@example.com",
            phone_number="+0000000000",
        )
