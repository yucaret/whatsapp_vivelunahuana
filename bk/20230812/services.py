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
    print("ingresando a obtener_Mensaje_whatsapp")
    if 'type' not in message :
        print("saliendo de obtener_Mensaje_whatsapp: mensaje no reconocido")
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
    
    print("saliendo de obtener_Mensaje_whatsapp")
    return text

def enviar_Mensaje_whatsapp(data):
    print("ingresando a enviar_Mensaje_whatsapp")
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)

        if response.status_code == 200:
            print("saliendo de enviar_Mensaje_whatsapp: mensaje enviado")
            return 'mensaje enviado', 200
        else:
            print("saliendo de enviar_Mensaje_whatsapp: error al enviar mensaje")
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        print("saliendo de enviar_Mensaje_whatsapp: error exception 403 " + str(e))
        return e, 403
    
def text_Message(number,text):
    print("ingresando a text_Message")
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

    print("saliendo de text_Message")
    return data

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    print("ingresando a replace_start")
    if s.startswith("521"):
        print("saliendo de replace_start: 521 to ...")
        return "52" + s[3:]
    else:
        print("saliendo de replace_start")
        return s

######################################################################################
# AGREGANDO LAS FUNCIONES PARA CHATGPT
######################################################################################
openai.api_key = sett.openai_api

def get_lista_para_contexto(df):
    print("ingresando a get_lista_para_contexto")
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

    print("saliendo de get_lista_para_contexto")
    
    return lista_detalle

def generar_respuesta_chatgpt(user_message, number, espedido=False):
    #################################################################################
    ## carga del archivo de configuracion
    #################################################################################
    print("ingresando a generar_respuesta_chatgpt")
    ruta_archivo = "confugracion_2.xlsx"
    # Leer el archivo Excel con dos hojas
    try:
        xls = pd.ExcelFile(ruta_archivo)
    except Exception as e:
        print('saliendo de  generar_respuesta_chatgpt: error pd.excelfile exception ' + str(e))
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
        print('saliendo de  generar_respuesta_chatgpt: error no lee la estructura de configuracion exception ' + str(e))
        return 'no enviado'
    
    messages = [{'role':'system', 'content':lista_estructura_contexto}]

    historial = get_chat_from_csv(number)
    
    # 2023-07-30 21:06 (jorge eduardo vicente hernández): si hay historial lo añade
    ######
    if len(historial) > 0:
        messages.extend(historial)
    ######
    
    messages.append({'role': 'user', 'content': user_message})
    
    if espedido:
      print('generar_respuesta_chatgpt el cliente dio conforme!!')
      messages.append(
                        {'role':'system', 'content':'En base a lo que el usuario (que su número celular es ' + str(number) + ') este pidiendo mayor información, \
                        categorizalo como cata, cursos de cata o viajes.  \
                        cálcula el precio total del servicio y considera si te a pedido descuento. \
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
        print('saliendo de  generar_respuesta_chatgpt: error no conecta a chatgpt exception ' + str(e))
        return 'no enviado'

    print("saliendo de generar_respuesta_chatgpt")

    return response.choices[0].message["content"]

def text_Message_al_gerente(number, diccionarioConforme):
    print("ingresando a text_Message_al_gerente")
    
    diccionarioConforme = diccionarioConforme.replace('\n', '').replace(' ', '')
    diccionarioConforme = json.loads(str(diccionarioConforme))

    #print('Imprimiento diccionario y clave')
    #for clave, valor in diccionarioConforme.items():
    #   print(clave, valor)

    text = 'Hola Victor, el cliente ' + str(diccionarioConforme['nombrecompleto']) + ' ' \
           'con celular ' + str(diccionarioConforme['celular']) + ' y correo ' + str(diccionarioConforme['correo']) + ' ' \
           'a solicitado un ' + str(diccionarioConforme['categoria']) + ' con el detalle de ' + str(diccionarioConforme['servicio']) + ' ' \
           'y precio total: ' + str(diccionarioConforme['precio']) + '.'
    
    #text = 'hola claudia...'
    
    data = text_Message(str(number),text)

    print("saliendo de text_Message_al_gerente")

    return data

def guardar_conversacion(conversation_id, number, name, user_msg,timestamp, bot_msg=''):
    
    print("ingresando a guardar_conversacion")
    
    try:
      conversations = []
      
      cabeceras = ['messageId', 'number', 'name', 'user_msg', 'bot_msg', 'timestamp']
      conversation = [conversation_id, number, name, user_msg, bot_msg, datetime.fromtimestamp(timestamp)]
      
      # Guardar las conversaciones en el archivo CSV
      # 2023-07-30 21:06 (jorge eduardo vicente hernández): que guarde archivos por número de usuario
      #with open('conversaciones.csv', 'a', newline='') as csv_file:
      #    print('guardar conversacion')
      #####
      filename_conversaciones = 'conversaciones' + '_' + str(number) + '.csv'

      # verificamos si existe el archivo
      existe_archivo = os.path.exists(filename_conversaciones)

      with open(filename_conversaciones, 'a', newline='') as csv_file:
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
      
      print("saliendo de guardar_conversacion: " + str(messages))
    except Exception as e:
        print('saliendo de guardar_conversacion: error ' + str(e))
        return e, 403
    
def get_chat_from_csv(number):
    print("ingresando a get_chat_from_csv")
    
    messages = []
    
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
    except Exception as e:
        print("saliendo de get_chat_from_csv: error " + str(e))
    ######
    
    print("saliendo de get_chat_from_csv")
    return messages

def guardar_pedido(jsonPedido, number):
    print("ingresando a guardar_pedido")
    # Eliminar el texto que sigue al JSON
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
    
    print("saliendo de guardar_pedido")