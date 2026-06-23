from rest_framework.response import Response


def first_validation_error(errors):
    if isinstance(errors, list):
        return str(errors[0])
    if isinstance(errors, dict):
        for value in errors.values():
            return first_validation_error(value)
    return str(errors)


def parse_request(request, serializer_class, **context):
    serializer = serializer_class(data=request.data, context=context)
    try:
        valid = serializer.is_valid()
    except LookupError as e:
        return None, Response({"error": str(e)}, status=404)

    if not valid:
        return None, Response(
            {"error": first_validation_error(serializer.errors)},
            status=400,
        )

    return serializer.validated_data, None
