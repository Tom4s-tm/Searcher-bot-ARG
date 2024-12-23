import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# URL de la solicitud
url = "https://informes.nosis.com/Home/Buscar"

# Encabezados necesarios
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"  # Indica que el contenido es formulario
}

# Función para hacer la solicitud de búsqueda
async def realizar_busqueda(query: str):
    payload = {
        "Texto": query,
        "Tipo": "-1",
        "EdadDesde": "-1",
        "EdadHasta": "-1",
        "IdProvincia": "-1",
        "Localidad": "",
        "recaptcha_response_field": "enganio al captcha",  # Esto debe ser resuelto correctamente
        "recaptcha_challenge_field": "enganio al captcha",  # Esto debe ser resuelto correctamente
        "encodedResponse": ""
    }

    try:
        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        # Verificar el código de estado
        if response.status_code == 200:
            try:
                response_json = response.json()
                if response_json.get("HayError", False):
                    return "Se reportó un error en la solicitud."
                elif response_json.get("EntidadesEncontradas"):
                    entidades_info = ""
                    for entidad in response_json["EntidadesEncontradas"]:
                        # Ahora no se incluyen las URLs ni el Mensaje Habeas Data
                        entidades_info += f"Documento: {entidad['Documento']}\n"
                        entidades_info += f"Razón Social: {entidad['RazonSocial']}\n"
                        entidades_info += f"Actividad: {entidad['Actividad']}\n"
                        entidades_info += f"Provincia: {entidad['Provincia']}\n"
                        entidades_info += "-" * 40 + "\n"
                    return entidades_info
                else:
                    return "No se encontraron entidades."
            except ValueError:
                return "La respuesta no está en formato JSON."
        else:
            return f"Error en la solicitud: {response.status_code}"

    except requests.RequestException as e:
        return f"Error en la solicitud: {e}"

# Comando de inicio
async def buscar(update: Update, context: CallbackContext):
    print("Comando /busqueda recibido")  # Mensaje de depuración
    await update.message.reply_text("¡Hola! ¿Quien quieres buscar?")

# Comando para buscar basado en el texto ingresado
async def search(update: Update, context: CallbackContext):
    print(f"Mensaje recibido: {update.message.text}")  # Mensaje de depuración

    # Verificar si hay argumentos (palabras después del comando)
    query = " ".join(context.args) if context.args else update.message.text

    if query:
        resultado = await realizar_busqueda(query)
        await update.message.reply_text(resultado)
    else:
        await update.message.reply_text("Por favor, ingresa quien quieres buscar.")

# Función principal para inicializar el bot
def main():
    print("Iniciando bot...")  # Mensaje de depuración
    application = Application.builder().token("TOKEN DEL BOT").build()

    application.add_handler(CommandHandler("buscar", buscar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

    application.run_polling()

if __name__ == "__main__":
    main()
