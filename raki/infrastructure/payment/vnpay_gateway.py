import hashlib
import hmac
import urllib.parse
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from typing import Dict, Any

from apps.payment.interfaces import PaymentGatewayInterface


class VNPayGateway(PaymentGatewayInterface):
    def __init__(self, tmn_code: str, secret_key: str, payment_url: str):
        self.tmn_code = tmn_code
        self.secret_key = secret_key
        self.payment_url = payment_url

    def create_payment(self, amount: int, order_id: str, **kwargs) -> Dict[str, Any]:
        ipaddr = kwargs.get("ipaddr", "127.0.0.1")
        return_url = kwargs.get("return_url", "")
        order_info = kwargs.get("order_info", f"Thanh toan don hang {order_id}")
        
        tz = ZoneInfo("Asia/Ho_Chi_Minh")
        now = datetime.now(tz)
        expire = now + timedelta(minutes=60)

        request_data = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": amount * 100,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
            "vnp_ExpireDate": expire.strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": ipaddr,
            "vnp_ReturnUrl": return_url,
        }

        input_data = sorted(request_data.items())
        query_string = ""
        seq = 0
        for key, val in input_data:
            if val is not None and str(val) != "":
                if seq == 1:
                    query_string = query_string + "&" + key + "=" + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    query_string = key + "=" + urllib.parse.quote_plus(str(val))

        hash_value = self._hmacsha512(self.secret_key, query_string)
        pay_url = self.payment_url + "?" + query_string + "&vnp_SecureHash=" + hash_value
        
        return {"pay_url": pay_url}

    def verify_payment(self, request_data: Dict[str, Any]) -> bool:
        """Verify VNPay IPN or Return response"""
        data = request_data.copy()
        vnp_secure_hash = data.pop("vnp_SecureHash", "")
        data.pop("vnp_SecureHashType", None)

        input_data = sorted(data.items())
        hash_data = ""
        seq = 0
        for key, val in input_data:
            if str(key).startswith("vnp_") and val is not None and str(val) != "":
                if seq == 1:
                    hash_data = hash_data + "&" + str(key) + "=" + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hash_data = str(key) + "=" + urllib.parse.quote_plus(str(val))
                    
        hash_value = self._hmacsha512(self.secret_key, hash_data)
        return vnp_secure_hash.lower() == hash_value.lower()

    @staticmethod
    def _hmacsha512(key: str, data: str) -> str:
        byte_key = key.encode("utf-8")
        byte_data = data.encode("utf-8")
        return hmac.new(byte_key, byte_data, hashlib.sha512).hexdigest()
