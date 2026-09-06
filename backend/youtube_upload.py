"""
Модуль для завантаження відео на YouTube від імені одного централізованого акаунту.
Перекладачі самі ніколи не бачать і не торкаються YouTube — все відбувається
автоматично на бекенді.
"""

import os
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")


def _get_youtube_client():
    """Створює авторизований клієнт YouTube API, використовуючи збережений refresh token."""
    credentials = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("youtube", "v3", credentials=credentials)


def upload_video_bytes(video_bytes: bytes, title: str) -> str:
    """
    Завантажує відео (у вигляді байтів) на YouTube як "unlisted" (не в публічному пошуку).
    Повертає ID завантаженого відео на YouTube.
    """
    youtube = _get_youtube_client()

    media = MediaIoBaseUpload(
        io.BytesIO(video_bytes),
        mimetype="video/webm",
        resumable=True,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"УЖМ: {title}",
                "description": "Запис українською жестовою мовою для проєкту Міст.",
                "categoryId": "27",  # Освіта
            },
            "status": {
                "privacyStatus": "unlisted",
            },
        },
        media_body=media,
    )

    response = request.execute()
    return response["id"]