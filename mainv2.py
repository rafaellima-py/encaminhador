import re
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMediaVideo, InputMediaPhoto, InlineKeyboardMarkup
from decouple import config
import asyncio

grupo = -1002091660933
canal = -1002199418795
admin_user = 673195223
media = {}
media_caption = {}  # Dicionário para armazenar a legenda
timeouts = {}
grupo_teste = -1001807528178
canal_teste = -1001790437275

token = '7341883421:AAFStSS4SwG3hhqJbVMsnGRXqsONL1TNzmQ'
bot = AsyncTeleBot(token)

# Função para limpar entities da legenda
def clean_caption(message):
    if not message.caption:
        return "@SecretinhoOficial"

    # Obtém apenas o texto puro, ignorando formatação e links embutidos
    caption = message.caption
    if 'nuds_link' in caption:
        caption = caption.replace('nuds_link', '')
    if 'nuds.link' in caption:
        caption = caption.replace('nuds.link', '')
    if message.entities:  # Se houver entities, removemos
        for entity in reversed(message.entities):  # Reverso para evitar erro ao modificar string
            caption = caption[:entity.offset] + caption[entity.offset + entity.length:]
            
    # Remove @nomes de usuários (@qualquer_coisa)
    caption = re.sub(r"@\S+", "", caption)

    # Remove links diretos (http, https, t.me/)
    caption = re.sub(r"https?:\/\/\S+", "", caption)

    # Remove espaços extras antes e depois
    caption = caption.strip()

    if 'nuds_link' in caption:
        caption = caption.replace('nuds_link', '')
        
    # Se a legenda ficar vazia depois da limpeza, define apenas @SecretinhoOficial
    return caption + " @SecretinhoOficial" if caption else "@SecretinhoOficial"


@bot.message_handler(commands=['start'])
async def start(message):
    await bot.reply_to(message, 'O bot está ativo')


@bot.message_handler(content_types=['video', 'photo'])
async def handle_media(message):
    global media, timeouts, media_caption
    
    media_group_id = message.media_group_id or 'single_' + str(message.message_id)

    if message.from_user.id == admin_user:
        try:
            if media_group_id not in media:
                media[media_group_id] = []
                media_caption[media_group_id] = ""

            # Captura a legenda e limpa as entities
            media_caption[media_group_id] = clean_caption(message)

            # Adiciona mídia ao álbum
            if message.content_type == 'video':
                if not media[media_group_id]:
                    media[media_group_id].append(InputMediaVideo(message.video.file_id, caption=media_caption[media_group_id]))
                else:
                    media[media_group_id].append(InputMediaVideo(message.video.file_id))
            elif message.content_type == 'photo':
                if not media[media_group_id]:
                    media[media_group_id].append(InputMediaPhoto(message.photo[-1].file_id, caption=media_caption[media_group_id]))
                else:
                    media[media_group_id].append(InputMediaPhoto(message.photo[-1].file_id))

            if media_group_id in timeouts:
                timeouts[media_group_id].cancel()

            timeouts[media_group_id] = asyncio.get_event_loop().call_later(2, asyncio.create_task, send_album(media_group_id))

        except Exception as e:
            await bot.send_message(message.chat.id, str(e))
            print(e)


async def send_album(media_group_id):
    global media, timeouts, media_caption

    markup = InlineKeyboardMarkup()

    if len(media[media_group_id]) == 1:
        item = media[media_group_id][0]
        if isinstance(item, InputMediaVideo):
            await bot.send_video(
                chat_id=canal,
                video=item.media,
                caption=media_caption[media_group_id],
                reply_markup=markup
            )
        elif isinstance(item, InputMediaPhoto):
            await bot.send_photo(
                chat_id=canal,
                photo=item.media,
                caption=media_caption[media_group_id],
                reply_markup=markup
            )
    elif len(media[media_group_id]) > 0:
        try:
            media[media_group_id][0].caption = media_caption[media_group_id]
            await bot.send_media_group(canal, media[media_group_id])
            
            media.pop(media_group_id)
            media_caption.pop(media_group_id)
            timeouts.pop(media_group_id)
        except Exception as e:
            print(f"Erro ao enviar o álbum: {e}")


async def main():
    try:
        await bot.polling(none_stop=True)
    except Exception as e:
        print(e)

asyncio.run(main())
