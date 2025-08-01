import requests
import base64
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PayPalAPI:
    """PayPal API integration utility"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_SECRET
        self.api_base = settings.PAYPAL_API_BASE
        self.access_token = None
    
    def get_access_token(self):
        """Get PayPal access token"""
        try:
            url = f"{self.api_base}/v1/oauth2/token"
            
            # Create basic auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Accept": "application/json",
                "Accept-Language": "en_US",
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = "grant_type=client_credentials"
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            logger.info("PayPal access token obtained successfully")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise
    
    def create_order(self, amount, currency="GBP", description="Booking Payment"):
        """Create a PayPal order"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.api_base}/v2/checkout/orders"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "PayPal-Request-Id": f"booking-{amount}-{currency}"
            }
            
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    },
                    "description": description
                }],
                "application_context": {
                    "return_url": "https://www.access-auto-services.co.uk/booking/success",
                    "cancel_url": "https://www.access-auto-services.co.uk/booking/cancel"
                }
            }
            
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            
            order = response.json()
            logger.info(f"PayPal order created: {order.get('id')}")
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to create PayPal order: {e}")
            raise
    
    def capture_order(self, order_id):
        """Capture a PayPal order"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.api_base}/v2/checkout/orders/{order_id}/capture"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            capture_data = response.json()
            logger.info(f"PayPal order captured: {order_id}")
            
            return capture_data
            
        except Exception as e:
            logger.error(f"Failed to capture PayPal order {order_id}: {e}")
            raise
    
    def get_order_details(self, order_id):
        """Get PayPal order details"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.api_base}/v2/checkout/orders/{order_id}"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            order_details = response.json()
            logger.info(f"PayPal order details retrieved: {order_id}")
            
            return order_details
            
        except Exception as e:
            logger.error(f"Failed to get PayPal order details {order_id}: {e}")
            raise

# Singleton instance
paypal_api = PayPalAPI()