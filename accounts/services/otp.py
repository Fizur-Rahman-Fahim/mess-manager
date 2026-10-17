"""OTP login stub for future SMS integration."""

def send_otp(mobile_number: str) -> bool:
    """Send OTP to mobile number. Not implemented in v1."""
    raise NotImplementedError('OTP login is planned for a future release.')

def verify_otp(mobile_number: str, code: str) -> bool:
    """Verify OTP code. Not implemented in v1."""
    raise NotImplementedError('OTP login is planned for a future release.')
