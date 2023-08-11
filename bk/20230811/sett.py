import os

token = os.getenv("TOKEN_PERSONAL")

whatsapp_token = os.getenv("TOKEN_WAPP")

whatsapp_url = os.getenv("WAPP_URL")

whatsapp_phone_number_id = os.getenv("WAPP_PHONE_NUMBER_ID")

openai_api_key =  os.getenv("TOKEN_OPENAI_CHATGPT")

celular_gerente = os.getenv("CELULAR_GERENTE")

# 22-jul-2023 todos los tipos de media que soporta WhatsApp
media_types = {
    'audio/aac': 'aac',
    'audio/mp4': 'mp4',
    'audio/mpeg': 'mp3',
    'audio/amr': 'amr',
    'audio/ogg': 'ogg',
    'text/plain': 'txt',
    'application/pdf': 'pdf',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/msword': 'doc',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'image/jpeg': 'jpeg',
    'image/png': 'png',
    'video/mp4': 'mp4',
    'video/3gp': '3gp',
    'image/webp': 'webp',
}

"""
stickers = {
    "poyo_feliz": 984778742532668,
    "perro_traje": 1009219236749949,
    "perro_triste": 982264672785815,
    "pedro_pascal_love": 801721017874258,
    "pelfet": 3127736384038169,
    "anotado": 24039533498978939,
    "gato_festejando": 1736736493414401,
    "okis": 268811655677102,
    "cachetada": 275511571531644,
    "gato_juzgando": 107235069063072,
    "chicorita": 3431648470417135,
    "gato_triste": 210492141865964,
    "gato_cansado": 1021308728970759
}

document_url = "https://www.africau.edu/images/default/sample.pdf"
"""
