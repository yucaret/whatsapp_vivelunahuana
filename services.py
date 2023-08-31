import requests
import sett
import json
import time
import os

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'

    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def video_Message(number, video_file_path):
    
    print('dentro de video message')
    try:
        video_file = os.open(video_file_path, "rb")
    except Exception as e:
        print('error: ' + str(e))

    print('cargamos el video')

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "video",
            "video": {
                "file": video_file
            }
        }
    )

    print('cargamos la data')

    return data

def quickreply_Message(number, quickreplyId):
    
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "quick_reply",
            "quick_reply": {  # Nombre correcto de la clave
                "id": quickreplyId
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def administrar_chatbot(text,number, messageId, name):
    pie_pagina = "Team Vive Lunahuana!!!"
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if "hola" in text:
        footer = pie_pagina

        # reaccion al mensaje
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        enviar_Mensaje_whatsapp(replyReaction)
        time.sleep(2)

        # mensaje de inicio
        texto_ = '¡Hola! Soy Claudia, del equipo Vive Lunahuaná. 🌿🐾 Descubre una increíble experiencia vivencial en ' \
                 'una nuestro fundo con piscina de 1000m2 en Lunahuaná, donde disfrutarás de la naturaleza al máximo. ¡Somos pet-friendly! 🐶.\n\n' \
                 'Estamos a solo 5 cuadras de la Plaza de Lunahuaná. 😊🐶 ¿Listo para vivir momentos inolvidables rodeado de la naturaleza con '\
                 'toda la familia o pareja👩❤️‍👨?'
        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # lista de opciones
        body = 'Solo  recibimos a 2 grupos familiares, tenemos paquetes para grupos de:'

        footer = pie_pagina

        options = ["hasta 3 personas", "hasta 6 u 8 pers.", "hasta 10 u 18 pers."]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1", messageId)
        enviar_Mensaje_whatsapp(replyButtonData)

    elif "hasta 10 u 18 pers" in text:
        # mensaje
        texto_ = 'Nuestro depa equipado cuenta con un estilo minimalista y siempre rodeado de plantas. Disfruta de una vista increíble\n\n' \
                 'En este link puedes ver nuestras fotos y distribución:\n👉https://n9.cl/depavivelunahuana👈\n\n' \
                 'Estamos a solo 5 cuadras de la Plaza de Lunahuaná. 😊🐶 ¿Listo para vivir momentos inolvidables rodeado de la naturaleza '\
                 'con toda la familia?'

        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # lista de opciones
        body = 'Cuéntanos qué paquete te interesa:'

        footer = pie_pagina

        options = ["Fin de semana🙌", "Durante semana🌿", "Elegir una fecha"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1", messageId)

        enviar_Mensaje_whatsapp(replyButtonData)

    elif "fin de semana" in text:
        # mensaje
        texto_ = 'Súper! Tenemos activa nuestra Promo 😎ESCAPADA, te envío la info completa y videos de la experiencia 🌿☺️...'

        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # envio de video
        print("ingreso a video message")
        videoMessage = video_Message(number, '/root/wharsapp_vivelunahuana/vivelunahuana_depa_kaori.mp4')
        print("cargo el videomessage")
        enviar_Mensaje_whatsapp(videoMessage)
        print("envio el mensaje de video")
        time.sleep(2)

        texto_ = 'Envío un video (el video del depa con kao)'

        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # envio mensaje
        texto_ = "Fotos de nuestro jardín y piscina rodeada de árboles , un ambiente ideal para  conectar con la naturaleza 😊🍀"

        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # envio fotos
        texto_ = "Envío fotos de jardín y piscina"

        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # envio mensaje
        texto_ = 'Tu estadía incluye emocionantes actividades de turismo vivencial. 🌿👩🌾\n' \
                 '1.-Descubre nuestro BioHuertos, 🥑🍊🌱en un recorrido guiado y cosecha de frutos de temporada.\n' \
                 '2.-Explora la belleza del puente colgante San Lorenzo, ☀️ubicado a solo 5 minutos en carro.\n'\
                 'Nos trasladaremos en la movilidad de nuestros huéspedes, brindándote comodidad y acceso a bellos paisajes naturales.\n'\
                 '3. Aprende la historia y proceso de producción mientras disfrutas de una degustación de vinos y pisco en la Bodega.🍷🍇'

        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # envio mensaje
        texto_ = 'Como gesto de bienvenida, te obsequiamos leña para una fogata mágica bajo las estrellas🪵🔥🌟'
        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

        time.sleep(2)

        # envio mensaje
        texto_ = 'Visita este enlace para ver fotos de las actividades. 📸🏞'\
                 '👉 bit.ly/actividadesvivelunahuana\n\n¡No pierdas la oportunidad de conectarte plenamente con la naturaleza en Vive Lunahuaná!🫶☀️'
        textMessage = text_Message(number, texto_)
        enviar_Mensaje_whatsapp(textMessage)

    elif "hasta 3 personas" in text:
        body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estos servicios te gustaría explorar?"
        footer = "Equipo Bigdateros"
        options = ["Analítica Avanzada", "Migración Cloud", "Inteligencia de Negocio", "xxxx", "yyyy", "zzzz"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2",messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
    #elif "sí, envía el pdf" in text:
    elif "hasta 6 u 8 pers." in text:
        sticker = sticker_Message(number, get_media_id("pelfet", "sticker"))
        textMessage = text_Message(number,"Genial, por favor espera un momento.")

        enviar_Mensaje_whatsapp(sticker)
        enviar_Mensaje_whatsapp(textMessage)
        time.sleep(3)

        #document = document_Message(number, sett.document_url, "Listo 👍🏻", "Inteligencia de Negocio.pdf")
        document = document_Message(number, sett.document_url, "Listo!!!", "recibo.pdf")
        enviar_Mensaje_whatsapp(document)
        time.sleep(3)

        body = "¿Te gustaría programar una reunión con uno de nuestros especialistas para discutir estos servicios más a fondo?"
        footer = pie_pagina
        options = ["✅ Sí, agenda reunión", "No, gracias." ]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "sí, agenda reunión" in text :
        body = "Estupendo. Por favor, selecciona una fecha y hora para la reunión:"
        footer = pie_pagina
        options = ["📅 10: mañana 10:00 AM", "📅 7 de junio, 2:00 PM", "📅 8 de junio, 4:00 PM"]

        listReply = listReply_Message(number, options, body, footer, "sed5",messageId)
        list.append(listReply)
    elif "7 de junio, 2:00 pm" in text:
        body = "Excelente, has seleccionado la reunión para el 7 de junio a las 2:00 PM. Te enviaré un recordatorio un día antes. ¿Necesitas ayuda con algo más hoy?"
        footer = pie_pagina
        options = ["✅ Sí, por favor", "❌ No, gracias."]

        buttonReply = buttonReply_Message(number, options, body, footer, "sed6",messageId)
        list.append(buttonReply)
    elif "no, gracias." in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas. Recuerda que también ofrecemos material gratuito para la comunidad. ¡Hasta luego! :)")
        list.append(textMessage)
    else :
        data = text_Message(number,"Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s