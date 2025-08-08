import requests
import base64
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class PayPalAPI:
    """PayPal API integration utility"""
    
    def __init__(self):
        # Load credentials from Django settings (which loads from .env)
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'PAYPAL_SECRET', None)
        self.api_base = getattr(settings, 'PAYPAL_API_BASE', 'https://api-m.paypal.com')
        self.access_token = None
        
        # Validate PayPal configuration
        if not self.client_id or not self.client_secret:
            logger.error("PayPal credentials not configured. Please set PAYPAL_CLIENT_ID and PAYPAL_SECRET in .env file")
        elif self.client_id.strip() == "" or self.client_secret.strip() == "":
            logger.error("PayPal credentials are empty. Please check your .env file")
        elif self._are_placeholder_credentials():
            logger.warning("PayPal credentials appear to be placeholder/example credentials")
            logger.warning("Please get real PayPal credentials from https://developer.paypal.com/")
            logger.warning("See GET_REAL_PAYPAL_SANDBOX_CREDENTIALS.md for instructions")
        else:
            # Log successful configuration (without exposing credentials)
            client_id_preview = f"{self.client_id[:8]}...{self.client_id[-4:]}" if len(self.client_id) > 12 else "***"
            logger.info(f"PayPal configuration loaded successfully - Client ID: {client_id_preview}, API Base: {self.api_base}")
            
            # Determine environment
            if 'sandbox' in self.api_base.lower():
                logger.info("PayPal configured for SANDBOX environment")
            else:
                logger.info("PayPal configured for LIVE environment")
    
    def _are_placeholder_credentials(self):
        """Check if credentials are placeholder/example values"""
        placeholder_patterns = [
            "AX-fjz_IjsdMWVi7Vn7eAVIYO4E-_hJf_Rq95sM3846o6pk",  # Current placeholder
            "EIeNSv_r8UGAX5qlwRlQ2BJGzfyOvjomZqp5-sbXww_JCcSXfOeBL7cwh-6f3FZQ0pnfV7WgQzbgbs4Z",  # Current placeholder
            "your_client_id_here",
            "your_secret_here",
            "sb-1vjnx44839480@business.example.com",
            "your_live_paypal_client_id_here",
            "your_sandbox_client_id_here"
        ]
        
        return (self.client_id in placeholder_patterns or 
                self.client_secret in placeholder_patterns or
                "example" in self.client_id.lower() or
                "placeholder" in self.client_id.lower())
    
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
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"PayPal API error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 401:
                    logger.error("PayPal authentication failed. Please check your PAYPAL_CLIENT_ID and PAYPAL_SECRET.")
            else:
                logger.error(f"PayPal network error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get PayPal access token: {e}")
            raise
    
    def create_order(self, amount, currency="GBP", description="Booking Payment", custom_id=None):
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
            
            purchase_unit = {
                "amount": {
                    "currency_code": currency,
                    "value": str(amount)
                },
                "description": description
            }
            
            # Add custom_id if provided (for tracking booking)
            if custom_id:
                purchase_unit["custom_id"] = str(custom_id)
            
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [purchase_unit],
                "application_context": {
                    "return_url": "https://www.access-auto-services.co.uk/booking/payment-success",
                    "cancel_url": "https://www.access-auto-services.co.uk/booking/payment-cancel",
                    "brand_name": "Access Auto Services",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "payment_method": {
                        "payer_selected": "PAYPAL",
                        "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                    }
                }
            }
            
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            
            order = response.json()
            logger.info(f"PayPal order created: {order.get('id')}")
            
            return order
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"PayPal create order error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 400:
                    logger.error("PayPal order creation failed. Check order data format and credentials.")
                elif e.response.status_code == 401:
                    logger.error("PayPal authentication failed. Access token may be expired.")
            else:
                logger.error(f"PayPal network error: {e}")
            raise
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
    

    
    def send_payout(self, recipient_email, amount, currency="GBP", note="Payment from Access Auto Services"):
        """Send payout to recipient (for refunds or payments to service providers)"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.api_base}/v1/payments/payouts"
            
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": f"payout-{int(time.time())}",
                    "email_subject": "You have a payment from Access Auto Services",
                    "email_message": note
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "receiver": recipient_email,
                    "note": note,
                    "sender_item_id": f"item-{int(time.time())}"
                }]
            }
            
            headers_req = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.post(url, headers=headers_req, json=payout_data)
            response.raise_for_status()
            
            payout = response.json()
            logger.info(f"Payout sent: {payout.get('batch_header', {}).get('payout_batch_id')}")
            
            return payout
            
        except Exception as e:
            logger.error(f"Failed to send payout: {e}")
            raise

# Singleton instance
paypal_api = PayPalAPI()