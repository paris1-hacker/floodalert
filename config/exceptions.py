from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(response.data, dict) and "detail" in response.data:
        message = str(response.data["detail"])
        errors = None
    else:
        message = "Validation error."
        errors = response.data

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
    }

    return response