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
        if 'es todo' in text:
            print('es todo')
            services.guardar_conversacion(messageId, number, name, text, timestamp, 'pedido realizado')
            jsonPedido = services.generar_respuesta_chatgpt(text, number, True)
            print('1jsonPedido',jsonPedido)
            services.guardar_pedido(jsonPedido, number)
            data = services.text_Message(number,'Pedido Confirmado, gracias!')
        else:
            print('recolecta pedido')
            respuestabot = services.generar_respuesta_chatgpt(text, number, False)
            print('recolecta pedido 2')
            #services.guardar_conversacion(messageId, number, name, text, timestamp, respuestabot)
            print('recolecta pedido 3')
            data = services.text_Message(number,respuestabot)

        print('data', data)
        services.enviar_Mensaje_whatsapp(data)
        ######################################################
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run(debug=True)         