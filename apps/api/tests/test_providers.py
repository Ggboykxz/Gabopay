"""Tests pour les providers de paiement"""

import pytest
from apps.api.providers.base import PaymentRequest, PaymentResponse, RefundRequest, RefundResponse, simulate_test_payment
from apps.api.providers.factory import get_provider, calculate_fee, FEES


class TestSimulateTestPayment:
    """Tests pour la simulation de paiement en mode test"""

    def test_simulate_success_number(self):
        """Test numéro spécial = succès"""
        response = simulate_test_payment("+24100000001", 5000)
        assert response.success is True
        assert response.status == "succeeded"

    def test_simulate_failed_number(self):
        """Test numéro spécial = échec"""
        response = simulate_test_payment("+24100000002", 5000)
        assert response.success is False
        assert response.status == "failed"
        assert response.error_code == "insufficient_funds"

    def test_simulate_timeout_number(self):
        """Test numéro spécial = timeout"""
        response = simulate_test_payment("+24100000003", 5000)
        assert response.status == "pending"

    def test_simulate_random_number(self):
        """Test numéro aléatoire"""
        response = simulate_test_payment("+24177123456", 5000)
        assert response.provider_ref is not None


class TestFeeCalculation:
    """Tests pour le calcul des frais"""

    def test_airtel_money_fee(self):
        """Test frais Airtel Money (1.5%, min 50)"""
        # 5000 * 1.5% = 75
        fee = calculate_fee(5000, "airtel_money")
        assert fee == 75

    def test_airtel_money_minimum_fee(self):
        """Test frais minimum Airtel Money"""
        # 1000 * 1.5% = 15 < 50, donc minimum 50
        fee = calculate_fee(1000, "airtel_money")
        assert fee == 50

    def test_moov_money_fee(self):
        """Test frais Moov Money (1.5%, min 50)"""
        fee = calculate_fee(10000, "moov_money")
        assert fee == 150

    def test_card_fee(self):
        """Test frais carte (2.9% + 100, min 150)"""
        # 10000 * 2.9% + 100 = 390
        fee = calculate_fee(10000, "card")
        assert fee == 390

    def test_card_minimum_fee(self):
        """Test frais minimum carte"""
        # 1000 * 2.9% + 100 = 129 < 150, donc minimum 150
        fee = calculate_fee(1000, "card")
        assert fee == 150

    def test_unknown_method_uses_airtel(self):
        """Test méthode inconnue utilise tarif Airtel"""
        fee = calculate_fee(5000, "unknown")
        assert fee == 75


class TestFeesConfiguration:
    """Tests pour la configuration des frais"""

    def test_airtel_fee_structure(self):
        """Test structure frais Airtel"""
        assert FEES["airtel_money"]["percentage"] == 1.5
        assert FEES["airtel_money"]["fixed"] == 0
        assert FEES["airtel_money"]["min"] == 50

    def test_moov_fee_structure(self):
        """Test structure frais Moov"""
        assert FEES["moov_money"]["percentage"] == 1.5
        assert FEES["moov_money"]["fixed"] == 0
        assert FEES["moov_money"]["min"] == 50

    def test_card_fee_structure(self):
        """Test structure frais carte"""
        assert FEES["card"]["percentage"] == 2.9
        assert FEES["card"]["fixed"] == 100
        assert FEES["card"]["min"] == 150


class TestProviderFactory:
    """Tests pour la factory de providers"""

    def test_get_airtel_provider_test_mode(self):
        """Test获取 Airtel provider mode test"""
        provider = get_provider("airtel_money", mode="test", test_phone="+24100000001")
        assert provider is not None
        assert provider.get_provider_type() == "airtel_money"

    def test_get_moov_provider_test_mode(self):
        """Test获取 Moov provider mode test"""
        provider = get_provider("moov_money", mode="test", test_phone="+24100000001")
        assert provider is not None
        assert provider.get_provider_type() == "moov_money"

    def test_get_card_provider(self):
        """Test获取 Card provider"""
        provider = get_provider("card")
        assert provider is not None
        assert provider.get_provider_type() == "card"

    def test_get_unknown_provider_raises(self):
        """Test provider inconnu lève erreur"""
        with pytest.raises(ValueError):
            get_provider("unknown_provider")