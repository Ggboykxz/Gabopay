"""Tests pour les modèles de base"""

import pytest
from apps.api.models.merchant import Merchant, MerchantStatus, KYCStatus
from apps.api.models.transaction import Transaction, TransactionStatus, TransactionMethod, TransactionMode
from apps.api.models.provider import ProviderAccount, ProviderType
from apps.api.core.security import generate_api_key, verify_api_key, parse_api_key, generate_hmac_signature, verify_hmac_signature


class TestApiKeySecurity:
    """Tests pour la sécurité des API keys"""

    def test_generate_api_key_with_test_prefix(self):
        """Test génération API key test"""
        key, key_hash = generate_api_key("gp_test")
        assert key.startswith("gp_test_")
        assert len(key_hash) == 64

    def test_generate_api_key_with_live_prefix(self):
        """Test génération API key live"""
        key, key_hash = generate_api_key("gp_live")
        assert key.startswith("gp_live_")

    def test_verify_api_key_success(self):
        """Test vérification API key valide"""
        key, key_hash = generate_api_key("gp_test")
        assert verify_api_key(key, key_hash) is True

    def test_verify_api_key_failure(self):
        """Test vérification API key invalide"""
        _, key_hash = generate_api_key("gp_test")
        assert verify_api_key("wrong_key", key_hash) is False

    def test_parse_valid_test_api_key(self):
        """Test parsing API key test valide"""
        result = parse_api_key("gp_test_sk_abc123")
        assert result == ("gp_test", "test")

    def test_parse_valid_live_api_key(self):
        """Test parsing API key live valide"""
        result = parse_api_key("gp_live_sk_xyz789")
        assert result == ("gp_live", "live")

    def test_parse_invalid_api_key(self):
        """Test parsing API key invalide"""
        assert parse_api_key("invalid_key") is None
        assert parse_api_key("gp_wrong_key") is None
        assert parse_api_key("") is None


class TestHMACSignature:
    """Tests pour les signatures HMAC"""

    def test_generate_signature(self):
        """Test génération signature"""
        signature = generate_hmac_signature('{"test": "data"}', "my_secret")
        assert signature.startswith("t=")
        assert "v1=" in signature

    def test_verify_signature_success(self):
        """Test vérification signature valide"""
        payload = '{"amount": 5000}'
        signature = generate_hmac_signature(payload, "secret")
        assert verify_hmac_signature(payload, signature, "secret") is True

    def test_verify_signature_failure(self):
        """Test vérification signature invalide"""
        payload = '{"amount": 5000}'
        signature = generate_hmac_signature(payload, "secret")
        assert verify_hmac_signature(payload, signature, "wrong_secret") is False

    def test_verify_signature_replay_attack(self):
        """Test protection contre replay attack"""
        import time
        payload = '{"test": "data"}'
        signature = generate_hmac_signature(payload, "secret", int(time.time()) - 400)
        assert verify_hmac_signature(payload, signature, "secret") is False


class TestModels:
    """Tests pour les modèles SQLAlchemy"""

    def test_merchant_status_values(self):
        """Test valeurs status marchand"""
        assert MerchantStatus.PENDING == "pending"
        assert MerchantStatus.ACTIVE == "active"
        assert MerchantStatus.SUSPENDED == "suspended"
        assert MerchantStatus.DELETED == "deleted"

    def test_kyc_status_values(self):
        """Test valeurs KYC"""
        assert KYCStatus.PENDING == "pending"
        assert KYCStatus.SUBMITTED == "submitted"
        assert KYCStatus.VERIFIED == "verified"
        assert KYCStatus.REJECTED == "rejected"

    def test_transaction_status_values(self):
        """Test valeurs status transaction"""
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.PROCESSING == "processing"
        assert TransactionStatus.SUCCEEDED == "succeeded"
        assert TransactionStatus.FAILED == "failed"
        assert TransactionStatus.REFUNDED == "refunded"

    def test_transaction_method_values(self):
        """Test valeurs méthode paiement"""
        assert TransactionMethod.AIRTEL_MONEY == "airtel_money"
        assert TransactionMethod.MOOV_MONEY == "moov_money"
        assert TransactionMethod.CARD == "card"
        assert TransactionMethod.CASH == "cash"

    def test_provider_type_values(self):
        """Test valeurs type provider"""
        assert ProviderType.AIRTEL_MONEY == "airtel_money"
        assert ProviderType.MOOV_MONEY == "moov_money"
        assert ProviderType.CARD == "card"