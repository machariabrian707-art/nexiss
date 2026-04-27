import stripe
from nexiss.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class BillingService:
    async def create_customer(self, org_id: str, org_name: str, email: str) -> str:
        customer = stripe.Customer.create(
            name=org_name,
            email=email,
            metadata={'org_id': org_id},
        )
        return customer.id

    async def create_checkout_session(self, customer_id: str, price_id: str, success_url: str, cancel_url: str) -> str:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url

    async def create_portal_session(self, customer_id: str, return_url: str) -> str:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url

    async def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return {'type': event['type'], 'data': event['data']['object']}


billing_service = BillingService()
