import requests
from src.config.config import Configurations
import json
from src.utils.LogsPrint import printLog

# https://telegram-bot-sdk.readme.io/reference/sendmessage


def sendTelegramMessage(*parameters):
    printLog(*parameters)
    if not (Configurations.isProd() or Configurations.isStaging()):
        return
    try:
        if not parameters:
            return

        text = "TelegramBot " + Configurations.BASE_URL + "\n"

        for p in parameters:
            if not isinstance(p, str):
                if isinstance(p, dict) or isinstance(p, list) or isinstance(p, tuple):
                    p = json.dumps(p, indent=2, separators=(',', ': '))
                else:
                    p = p.__str__()
            text += p

        chat_id = -491368163
        telegramMsgSize = 4096

        bigMessage = None
        if len(text) > telegramMsgSize:
            bigMessage = text
            text = text[:telegramMsgSize]

        reply_to_message_id = sendTelegramMessageText(chat_id, text)
        if bigMessage:
            sendTelegramMessageFile(chat_id, "👆👆👆", bigMessage, reply_to_message_id)
    except Exception as e:
        printLog("ERROR sendTelegramMessage", e)


def sendTelegramMessageText(chat_id: int, text: str, reply_to_message_id=None, default=None):
    telegramMsgSize = 4096
    if len(text) > telegramMsgSize:
        payload = {
            "text": text[:telegramMsgSize],
            "chat_id": chat_id,
            "reply_to_message_id": reply_to_message_id
        }
    else:
        payload = {
            "text": text,
            "chat_id": chat_id,
            "reply_to_message_id": reply_to_message_id
        }

    response = requests.post("https://api.telegram.org/bot{}/sendMessage"
                             .format("1919318351:AAGSLE_ootbLpaOPgwU0Enuyl3d3wpzc9kI"), payload)

    message_id = None
    if response.ok:
        responseJson = response.json()
        result = responseJson.get("result", None)
        if result:
            message_id = result.get("message_id", None)
    else:
        return default
    return message_id


def sendTelegramMessageFile(chat_id: int, text: str, fileContent: str, reply_to_message_id=None, default=None):
    maxSize = 1024
    if len(text) < maxSize:
        fileContent = text[maxSize:] + fileContent
        text = text[: maxSize]
    payload = {
        "caption": text,
        "reply_to_message_id": reply_to_message_id,
        "chat_id": chat_id
    }
    response = requests.post("https://api.telegram.org/bot{}/sendDocument"
                             .format("1919318351:AAGSLE_ootbLpaOPgwU0Enuyl3d3wpzc9kI"),
                             params=payload, files={"document": ("context.txt", fileContent.encode())})
    message_id = None
    if response.ok:
        responseJson = response.json()
        result = responseJson.get("result", None)
        if result:
            message_id = result.get("message_id", None)
    else:
        return default
    return message_id

def sendStructuredTelegramMessage(chat_id: int, title: str, fields: dict, footer: str = None, reply_to_message_id=None, default=None):
    def escape_markdown(text):
        # Escapa caracteres especiales de Markdown v2 de Telegram
        for ch in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            text = text.replace(ch, f'\\{ch}')
        return text

    message_lines = []
    if title:
        message_lines.append(f"*{escape_markdown(title)}*")
        message_lines.append("")  # Línea en blanco

    for key, value in fields.items():
        message_lines.append(f"*{escape_markdown(str(key))}:* {escape_markdown(str(value))}")

    if footer:
        message_lines.append("")
        message_lines.append(f"_{escape_markdown(footer)}_")

    text = "\n".join(message_lines)

    payload = {
        "text": text,
        "chat_id": chat_id,
        "parse_mode": "MarkdownV2",
        "reply_to_message_id": reply_to_message_id
    }

    response = requests.post(
        "https://api.telegram.org/bot{}/sendMessage".format("1919318351:AAGSLE_ootbLpaOPgwU0Enuyl3d3wpzc9kI"),
        data=payload
    )

    message_id = None
    if response.ok:
        responseJson = response.json()
        result = responseJson.get("result", None)
        if result:
            message_id = result.get("message_id", None)
    else:
        return default
    return message_id
