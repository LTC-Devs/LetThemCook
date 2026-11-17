import logging

import requests
from django.http import HttpRequest, JsonResponse

from .services import fetch_product_info, search_products

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def lookup(request: HttpRequest):
    ean = request.GET.get("ean", "").strip()
    if not (ean.isdigit() and 8 <= len(ean) <= 14):
        return JsonResponse({"error": "invalid ean"}, status=400)

    try:
        info = fetch_product_info(ean)
    except requests.RequestException as e:
        logger.error("ERROR: Req:", e.request, "Resp:", e.response)
        return JsonResponse({"error": "upstream unavailable"}, status=502)

    if not info:
        logger.warning("EAN not found upstream: %s", ean)
        return JsonResponse({"error": "ean not found upstream"}, status=404)

    matches = [{"id": p.id, "data": p.name} for p in search_products(info)]
    return JsonResponse({"ean": ean, "upstream_data": info, "matches": matches})
