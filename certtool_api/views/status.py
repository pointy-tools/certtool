from django.conf import settings
from django.http import JsonResponse


def status_check(*_):
    return JsonResponse(
        status=200,
        data={
            "success": True,
            "version": settings.VERSION,
        },
    )
