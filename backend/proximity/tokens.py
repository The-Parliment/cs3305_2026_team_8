
def get_username(username: str) -> str:
    """
    this function needs to be updated when the front end is more complete, and is calling our proximity service
    with valid tokens for a registered/logged in user. For now, we just return the username from the request payload
    """
    return username