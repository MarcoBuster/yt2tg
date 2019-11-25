import os
import sqlite3
import urllib.request

import youtube
import youtube_dl
from telethon.sync import TelegramClient
from telethon.tl import types

import config

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

bot = TelegramClient(
    'bot',
    api_id=config.TELEGRAM_API_ID,
    api_hash=config.TELEGRAM_API_HASH,
).start(bot_token=config.TELEGRAM_BOT_TOKEN)
api = youtube.API(
    client_id=config.YOUTUBE_CLIENT_ID,
    client_secret=config.YOUTUBE_CLIENT_SECRET,
    api_key=config.YOUTUBE_API_KEY,
)
ydl = youtube_dl.YoutubeDL({
    'outtmpl': f'{ABSOLUTE_PATH}/tmp/tmp_file.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '140',
    }],
} if config.MODE == 'audio' else {
    'outtmpl': f'{ABSOLUTE_PATH}/tmp/tmp_file.%(ext)'
})
conn = sqlite3.connect('bot.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS urls(video_id text)')


def get_videos(channel_id):
    # https://stackoverflow.com/a/36387404/6083563
    playlist_id = api.get('channels', id=channel_id, part='contentDetails')['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos = api.get('playlistItems', playlistId=playlist_id, part='contentDetails')['items']
    return videos


def check_new_videos(channel_id):
    videos = get_videos(channel_id)
    new_videos = []
    for video in videos:
        video_id = video['contentDetails']['videoId']
        c.execute('SELECT COUNT(*) FROM urls WHERE video_id=?;', (video_id, ))
        if c.fetchone()[0]:
            continue
        new_videos.append(video_id)
    return new_videos


def download_then_send(video_id):
    result = ydl.extract_info(f'https://youtube.com/watch?v={video_id}')
    urllib.request.urlretrieve(result['thumbnail'], 'tmp/thumb.jpg')
    if config.MODE == 'audio':
        bot.send_file(
            config.TELEGRAM_CHAT_ID,
            file=f'{ABSOLUTE_PATH}/tmp/tmp_file.mp3',
            thumb=f'{ABSOLUTE_PATH}/tmp/thumb.jpg',
            attributes=[
                types.DocumentAttributeAudio(
                    voice=False,
                    title=result['title'],
                    performer=result['uploader'],
                    duration=result['duration'],
                )
            ],
        )
        os.remove(f'{ABSOLUTE_PATH}/tmp/tmp_file.mp3')
    elif config.MODE == 'video':
        bot.send_file(config.TELEGRAM_CHAT_ID, file='tmp/tmp_file.mp4')
        os.remove(f'{ABSOLUTE_PATH}/tmp/tmp_file.mp4')
    os.remove(f'{ABSOLUTE_PATH}/tmp/thumb.jpg')
    c.execute('INSERT INTO urls VALUES(?)', (video_id, ))
    conn.commit()


def main():
    to_download = []
    for channel_id in config.YOUTUBE_CHANNEL_IDS:
        to_download.extend(check_new_videos(channel_id))

    to_download.reverse()

    for video_id in to_download:
        download_then_send(video_id)


if __name__ == '__main__':
    main()
