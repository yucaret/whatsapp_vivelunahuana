from flask import Flask, request
import sett 
import services

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    app.logger.info('Bienvenido')
    app.logger.info(sett.token)
    app.logger.info(sett.whatsapp_token)
    app.logger.info(sett.whatsapp_url)

    return 'Hola mundo vivelunahuana, desde Flask'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            app.logger.info('Token correcto')
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
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
            print('>>>>>>>>>>>>>>>> conforme >>>>>>>>>>>>>>>>>>')
            services.guardar_conversacion(messageId, number, name, text, timestamp, 'conformidad')

            # 2023-07-30 21:06 (jorge eduardo vicente hernández): renombre de variable
            #jsonPedido = services.generar_respuesta_chatgpt(text, number, True)
            #print('1jsonPedido',jsonPedido)
            diccionarioConforme = services.generar_respuesta_chatgpt(text, number, True)
            print('diccionarioConforme: ', str(diccionarioConforme))

            # 2023-07-30 21:06 (jorge eduardo vicente hernández): se envia mensaje al gerente
            #services.guardar_pedido(jsonPedido, number)
            #data = services.text_Message(number,'Pedido Confirmado, gracias!')
            print('telefono del gerente: ' + str(sett.celular_gerente))
            dataGerente = services.text_Message_al_gerente(sett.celular_gerente, diccionarioConforme)
            print('recibe data de gerente ', dataGerente)
            respuesta = services.enviar_Mensaje_whatsapp(dataGerente)
            print('se envia data de gerente: ' + str(respuesta))

            data = services.text_Message(number,'Gracias en breve se comunicarán contigo!!!')
            print('se genera data de conforme')
        else:
            print('>>>>>>>>>>>>>>>> sigue conversando >>>>>>>>>>>>>>>>>>')
            respuestabot = services.generar_respuesta_chatgpt(text, number, False)
            print('recibe respuesta de bot')
            services.guardar_conversacion(messageId, number, name, text, timestamp, respuestabot)
            print('guarda conversacion')
            data = services.text_Message(number,respuestabot)
            print('se genera la data de conversacion')

        respuesta = services.enviar_Mensaje_whatsapp(data)
        print('se envia mensaje con data de conversacion: ' + str(respuesta))
        ######################################################
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run(debug=True)