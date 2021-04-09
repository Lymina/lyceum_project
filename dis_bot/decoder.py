import base64


def decoder(string):
    en_bytes = string.encode("utf-8")
    de_bytes = base64.b64decode(en_bytes)
    result = de_bytes.decode("utf-8")
    return result
