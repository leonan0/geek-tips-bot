# ls bot.py | entr -r python bot.py
from os import getenv
from uvloop import install
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup
)

app = Client(
    'GeekTipsBot',
    api_id=getenv('TELEGRAM_API_ID'),
    api_hash=getenv('TELEGRAM_API_HASH'),
    bot_token=getenv('TELEGRAM_BOT_TOKEN')
)

install()

CHAT_ID = getenv('CHAT_ID')

RED = '\n❌❌❌❌❌❌❌❌❌\n❌❌❌❌❌❌❌❌❌\n❌❌❌❌❌❌❌❌❌\n'

GREEN = ' ✅✅✅✅✅✅✅✅✅✅\n✅✅✅✅✅✅✅✅✅✅✅✅✅\n✅✅✅✅✅✅✅✅✅✅✅✅✅\n'

MERCADOS = {
    "ambas": "AMBAS MARCAM ⚽⚽",
    "ambas nao": "AMBAS NÃO MARCAM ⚽❌",
    "casa": "CASA VENCE 🏠✅",
    "over": "OVER 2.5 ⚽➕"

}


def set_message(campeonato, minutagem, mercado):
    minutos = 1
    try:
        campeonato = campeonato.upper()
        minutagem = int(minutagem)
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
    if result == "green":
        texto = lista[6].replace(minutagem, minutagem + " ✅")
    else:
        texto = lista[6].replace('/', "/")

    lista.pop(6)

    lista.insert(6, texto)

    lista.insert(8, f"ODD @{odd}{GREEN}" if result == 'green' else RED)

    return lista




@app.on_message(filters.command('mercados'))
async def get_mercados(client, message):
    message_r = ''
    for m in MERCADOS.keys():
        message_r += f'{m} -> {MERCADOS[m]}\n'

    await message.reply(message_r)


@app.on_message(filters.command('start'))
async def start(client, message):
    print(message)
    await message.reply('Bem vindo!')


@app.on_message(filters.regex('green*') | filters.regex('red'))
async def edit_message_text(client, message):
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
    if 'green' in callback_query.data:
        pass
    else:
        pass

    r = await callback_query.edit_message_text('Teste', reply_markup="inline_markup")


@app.on_message(filters.command('callback'))
async def callbacks(client, message):
    inline_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('green', callback_data='green'),
                InlineKeyboardButton(
                    'red', callback_data='red')
            ]
        ]
    )
    await message.reply('Escolha algo!', reply_markup=inline_markup)


@app.on_message()
async def hello(client, message: Message):
    if message.from_user.username in ['leonan0', 'Leandr0Caetan0', 'JoaoAngelo11']:
        try:
            camp, mins, entrada = message.text.split(',')
            message_reply, minutos = set_message(camp, mins, entrada)
            print(message.from_user)
            await message.reply(message_reply)
            c = await app.send_message(CHAT_ID, message_reply)
            await message.reply(str(c.id))
            keys = [InlineKeyboardButton('RED', callback_data=f"RED,{c.id}")]
            for a in minutos:
                keys.append(InlineKeyboardButton(
                    'GREEN on '+str(a), callback_data=f'green,{a},{c.id}'),)

            inline_markup = InlineKeyboardMarkup(
                [
                    keys
                ]
            )
            # await message.reply('Escolha algo!', reply_markup=inline_markup)

        except Exception as ex:
            print("Não entendi"+str(ex))
    else:
        await message.reply('Você ta sem moral')


print('running!!!')
app.run()
