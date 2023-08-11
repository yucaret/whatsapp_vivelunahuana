import requests
import sett
import json
import time
import openai
import csv
import os
from datetime import datetime
import pandas as pd
import time

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
        return e, 403
    
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
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a ViveLunahuana. ¿Cómo podemos ayudarte hoy?"
        footer = "Equipo ViveLunahuana"
        footer = "Equipo ViveLunahuana"
        options = ["✅ servicios", "📅 agendar cita"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        list.append(replyReaction)
        list.append(replyButtonData)
    elif "servicios" in text:
        body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estos servicios te gustaría explorar?"
        footer = "Equipo ViveLunahuana"
        options = ["Analítica Avanzada", "Migración Cloud", "Inteligencia de Negocio"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2",messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(listReplyData)
        list.append(sticker)
    elif "inteligencia de negocio" in text:
        body = "Buenísima elección. ¿Te gustaría que te enviara un documento PDF con una introducción a nuestros métodos de Inteligencia de Negocio?"
        footer = "Equipo ViveLunahuana"
        options = ["✅ Sí, envía el PDF.", "⛔ No, gracias"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed3",messageId)
        list.append(replyButtonData)
    elif "sí, envía el pdf" in text:
        sticker = sticker_Message(number, get_media_id("pelfet", "sticker"))
        textMessage = text_Message(number,"Genial, por favor espera un momento.")

        enviar_Mensaje_whatsapp(sticker)
        enviar_Mensaje_whatsapp(textMessage)
        time.sleep(3)

        document = document_Message(number, sett.document_url, "Listo 👍🏻", "Inteligencia de Negocio.pdf")
        enviar_Mensaje_whatsapp(document)
        time.sleep(3)

        body = "¿Te gustaría programar una reunión con uno de nuestros especialistas para discutir estos servicios más a fondo?"
        footer = "Equipo ViveLunahuana"
        options = ["✅ Sí, agenda reunión", "No, gracias." ]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData)
    elif "sí, agenda reunión" in text :
        body = "Estupendo. Por favor, selecciona una fecha y hora para la reunión:"
        footer = "Equipo ViveLunahuana"
        options = ["📅 10: mañana 10:00 AM", "📅 7 de junio, 2:00 PM", "📅 8 de junio, 4:00 PM"]

        listReply = listReply_Message(number, options, body, footer, "sed5",messageId)
        list.append(listReply)
    elif "7 de junio, 2:00 pm" in text:
        body = "Excelente, has seleccionado la reunión para el 7 de junio a las 2:00 PM. Te enviaré un recordatorio un día antes. ¿Necesitas ayuda con algo más hoy?"
        footer = "Equipo ViveLunahuana"
        options = ["✅ Sí, por favor", "❌ No, gracias."]


        buttonReply = buttonReply_Message(number, options, body, footer, "sed6",messageId)
        list.append(buttonReply)
    elif "no, gracias." in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas. Recuerda que también ofrecemos material gratuito para la comunidad. ¡Hasta luego  😊")
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

######################################################################################
# AGREGANDO LAS FUNCIONES PARA CHATGPT
######################################################################################
openai.api_key = sett.openai_api

def get_lista_para_contexto(df):
    lista_detalle = ""

    for i, row in df.iterrows():
        lista = ""
        
        j = 0
        for value in row:
            if j == 0:
                lista = str(value)
            else:
                lista = lista + '|' + str(value)

            j = j + 1

        if i == 0:
            lista_detalle = lista
        else:
            lista_detalle = lista_detalle + '\n' + lista
    
    return lista_detalle

def generar_respuesta_chatgpt(user_message, number, espedido=False):
    #################################################################################
    ## carga del archivo de configuracion
    #################################################################################
    ruta_archivo = "confugracion_2.xlsx"
    # Leer el archivo Excel con dos hojas
    try:
        xls = pd.ExcelFile(ruta_archivo)
    except Exception as e:
        print('xxxxxxxx no lee archivo excel de configuracion en generar_respuesta_chatgpt: ' + str(e))
        return 'no enviado'
    
    df_estructura = pd.read_excel(xls, "estructura_bot")
    #################################################################################
    # Contruyendo Estructura de Contexto
    #################################################################################

    # configurando variables para la estructura
    columnas_estructura_1 = df_estructura.columns.tolist()
    columnas_estructura_2 = df_estructura.values
    valores_estructura = columnas_estructura_2[1]
    columnas_estructura_2 = columnas_estructura_2[0]

    try:
        i = 0
        lista_estructura_contexto = ""
        for columna in columnas_estructura_1:
        
            lista_estructura_contexto = lista_estructura_contexto + '\n' + valores_estructura[i]

            if "detalle" in columna:
                detalle_item = columnas_estructura_2[i]

                df_item = pd.read_excel(xls, detalle_item)

                columnas_item = "|".join(str(value) for value in df_item.columns)
                lista_item = get_lista_para_contexto(df_item)
                
                lista_estructura_contexto = lista_estructura_contexto + '\n' + \
                                            'estructura del ' + detalle_item + ':' + '\n' + \
                                            columnas_item + '\n' + \
                                            'listado del ' + detalle_item + ':' + '\n' + \
                                            lista_item + '\n'
            
            i = i + 1
    except Exception as e:
        print('xxxxxxxx no lee la estructura de configuracion en generar_respuesta_chatgpt: ' + str(e))
        return 'no enviado'
    
    print('generar_respuesta_chatgpt espedido true')
    messages = [{'role':'system', 'content':lista_estructura_contexto}]

    historial = get_chat_from_csv(number)
    
    # 2023-07-30 21:06 (jorge eduardo vicente hernández): si hay historial lo añade
    ######
    if len(historial) > 0:
        messages.extend(historial)
    ######

    print('message:' ,messages )
    
    messages.append({'role': 'user', 'content': user_message})
    
    print('generar_respuesta_chatgpt')
    
    if espedido:
      print('generar_respuesta_chatgpt espedido true')
      messages.append(
                        {'role':'system', 'content':'En base a lo que el usuario (que su número celular es ' + str(number) + ') este pidiendo mayor información, \
                        categorizalo como cata, cursos de cata o viajes.  \
                        calcúla el precio total del servicio y considera si te a pedido descuento. \
                        Y devuelve una estructura de dicconario de python con los elementos:  \
                        1) celular, nombre de elemento "celular"; \
                        2) nombre completo del cliente, nombre del elemento "nombre completo"; \
                        3) correo electronico, nombre del elemento "correo"; \
                        4) categoria, nombre del elemento"categoria"; \
                        5) servicio, este elemento se refiere al servicio que pidio información, nombre del elemento "servicio"; \
                        6) precio total, nombre del elemento "precio".'},
                    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        ) 
    except Exception as e:
        print('xxxxxxxx no conecta a chatgpt en generar_respuesta_chatgpt: ' + str(e))
        return 'no enviado'

    print(response) 
    return response.choices[0].message["content"]

def text_Message_al_gerente(number, diccionarioConforme):
    print('entro al proceso text_Message_al_gerente')
    print(str(diccionarioConforme))
    print('convierte diccionario')
    diccionarioConforme = diccionarioConforme.replace('\n', '').replace(' ', '')
    diccionarioConforme = json.loads(str(diccionarioConforme))

    print('Imprimiento diccionario y clave')
    for clave, valor in diccionarioConforme.items():
       print(clave, valor)

    print('Salio de imprimiento diccionario y clave')
    text = 'Hola Victor, el cliente ' + str(diccionarioConforme['nombrecompleto']) + ' ' \
           'con celular ' + str(diccionarioConforme['celular']) + ' y correo ' + str(diccionarioConforme['correo']) + ' ' \
           'a solicitado un ' + str(diccionarioConforme['categoria']) + ' con el detalle de ' + str(diccionarioConforme['servicio']) + ' ' \
           'y precio total: ' + str(diccionarioConforme['precio']) + '.'
    #text = 'hola claudia...'
    data = text_Message(str(number),text)

    print('text_Message_al_gerente ' + str(data))

    return data

def generar_respuesta_chatgpt_original(user_message, number, espedido=False):
    print('generar_respuesta_chatgpt espedido true')
    messages = [{'role':'system', 'content':"""
                Eres BotPedido, un servicio automatizado para recoger pedidos para un restaurante de comida peruana. \
                Primero empieza la conversación saludando al cliente, luego recoges el pedido, \
                y luego preguntas si es para recoger o para entregar. \
                Esperas a recoger todo el pedido, luego lo resúmenes y verificas por última \
                vez si el cliente quiere agregar algo más. \
                Si es una entrega, pides una dirección. \
                Finalmente recoges el pago.\
                Asegúrate de aclarar todas las opciones, entradas, bebidas y tamaños para identificar \
                de forma única el artículo del menú.\
                Respondes de manera corta, precisa, muy conversacional y amigable. \
                El menú incluye \
                Ceviche  10 35 soles \
                Lomo saltado 12 28 soles \
                Arroz con pollo  11 26 soles \
                Entradas: \
                Tamales  10 soles \
                Anticuchos  22 soles \
                Papa rellena  15 soles \
                Bebidas: \
                Chicha Morada  6 soles \
                Inca Kola  5 soles \
                Agua embotellada  4 soles. \
                """}]
    historial = get_chat_from_csv(number)
    messages.extend(historial)
    print('message:' ,messages )
    
    messages.append({'role': 'user', 'content': user_message})
    print('generar_respuesta_chatgpt')
    if espedido:
      print('generar_respuesta_chatgpt espedido true')
      messages.append(
                        {'role':'system', 'content':'Crea un resumen del pedido anterior en formato JSON. \
                        Primero analiza el menu del restaurante ingresado al inicio \
                        contexto inicial y compara con el pedido del usuario y solo cuando hayas analizado  \
                        el pedido completo del usuario,  categorizalo en lista plato principal, lista de entradas, lista de bebidas.  \
                        luego actualizar el precio total del pedido una vez hayas listado cada item. \
                        Los campos del json deben ser  \
                        1) lista plato principal  con atributos de nombre , tamaño , cantidad precio, \
                        2) lista de entradas con atributos de nombre, cantidad y precio, \
                        3) lista de bebidas con atributos de nombre, cantidad y precio,  \
                        4) precio total.'},
                    )
      
    response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=messages,
          temperature=0
      ) 
    print(response) 
    return response.choices[0].message["content"]

def guardar_conversacion(conversation_id, number, name, user_msg,timestamp, bot_msg=''):
    try:
      conversations = []
      print('inicio de guardar_conversacion')
      cabeceras = ['messageId', 'number', 'name', 'user_msg', 'bot_msg', 'timestamp']
      conversation = [conversation_id, number, name, user_msg, bot_msg, datetime.fromtimestamp(timestamp)]
      print('se genero conversation en guardar_conversacion')
      # Guardar las conversaciones en el archivo CSV
      # 2023-07-30 21:06 (jorge eduardo vicente hernández): que guarde archivos por número de usuario
      #with open('conversaciones.csv', 'a', newline='') as csv_file:
      #    print('guardar conversacion')
      #####
      filename_conversaciones = 'conversaciones' + '_' + str(number) + '.csv'

      # verificamos si existe el archivo
      existe_archivo = os.path.exists(filename_conversaciones)

      with open(filename_conversaciones, 'a', newline='') as csv_file:
        print('guardar conversacion: ' + filename_conversaciones)
      ######

        data = csv.writer(csv_file, delimiter=',')

      ######
        if not existe_archivo:
            # Escribir la cabecera solo si el archivo no existe
            data.writerow(cabeceras)
      ######

        data.writerow(conversation)

      print ('se guardo la conversacion con guardar_conversacion')

      time.sleep(2)
      messages =  get_chat_from_csv(number)
      print ('mensajes del usuario desde guardar_conversacion: ', messages)
    except Exception as e:
        print('xxxxxxxxx  error en guardar_conversacion ' + str(e))
        return e,403
    

def get_chat_from_csv(number):
    messages = []
    print('inicio de get_chat_from_csv, el celular es: ' + str(number) + ' ....')

    # 2023-07-30 21:06 (jorge eduardo vicente hernández): que lea archivos por número de usuario
    #with open('conversaciones.csv') as file:
    #    reader = csv.DictReader(file)
    #    print('conversaciones.csv')
    ######
    try:
        filename_conversaciones = 'conversaciones' + '_' + str(number) + '.csv'
        with open(filename_conversaciones, 'r') as file:
            reader = csv.DictReader(file)
            print('conversaciones reader: ' + str(reader))
    ######
            for row in reader:
                print('row: ' + str(row))
                print('tipo de dato de numero: ' + str(type(number)))
                print('tipo de dato de row[numero]: ' + str(type(row['number'])))
                if row['number'] == number:
                    print('number ' + str(number))
                    user_msg = {'role': 'user', 'content': row['user_msg']}
                    bot_msg = {'role': 'assistant', 'content': row['bot_msg']}
                    messages.append(user_msg)
                    messages.append(bot_msg)
    ######
        print('exito get_chat_from_csv')
    except Exception as e:
        print('xxxxxxxx sin archivo, sin historial de get_chat_csv: ' + str(e))
    ######

    return messages

def guardar_pedido(jsonPedido, number):
    # Eliminar el texto que sigue al JSON
    print('guardar perdido')
    start_index = jsonPedido.find("{")
    end_index = jsonPedido.rfind("}")

    # Extrae la cadena JSON de la respuesta
    json_str = jsonPedido[start_index:end_index+1]

    # Convierte la cadena JSON en un objeto de Python
    pedido = json.loads(json_str)

    # Ahora puedes usar 'pedido' como un objeto de Python
    print('pedido', pedido)
    with open('pedidos.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        print('pedidos.csv')
        platos_principales = [f"{plato['cantidad']}  {plato['nombre']} - {plato['precio']} soles" for plato in pedido['plato_principal']]
        entradas = [f"{entrada['cantidad']} {entrada['nombre']} - {entrada['precio']} soles" for entrada in pedido['entradas']]
        bebidas = [f"{bebida['cantidad']} {bebida['nombre']} - {bebida['precio']} soles" for bebida in pedido['bebidas']]

        writer.writerow([number, 
                         ', '.join(platos_principales), 
                         ', '.join(entradas), 
                         ', '.join(bebidas), 
                         pedido['precio_total'], 
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
######################################################################################