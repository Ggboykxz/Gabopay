"""Provider factory for getting provider instances."""

from apps.api.providers.base import BaseProvider
from apps.api.providers.airtel import get_airtel_provider
from apps.api.providers.moov import get_moov_provider
from apps.api.providers.card import get_card_provider


def get_provider(provider_type: str, mode: str = "test", test_phone: str = None) -> BaseProvider:
    """
    Get the appropriate provider instance.

    Args:
        provider_type: The type of provider (airtel_money, moov_money, card)
        mode: The API mode (test or live)
        test_phone: Phone number for test mode simulation

    Returns:
        Provider instance
    """
    providers = {
        "airtel_money": get_airtel_provider,
        "moov_money": get_moov_provider,
        "card": get_card_provider,
    }

    provider_func = providers.get(provider_type)
    if not provider_func:
        raise ValueError(f"Unknown provider type: {provider_type}")

    if provider_type in ("airtel_money", "moov_money"):
        return provider_func(mode, test_phone)
    return provider_func()


# Fee configuration
FEES = {
    "airtel_money": {
        "percentage": 1.5,
        "fixed": 0,
        "min": 50,
    },
    "moov_money": {
        "percentage": 1.5,
        "fixed": 0,
        "min": 50,
    },
    "card": {
        "percentage": 2.9,
        "fixed": 100,
        "min": 150,
    },
}


def calculate_fee(amount: int, method: str) -> int:
    """
    Calculate platform fee for a transaction.

    Args:
        amount: Transaction amount in XAF
        method: Payment method

    Returns:
        Fee amount in XAF (integer)
    """
    fee_config = FEES.get(method, FEES["airtel_money"])

    percentage_fee = int(amount * (fee_config["percentage"] / 100))
    total_fee = percentage_fee + fee_config["fixed"]

    return max(total_fee, fee_config["min"])