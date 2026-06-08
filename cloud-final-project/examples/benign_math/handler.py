def handler(event, context):
    numbers = event.get("numbers", [])
    return {"sum": sum(numbers), "count": len(numbers)}
