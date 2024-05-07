def get_clean_user(username: str) -> str:
    """A small helper that removes whitespace and ensures username is
    lower case"""
    # If the github username has spaces there is an error which might be
    # that someone added a name after the username. Only return the github
    # username
    if len(username.split()) > 1:
        username = username.split()[0]
    return username.lower().strip()
