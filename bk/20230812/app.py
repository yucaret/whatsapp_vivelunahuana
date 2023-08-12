from flask import Flask, request
import sett 
import services

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    app.logger.info('Bienvenido a gepeto')
    app.logger.info(sett.token)
    app.logger.info(sett.whatsapp_token)
    app.logger.info(sett.whatsapp_url)

    return 'Hola mundo vivelunahuana, desde Flask'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    print("ingresando a verificar_token")
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            app.logger.info('Token correcto')
            print("saliendo de verificar_token: token correcto")
            return challenge
        else:
            print("saliendo de verificar_token: token incorrecto")
            return 'token incorrecto', 403
    except Exception as e:
        print("error en verificar_token: " + str(e))
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    print("ingresando a recibir_mensajes")
    try: 
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = services.replace_start(message['from'])
        messageId = message['id']
        timestamp = int(message['timestamp'])
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)
        #services.administrar_chatbot(text, number,messageId,name)
        app.logger.info('Mensaje usuari:{}'.format(text))


        ###################################################
        # Agregando chatgpt mensaje
        ###################################################
        # 2023-07-30 21:06 (jorge eduardo vicente hernández): con la palabra conforme ingresa
        #if 'es todo' in text:
        #    print('es todo')
        #    services.guardar_conversacion(messageId, number, name, text, timestamp, 'pedido realizado')
        if 'conforme' in str.lower(text):
            services.guardar_conversacion(messageId, number, name, text, timestamp, 'conformidad')

            # 2023-07-30 21:06 (jorge eduardo vicente hernández): renombre de variable
            #jsonPedido = services.generar_respuesta_chatgpt(text, number, True)
            #print('1jsonPedido',jsonPedido)
            diccionarioConforme = services.generar_respuesta_chatgpt(text, number, True)
            
            # 2023-07-30 21:06 (jorge eduardo vicente hernández): se envia mensaje al gerente
            #services.guardar_pedido(jsonPedido, number)
            #data = services.text_Message(number,'Pedido Confirmado, gracias!')
            dataGerente = services.text_Message_al_gerente(sett.celular_gerente, diccionarioConforme)
            respuesta = services.enviar_Mensaje_whatsapp(dataGerente)
            
            data = services.text_Message(number,'Gracias en breve se comunicarán contigo!!!')
        else:
            respuestabot = services.generar_respuesta_chatgpt(text, number, False)
            services.guardar_conversacion(messageId, number, name, text, timestamp, respuestabot)
            data = services.text_Message(number,respuestabot)
            
        respuesta = services.enviar_Mensaje_whatsapp(data)

        print("saliendo de recibir_mensajes: " + str(respuesta))
        ######################################################
        return 'enviado'

    except Exception as e:
        print("error en recibir_mensajes: " + str(e))
        return 'no enviado '

if __name__ == '__main__':
    app.run(debug=True)