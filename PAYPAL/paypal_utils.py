import requests
import base64
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class PayPalAPI:
    """PayPal API integration utility"""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_SECRET
        self.api_base = settings.PAYPAL_API_BASE
        self.webhook_id = getattr(settings, 'PAYPAL_WEBHOOK_ID', None)
        self.access_token = None
        
        # Validate PayPal configuration
        if not self.client_id or not self.client_secret:
            logger.error("PayPal credentials not configured. Please set PAYPAL_CLIENT_ID and PAYPAL_SECRET in environment variables.")
        elif self.client_id in ["sb-1vjnx44839480@business.example.com", "your_live_paypal_client_id_here"]:
            logger.error("PayPal credentials are still placeholders. Please update with real credentials from https://developer.paypal.com/")
        else:
            logger.info("PayPal configuration loaded successfully")
    
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
    
    def verify_webhook_signature(self, headers, body):
        """Verify PayPal webhook signature"""
        try:
            if not self.webhook_id:
                logger.warning("PayPal webhook ID not configured")
                return False
            
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.api_base}/v1/notifications/verify-webhook-signature"
            
            verification_data = {
                "auth_algo": headers.get('PAYPAL-AUTH-ALGO'),
                "cert_id": headers.get('PAYPAL-CERT-ID'),
                "transmission_id": headers.get('PAYPAL-TRANSMISSION-ID'),
                "transmission_sig": headers.get('PAYPAL-TRANSMISSION-SIG'),
                "transmission_time": headers.get('PAYPAL-TRANSMISSION-TIME'),
                "webhook_id": self.webhook_id,
                "webhook_event": body
            }
            
            headers_req = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.post(url, headers=headers_req, json=verification_data)
            response.raise_for_status()
            
            result = response.json()
            verification_status = result.get('verification_status')
            
            logger.info(f"Webhook verification status: {verification_status}")
            return verification_status == 'SUCCESS'
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False
    
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