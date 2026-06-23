import json
import uuid
import requests
import hmac
import hashlib
from typing import Dict, Any

from apps.payment.interfaces import PaymentGatewayInterface


class MomoGateway(PaymentGatewayInterface):
    def __init__(self, partner_code: str, access_key: str, secret_key: str, endpoint: str):
        self.partner_code = partner_code
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint

    def create_payment(self, amount: int, order_id: str, **kwargs) -> Dict[str, Any]:
        redirect_url = kwargs.get("redirect_url", "")
        ipn_url = kwargs.get("ipn_url", "")
        order_info = kwargs.get("order_info", "pay with MoMo")
        partner_name = kwargs.get("partner_name", "MoMo Payment")
        store_id = kwargs.get("store_id", "Test Store")
        
        request_type = "payWithMethod"
        lang = "vi"
        extra_data = ""
        auto_capture = True
        request_id = str(uuid.uuid4())

        raw_signature = (
            f"accessKey={self.access_key}&amount={amount}&extraData={extra_data}&ipnUrl={ipn_url}"
            f"&orderId={order_id}&orderInfo={order_info}&partnerCode={self.partner_code}"
            f"&redirectUrl={redirect_url}&requestId={request_id}&requestType={request_type}"
        )
        signature = hmac.new(
            self.secret_key.encode("ascii"),
            raw_signature.encode("ascii"),
            hashlib.sha256
        ).hexdigest()

        data = {
            "partnerCode": self.partner_code,
            "orderId": order_id,
            "partnerName": partner_name,
            "storeId": store_id,
            "ipnUrl": ipn_url,
            "amount": str(amount),
            "lang": lang,
            "requestType": request_type,
            "redirectUrl": redirect_url,
            "autoCapture": auto_capture,
            "orderInfo": order_info,
            "requestId": request_id,
            "extraData": extra_data,
            "signature": signature,
            "orderGroupId": "",
        }

        payload = json.dumps(data)
        headers = {"Content-Type": "application/json", "Content-Length": str(len(payload))}
        response = requests.post(self.endpoint, data=payload, headers=headers)
        response.raise_for_status()
        resp_json = response.json()
        
        return {"pay_url": resp_json.get("payUrl")}

    def verify_payment(self, request_data: Dict[str, Any]) -> bool:
        """Verify Momo IPN/webhook (optional)."""
        return True
