import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler
from telegram.ext import Application, filters
from YT import get_song_link as get_yt_song_link, get_song_info_from_url as get_yt_song_info
from Yandex import get_song_link as get_yandex_song_link, get_song_info_from_url as get_yandex_song_info
# from audio_utils import get_raw_file as get_raw_file

SETTINGS_FILE = 'settings.json'

def load_preferences():
    try:
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_preferences(preferences):
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(preferences, file, indent=4)

# Load user preferences at startup
user_preferences = load_preferences()

async def settings(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    preferences = user_preferences.get(user_id, ['yt', 'yandex'])

    # Create inline keyboard buttons
    buttons = [
        InlineKeyboardButton(
            text=f"✅ YouTube" if 'yt' in preferences else "❌ YouTube",
            callback_data=f"toggle_yt"
        ),
        InlineKeyboardButton(
            text=f"✅ Yandex" if 'yandex' in preferences else "❌ Yandex",
            callback_data=f"toggle_yandex"
        ),
        InlineKeyboardButton(
            text=f"✅ Raw MP3" if 'raw' in preferences else "❌ Raw MP3",
            callback_data=f"toggle_raw"
        )
    ]

    reply_markup = InlineKeyboardMarkup.from_column(buttons)
    await update.message.reply_text("Choose services:", reply_markup=reply_markup)

async def toggle_service(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = str(query.from_user.id)
    preferences = user_preferences.get(user_id, ['yt', 'yandex', 'raw'])

    # Determine which service to toggle
    if query.data == "toggle_yt":
        if 'yt' in preferences:
            preferences.remove('yt')
        else:
            preferences.append('yt')
    elif query.data == "toggle_yandex":
        if 'yandex' in preferences:
            preferences.remove('yandex')
        else:
            preferences.append('yandex')
    elif query.data == "toggle_raw":
        if 'raw' in preferences:
            preferences.remove('raw')
        else:
            preferences.append('raw')

    # Update preferences and save to file
    user_preferences[user_id] = preferences
    save_preferences(user_preferences)

    # Update the button text
    buttons = [
        InlineKeyboardButton(
            text=f"✅ YouTube" if 'yt' in preferences else "❌ YouTube",
            callback_data=f"toggle_yt"
        ),
        InlineKeyboardButton(
            text=f"✅ Yandex" if 'yandex' in preferences else "❌ Yandex",
            callback_data=f"toggle_yandex"
        ),
        InlineKeyboardButton(
            text=f"✅ Raw MP3" if 'raw' in preferences else "❌ Raw MP3",
            callback_data=f"toggle_raw"
        )
    ]

    reply_markup = InlineKeyboardMarkup.from_column(buttons)
    await query.edit_message_text("Choose services:", reply_markup=reply_markup)

async def find(update: Update, context: CallbackContext) -> None:
    # Check if the user provided a search query
    if not context.args:
        # Set waiting state and ask for song
        context.user_data['waiting_for_song'] = True
        await update.message.reply_text('Waiting for the song...')
        return

    # Process the search query
    await process_search(update, context, ' '.join(context.args))

async def process_search(update: Update, context: CallbackContext, search_query: str) -> None:
    user_id = str(update.effective_user.id)
    preferences = user_preferences.get(user_id, ['yt', 'yandex', 'raw'])

    # Check if input is a URL
    is_url = search_query.startswith(('http://', 'https://'))
    
    response = []
    
    # If the input is a URL, extract song info first
    if is_url:
        song_info = None
        song_name = None
        
        try:
            # Determine URL type and get song info
            if 'music.youtube.com' in search_query or 'youtube.com' in search_query:
                song_info = get_yt_song_info(search_query)
            elif 'music.yandex.ru' in search_query:
                song_info = get_yandex_song_info(search_query)
                
            # Check if we got a valid response
            if isinstance(song_info, dict) and 'title' in song_info and 'artist' in song_info:
                song_name = f"{song_info['artist']} - {song_info['title']}"
                response.append(f"🎵 Found: {song_name}")
                search_query = song_name  # Use the extracted song name for other services
            else:
                response.append(f"❌ Could not extract song info: {song_info}")
                # Return early if we couldn't extract song info
                await update.message.reply_text("\n".join(response), disable_web_page_preview=True)
                return
        except Exception as e:
            response.append(f"❌ Error extracting song info: {str(e)}")
            await update.message.reply_text("\n".join(response), disable_web_page_preview=True)
            return
    
    # Get links from preferred services
    if 'yt' in preferences:
        try:
            yt_link = get_yt_song_link(search_query)
            response.append(f"YouTube: {yt_link}")
        except Exception as e:
            response.append(f"YouTube: Error - {str(e)}")
    
    if 'yandex' in preferences:
        try:
            yandex_link = get_yandex_song_link(search_query)
            response.append(f"Yandex: {yandex_link}")
        except Exception as e:
            error_msg = str(e)
            if "451" in error_msg or "Unavailable For Legal Reasons" in error_msg:
                response.append("Yandex: Service unavailable in your region due to legal restrictions")
            else:
                response.append(f"Yandex: Error - {error_msg}")
    
    # if 'raw' in preferences:
    #     if not yt_link:
    #         response.append("No results found for raw MP3.")
    #     else:
    #         # raw_file = get_raw_file(yt_link)
    #         await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(raw_file, 'rb'), caption="Here is your MP3 file!")
    #         os.remove(raw_file)

    if not response:
        response = ["No services selected."]
    
    await update.message.reply_text("\n".join(response), disable_web_page_preview=True)

async def handle_message(update: Update, context: CallbackContext) -> None:
    # Check if we're waiting for a song
    if context.user_data.get('waiting_for_song', False):
        context.user_data['waiting_for_song'] = False
        await process_search(update, context, update.message.text)
    else:
        # Handle regular messages (if needed)
        pass

def main():
    # Read the token from the TOKEN file
    with open('TOKEN', 'r') as file:
        token = file.read().strip()

    # Create the Application and pass it your bot's token
    application = Application.builder().token(token).build()

    # Register the /settings command handler
    application.add_handler(CommandHandler("settings", settings))

    # Register the callback query handler for toggling services
    application.add_handler(CallbackQueryHandler(toggle_service))

    # Register the /find command handler directly with the application
    application.add_handler(CommandHandler("find", find))

    # Register the message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()
  
if __name__ == '__main__':
    main()




