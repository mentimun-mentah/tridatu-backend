refresh_token_cookie = {
    "name": "refresh_token_cookie",
    "in": "cookie",
    "required": False,
    "schema": {
        "title": "refresh_token_cookie",
        "type": "string"
    }
}

access_token_cookie = {
    "name": "access_token_cookie",
    "in": "cookie",
    "required": False,
    "schema": {
        "title": "access_token_cookie",
        "type": "string"
    }
}

csrf_token_header = {
    "name": "X-CSRF-TOKEN",
    "in": "header",
    "required": True,
    "schema": {
        "title": "X-CSRF-TOKEN",
        "type": "string"
    }
}

list_access_token = [
    'access_revoke', 'add_password', 'update_password', 'update_avatar'
]

list_refresh_token = [
    'refresh_token','refresh_revoke'
]
