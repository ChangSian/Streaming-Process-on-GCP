##Token
bearer_token = r'AAAAAAAAAAAAAAAAAAAAAN6yUAEAAAAAKuVoq0kNmLPK2XWVG9nv4WTbd38%3DYYmajyFpf39qIl8KDeMYrlTj1ptFqcTbZRlC0KIObuPMlEvAqS'
consumer_key = '3XTmUu99cyte9ZoWkxpAtx4bD'
consumer_secret = 'YV3ei9cFgcuEwhWxHOKt7x0tB1WaBoURL341xHeLvS5mf5d163'
access_token_key = '1845731575-fXIXALnnPKudDgqt8gDIRKp6DYMZhu5P3JEmeuG'
access_token_secret = 'i9ozC5rIR6KpP7VTxa972cwF3mhHhrucyq8MKhsTPq9f1'

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r