from os import getenv
from dotenv import load_dotenv
from pyrogram import Client, filters  
from pyrogram.types import ForceReply
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup
)

from dotenv import load_dotenv
from os import getenv
from uvloop import install

load_dotenv()
install()

CHAT_ID = getenv('CHAT_ID'),

app = Client(
    'GeekTipsBot',
    api_id=getenv('TELEGRAM_API_ID'),
    api_hash=getenv('TELEGRAM_API_HASH'),
    bot_token=getenv('TELEGRAM_BOT_TOKEN')
)


ALLOWED_USERS = ['leonan0', 'Leandr0Caetan0', 'JoaoAngelo11']

RED = '\n❌❌❌❌❌❌❌❌❌\n❌❌❌❌❌❌❌❌❌\n❌❌❌❌❌❌❌❌❌\n'

GREEN = ' ✅✅✅✅✅✅✅✅✅✅\n✅✅✅✅✅✅✅✅✅✅✅✅✅\n✅✅✅✅✅✅✅✅✅✅✅✅✅\n'

MERCADOS = {
    "ambas": "AMBAS MARCAM ⚽⚽",
    "ambas nao": "AMBAS NÃO MARCAM ⚽❌",
    "casa": "CASA VENCE 🏠✅",
    "over": "OVER 2.5 ⚽➕"

}


def validate_user(message):
    if message.from_user.username in ALLOWED_USERS:
        return True
    else:
        return False


def set_message(campeonato, minutagem, mercado):
    minutos = 1
    try:
        campeonato = campeonato.upper()
        minutos = [str(minutagem).rjust(2, '0'), str(minutagem+3 if minutagem+3 <= 59 else minutagem+3 -
                                                     60).rjust(2, '0'), str(minutagem+6 if minutagem+6 <= 59 else minutagem+6 - 60).rjust(2, '0')]
        mercado = MERCADOS[mercado]
        message = ''
        message_layout = ["✅⚽ Geek Tips - Virtual ✅⚽\n",
                          "\n",
                          f"❇️ {campeonato} ❇️\n",
                          "\n",
                          "⏳Minutos⏳\n"
                          "\n",
                          f"🕒 {minutos[0]} / {minutos[1]} / {minutos[2]}\n",
                          "\n",
                          "ENTRADA:",
                          f"{mercado}\n",
                          "\n",
                          "Stakes: 1 % -> 2 % -> 4 % da Banca\n",
                          "\n",
                          "https://www.bet365.com/#/AVR/B146/R^1/\n",
                          "\n",
                          "⚠️⚠️ NUNCA FUJA DA GESTÃO!!! ⚠️⚠️"
                          ]
        for i in message_layout:
            message += i
    except Exception as ex:
        message = f"ERROR -> {ex}"
    return message, minutos


def get_message_result(message, result, minutagem, odd):
    lista = message.text.split('\n')
    if result == "GREEN":
        texto = lista[6].replace(minutagem, minutagem + " ✅")
    else:
        texto = lista[6].replace('/', "/")

    lista.pop(6)

    lista.insert(6, texto)

    lista.insert(8, f"ODD @{odd}{GREEN}" if result == 'GREEN' else RED)

    message_to_send = ''

    for i in lista:
        if i == '':
            message_to_send += '\n'
        else:
            message_to_send += i+'\n'

    return message_to_send


def log(message):
    print(f"""username -> {message.from_user.username if message.from_user else None},\nuser.id -> {message.from_user.id if message.from_user else None},\nchat.id -> {message.chat.id},\ncommand -> {message.command}""")


@app.on_message(filters.command('post'))
async def post(client, message):
    log(message)
    if validate_user(message):
        camp, min, mercado = message.command[1].split(',')
        message_to_rpl, minutos = set_message(camp, int(min), mercado)

        keys = [InlineKeyboardButton(
            'RED', callback_data=f"RED")]
        for a in minutos:
            keys.append(InlineKeyboardButton(
                'GREEN on '+str(a), callback_data=f'GREEN,{a}'),)

        inline_markup = InlineKeyboardMarkup(
            [
                keys
            ]
        )

        await message.reply(message_to_rpl, reply_markup=inline_markup)


@app.on_message(filters.command('mercados'))
async def get_mercados(client, message):
    log(message)

    message_r = ''
    for m in MERCADOS.keys():
        message_r += f'{m} -> {MERCADOS[m]}\n'

    await message.reply(message_r)


@app.on_message(filters.command('start'))
async def start(client, message):
    log(message)

    print(message)
    await message.reply('Bem vindo!')


@app.on_message(filters.regex('green*') | filters.regex('red'))
async def edit_message_text(client, message):
    log(message)

    result, message_id, mins, odd = message.text.split(',')
    message_id = int(message_id)
    message_to_edit = await app.get_messages(CHAT_ID, message_id)
    message_new = get_message_result(message_to_edit, result, mins, odd)
    message_new_t = ''
    for x in message_new:

        if x == '':
            message_new_t += '\n'
        else:
            message_new_t += x
            message_new_t += '\n'

    await app.edit_message_text(CHAT_ID, message_id, message_new_t)


@app.on_callback_query()
async def callback(client, callback_query):
    r = callback_query.data.split(',')
    if r[0] == 'RED':
        pass
    else:
        h = await callback_query.message.reply_text(f"Qual a ODD? | {r[0]},{r[1]}", reply_to_message_id=callback_query.message.id, reply_markup=ForceReply())
        print(h.id)


@app.on_message(filters.reply)
async def testes(client, message):
    odd = message.text

    odd_question = message.reply_to_message
    x = message.reply_to_message.text.split('| ')[1].split(',')
    x.append(odd)
    tip_message = await app.get_messages(message.chat.id, odd_question.reply_to_message_id)
    edited_message = get_message_result(tip_message, x[0], x[1], x[2])
    await app.edit_message_text(tip_message.chat.id, tip_message.id, edited_message)


print('running!!!')
app.run()
