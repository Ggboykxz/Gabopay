"""GABOPAY SDK Errors"""


class GabopayError(Exception):
    """Base error for GABOPAY SDK"""

    def __init__(self, message: str, status_code: Optional[int] = None, code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


class WebhookVerificationError(Exception):
    """Error raised when webhook signature verification fails"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


from typing import Optional