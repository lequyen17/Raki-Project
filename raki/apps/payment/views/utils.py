def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def build_public_uri(request, path):
    """
    Build an absolute callback URL reachable by external payment gateways.
  Prefer VNPAY_PUBLIC_BASE_URL when running behind ngrok/proxy.
    """
    from django.conf import settings

    base_url = getattr(settings, "VNPAY_PUBLIC_BASE_URL", "").rstrip("/")
    if base_url:
        return f"{base_url}{path}"
    return request.build_absolute_uri(path)
