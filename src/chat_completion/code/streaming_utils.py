def add_context_to_streamed_response(response, context):
    first_resp = next(response)
    if not first_resp.choices:
        first_resp = next(response)
    first_resp.choices[0]["delta"]["context"] = context
    yield first_resp
    yield from response
