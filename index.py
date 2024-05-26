import telebot
import webbrowser
from youtubesearchpython import VideosSearch
import pyautogui
import time
import threading



# Initialize the Telegram bot with your bot token
TOKEN = 'token goes here'
bot = telebot.TeleBot(TOKEN)
print("hello world")

# Queue to store songs
song_queue = []
# Flag to indicate if a song is currently playing
is_playing = False

# Function to search for a song on YouTube and return its URL
def search_song_info(song_title):
    # Search for the song title
    videosSearch = VideosSearch(song_title, limit=1)
    results = videosSearch.result()

    if results['result']:
        # Extract link and duration
        song_link = results['result'][0]['link']
        duration = results['result'][0]['duration']
        titlee = results['result'][0]['title']
        
        return song_link, duration, titlee
    else:
        return None, None

# Function to play songs from the queue
def play_next_song():
    global is_playing

    while True:
        # If there are songs in the queue and no song is currently playing
        if song_queue and not is_playing:
            song_title, chat_id = song_queue.pop(0)  # Get the first song from the queue
            is_playing = True

            # Search for the song on YouTube
            song_link, duration, titlee = search_song_info(song_title)

            if song_link:
                try:
                    # Extract the URL starting from "youtube.com"
                    start_index = song_link.find("youtube.com")
                    if start_index != -1:
                        youtube_url = song_link[start_index:]
                    else:
                        bot.send_message(chat_id, "Invalid YouTube link.")
                        is_playing = False
                        continue

                    # Open the URL using pyautogui
                    pyautogui.hotkey('ctrl', 'e')
                    pyautogui.hotkey('backspace')
                    pyautogui.typewrite(youtube_url)
                    pyautogui.press('enter')

                    # Convert duration to seconds
                    duration_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(":"))))

                    bot.send_message(chat_id, f"Playing {titlee} for {duration}")

                    # Wait for the duration of the song
                    time.sleep(duration_seconds)

                    # Mark the song as finished playing
                    is_playing = False
                except Exception as e:
                    bot.send_message(chat_id, f"An error occurred: {e}")
                    is_playing = False
            else:
                bot.send_message(chat_id, "Song not found on YouTube.")
                is_playing = False
        else:
            # If no song is in the queue or a song is currently playing, wait for a while before checking again
            time.sleep(5)

# Function to display the current queue
def display_queue(chat_id):
    queue_message = "Current queue:\n"
    for i, (song_title, _) in enumerate(song_queue, start=1):
        queue_message += f"{i}. {song_title}\n"
    bot.send_message(chat_id, queue_message)

# Start a new thread to continuously check for the next song to play
threading.Thread(target=play_next_song).start()

# Handle /play command
@bot.message_handler(commands=['play'])
def handle_play(message):
    global song_queue

    # Extract the song title from the message
    query = message.text.split(' ', 1)[1]

    # Add the song to the queue
    song_queue.append((query, message.chat.id))

    # Reply to the user that the song has been added to the queue
    bot.reply_to(message, f"Added {query} to the queue.")

# Handle /display command
@bot.message_handler(commands=['display'])
def handle_display(message):
    display_queue(message.chat.id)

# Start the bot
bot.polling()