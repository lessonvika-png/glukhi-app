"""
Одноразовий скрипт для отримання refresh token від YouTube.
Запусти його ОДИН РАЗ локально, він відкриє браузер і попросить дозвіл.
Після цього видасть refresh_token, який треба скопіювати в .env файл бекенду.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# Дозвіл, який нам потрібен: завантажувати відео на YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )
    # Це відкриє браузер, попросить увійти в Google-акаунт і дати дозвіл
    credentials = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("УСПІШНО! Ось твій refresh token — скопіюй його в .env:")
    print("=" * 60)
    print(f"\nYOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    print(f"YOUTUBE_CLIENT_ID={credentials.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={credentials.client_secret}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()