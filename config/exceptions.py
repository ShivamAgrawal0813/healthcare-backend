from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize API error responses across the backend.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "error_type": exc.__class__.__name__,
            "message": "Validation or processing error occurred.",
            "errors": response.data
        }

        # Format friendly message if detail exists
        if isinstance(response.data, dict) and "detail" in response.data:
            custom_data["message"] = str(response.data["detail"])
        elif isinstance(response.data, list) and len(response.data) > 0:
            custom_data["message"] = str(response.data[0])

        response.data = custom_data

    return response
