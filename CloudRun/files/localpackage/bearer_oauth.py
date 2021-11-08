def bearer_oauth(r):
    bearer_token = r'AAAAAAAAAAAAAAAAAAAAAN6yUAEAAAAAKuVoq0kNmLPK2XWVG9nv4WTbd38%3DYYmajyFpf39qIl8KDeMYrlTj1ptFqcTbZRlC0KIObuPMlEvAqS'
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r