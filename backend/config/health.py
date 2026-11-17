from django.http import JsonResponse
from django.db import connection
import logging


def healthz(request):
	try:
		with connection.cursor() as cursor:
			cursor.execute("SELECT 1")
	except Exception:
		return JsonResponse({"status": "error"}, status=503)
	
	return JsonResponse({"status": "ok"})
		
class HideSuccessfulHealthProbesFilter(logging.Filter):
	def filter(self, record):
		return "/healthz" not in record.getMessage()