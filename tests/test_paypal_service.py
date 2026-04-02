from app.services.paypal_service import (
    extract_subscription_id_from_webhook,
    extract_user_id_from_custom_id,
    get_approval_url,
)


def test_extract_user_id_from_custom_id():
    assert extract_user_id_from_custom_id("user:42|plan:mensual") == 42
    assert extract_user_id_from_custom_id("invalid") is None


def test_extract_subscription_id_from_webhook_for_subscription_event():
    event = {
        "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
        "resource": {"id": "I-ABC123"},
    }
    assert extract_subscription_id_from_webhook(event) == "I-ABC123"


def test_extract_subscription_id_from_webhook_for_payment_sale_event():
    event = {
        "event_type": "PAYMENT.SALE.COMPLETED",
        "resource": {
            "supplementary_data": {
                "related_ids": {
                    "subscription_id": "I-SALE123",
                }
            }
        },
    }
    assert extract_subscription_id_from_webhook(event) == "I-SALE123"


def test_get_approval_url():
    payload = {
        "links": [
            {"rel": "self", "href": "https://api.example/self"},
            {"rel": "approve", "href": "https://www.paypal.com/checkoutnow?token=abc"},
        ]
    }
    assert get_approval_url(payload) == "https://www.paypal.com/checkoutnow?token=abc"
