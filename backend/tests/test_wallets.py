"""
Tests for Wallet API endpoints
"""
import pytest
from decimal import Decimal
from httpx import AsyncClient

from app.models import User


@pytest.mark.asyncio
class TestWalletAPI:
    """Test wallet operations"""

    async def test_get_wallet_balance(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting wallet balance"""
        response = await client.get(
            "/api/v1/wallets/balance",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["user_id"] == str(test_user.id)
        assert Decimal(data["balance_usdc"]) == Decimal("1000.00")
        assert "total_earned" in data
        assert "total_spent" in data

    async def test_deposit_funds(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test depositing funds"""
        response = await client.post(
            "/api/v1/wallets/deposit",
            headers=auth_headers,
            json={
                "amount": "500.00",
                "transaction_hash": "0x123abc",
                "metadata": {"source": "test"}
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["type"] == "DEPOSIT"
        assert Decimal(data["amount"]) == Decimal("500.00")
        assert Decimal(data["balance_after"]) == Decimal("1500.00")
        assert data["transaction_hash"] == "0x123abc"

    async def test_deposit_negative_amount(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test depositing negative amount fails"""
        response = await client.post(
            "/api/v1/wallets/deposit",
            headers=auth_headers,
            json={"amount": "-100.00"}
        )

        assert response.status_code == 422  # Validation error

    async def test_withdraw_funds(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test withdrawing funds"""
        response = await client.post(
            "/api/v1/wallets/withdraw",
            headers=auth_headers,
            json={
                "amount": "100.00",
                "destination_address": "0xabc123"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["type"] == "WITHDRAWAL"
        assert Decimal(data["amount"]) == Decimal("100.00")
        assert Decimal(data["balance_after"]) == Decimal("900.00")

    async def test_withdraw_insufficient_funds(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test withdrawing more than balance fails"""
        response = await client.post(
            "/api/v1/wallets/withdraw",
            headers=auth_headers,
            json={"amount": "2000.00"}
        )

        assert response.status_code == 402  # Payment required
        assert "Insufficient funds" in response.json()["detail"]

    async def test_get_transaction_history(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting transaction history"""
        # Make a deposit first
        await client.post(
            "/api/v1/wallets/deposit",
            headers=auth_headers,
            json={"amount": "250.00"}
        )

        # Get transactions
        response = await client.get(
            "/api/v1/wallets/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["type"] == "DEPOSIT"
        assert Decimal(data[0]["amount"]) == Decimal("250.00")

    async def test_get_transaction_history_with_filter(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test filtering transaction history"""
        # Make deposit and withdrawal
        await client.post(
            "/api/v1/wallets/deposit",
            headers=auth_headers,
            json={"amount": "250.00"}
        )
        await client.post(
            "/api/v1/wallets/withdraw",
            headers=auth_headers,
            json={"amount": "50.00"}
        )

        # Filter by type
        response = await client.get(
            "/api/v1/wallets/transactions?transaction_type=DEPOSIT",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert all(tx["type"] == "DEPOSIT" for tx in data)

    async def test_get_spending_analytics(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting spending analytics"""
        response = await client.get(
            "/api/v1/wallets/analytics?days=30",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "period_days" in data
        assert "total_spent" in data
        assert "total_transactions" in data
        assert "current_balance" in data
        assert "lifetime_spent" in data
        assert "lifetime_earned" in data
        assert data["period_days"] == 30

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing wallet without authentication"""
        response = await client.get("/api/v1/wallets/balance")

        assert response.status_code == 401
