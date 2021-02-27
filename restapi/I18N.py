import json

with open('locales/en/translate.json', 'rb') as f:
    en_translate = json.loads(f.read(), object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})

with open('locales/id/translate.json', 'rb') as f:
    id_translate = json.loads(f.read(), object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()})

PydanticError = {
    'en': en_translate['PydanticError'],
    'id': id_translate['PydanticError']
}
ResponseMessages = {
    'en': en_translate['ResponseMessages'],
    'id': id_translate['ResponseMessages']
}
HttpError = {
    'en': en_translate['HttpError'],
    'id': id_translate['HttpError']
}
