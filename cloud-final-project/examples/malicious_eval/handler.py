def handler(event, context):
    return eval(event.get("expression", "1 + 1"))
