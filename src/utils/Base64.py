import base64
import hashlib

def base64_encode(data):
    return base64.b64encode(data)

def base64_decode(data, validate=False):
    return base64.b64decode(data, validate=validate)

def compute_hash(data_bytes):
    return hashlib.sha256(data_bytes).hexdigest()