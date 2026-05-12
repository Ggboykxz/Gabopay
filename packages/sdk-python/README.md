# GABOPAY Python SDK

Python SDK for the GABOPAY payment infrastructure API.

## Installation

```bash
pip install gabopay
```

## Usage

```python
from gabopay import Gabopay

client = Gabopay(secret_key="gp_test_...")
charge = client.charges_create(amount=5000, method="airtel_money", phone="+24100000001")
```
