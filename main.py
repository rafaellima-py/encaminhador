# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "aiofiles",
#     "aiohttp",
#     "python-decouple",
#     "telegrambotapi",
# ]
# ///
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMediaVideo, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from decouple import config
import asyncio
grupo = -1002091660933
canal = -1002199418795
admin_user = 673195223
media = {}
timeouts = {}
enviado = False
grupo_teste = -1001807528178
canal_teste = -1001790437275

token = '7341883421:AAFStSS4SwG3hhqJbVMsnGRXqsONL1TNzmQ'
bot = AsyncTeleBot(token)


# Handler para iniciar o bot
@bot.message_handler(commands=['start'])
async def start(message):
    await bot.reply_to(message, 'O bot está ativo')

# Handler para álbuns de mídia (media groups)
@bot.message_handler(content_types=['video', 'photo'])
async def handle_media(message):
    global media, timeouts
    
    # Identifica o grupo de mídia (álbum) usando media_group_id
    media_group_id = message.media_group_id
    
    # Se não houver media_group_id, trata como uma mídia isolada
    if media_group_id is None:
        media_group_id = 'single_' + str(message.message_id)  # Usa o ID da mensagem para identificar um único item

    # Se é o administrador que está enviando
    if message.from_user.id == admin_user:
        try:
            # Inicializa uma nova lista para o álbum, se não existir
            if media_group_id not in media:
                media[media_group_id] = []

            # Adiciona vídeos ao álbum
            if message.content_type == 'video':
                # Adiciona legenda apenas ao primeiro vídeo
                if not media[media_group_id]:  # Se for o primeiro item
                    media[media_group_id].append(InputMediaVideo(message.video.file_id, caption="@SecretinhoOficial"))
                else:
                    media[media_group_id].append(InputMediaVideo(message.video.file_id))

            # Adiciona fotos ao álbum
            elif message.content_type == 'photo':
                # Adiciona legenda apenas à primeira foto
                if not media[media_group_id]:  # Se for o primeiro item
                    media[media_group_id].append(InputMediaPhoto(message.photo[-1].file_id, caption="@SecretinhoOficial"))
                else:
                    media[media_group_id].append(InputMediaPhoto(message.photo[-1].file_id))

            # Limpa o timeout anterior para evitar múltiplos envios
            if media_group_id in timeouts:
                timeouts[media_group_id].cancel()

            # Define um novo timeout para enviar o álbum após 2 segundos sem novas mídias
            timeouts[media_group_id] = asyncio.get_event_loop().call_later(2, asyncio.create_task, send_album(media_group_id))

        except Exception as e:
            await bot.send_message(message.chat.id, str(e))
            print(e)


# Função para enviar o álbum
async def send_album(media_group_id):
    global media, timeouts
    markup = InlineKeyboardMarkup()
    keyboard = InlineKeyboardMarkup()

    
    # Adiciona botões (customize os textos, emojis e URLs) ainda nao sera usado
    #keyboard.add(InlineKeyboardButton("📂 Exemplo de Link 1 📂", url="https://mega.nz"))
    #keyboard.add(InlineKeyboardButton("✨ Exemplo de Link 2✨", url="https://mega.nz"))
    #keyboard.add(InlineKeyboardButton("Exemplo de Link 3 👊", url="https://example.com"))

    if len(media[media_group_id]) == 1:
        # Itera sobre o álbum para identificar o tipo de mídia
        for item in media[media_group_id]:
            if isinstance(item, InputMediaVideo):
                # Extrai o file_id e envia o vídeo com legenda
                await bot.send_video(
                    chat_id=canal_teste,
                    video=item.media,  # Extrai o file_id do objeto InputMediaVideo
                    caption="Teste",
                    reply_markup=keyboard
                )
            elif isinstance(item, InputMediaPhoto):
                # Extrai o file_id e envia a foto com legenda
                await bot.send_photo(
                    chat_id=canal_teste,
                    photo=item.media,  # Extrai o file_id do objeto InputMediaPhoto
                    caption="Teste",
                    reply_markup=keyboard
                )
    elif len(media[media_group_id]) > 0:
        try:
            # Envia o álbum
            await bot.send_media_group(canal_teste, media[media_group_id])
            print(f"Enviando álbum: {media[media_group_id]}")
            
            # Limpa o grupo de mídias enviado e remove o timeout
            media.pop(media_group_id)
            timeouts.pop(media_group_id)
        except Exception as e:
            print(f"Erro ao enviar o álbum: {e}")

async def main():
    try:
        await bot.polling(none_stop=True)
    except Exception as e:
        print(e)

asyncio.run(main())
