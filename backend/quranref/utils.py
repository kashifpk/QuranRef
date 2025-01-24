import hashlib
import base64


def text_to_digest(text: str) -> str:
    return base64.urlsafe_b64encode(hashlib.shake_256(text.encode()).digest(6)).decode()
