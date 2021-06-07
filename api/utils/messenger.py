import json

def error(
        type: str,
        message: str
    ):

    return {
        "success": False,
        "error": type,
        "reason": message
    }

def send(
        data
    ):

    return {
        "success": True,
        "data": data
    }

def success():
    return {
        "success": True
    }