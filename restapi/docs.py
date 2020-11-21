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
    'access_revoke', 'add_password', 'update_password', 'update_avatar',
    'update_account', 'fresh_token', 'create_address', 'update_address',
    'main_address_true', 'delete_address', 'create_outlet', 'delete_outlet',
    'create_brand', 'update_brand', 'delete_brand', 'create_category',
    'update_category', 'delete_category', 'create_sub_category'
]

list_access_token_without_csrf = [
    'my_user', 'my_address', 'my_address_by_id', 'get_brand_by_id',
    'get_category_by_id'
]

list_refresh_token = [
    'refresh_token','refresh_revoke'
]
