import telebot
import requests
import time
import os

from flask import Flask
from threading import Thread
from urllib.parse import quote

# ===== 설정 =====
BOT_TOKEN = "8615496573:AAH7JRA50W5SR0NbLlYfwTOYcI0hcGLXxmg"
KAKAO_API_KEY = "ef1b18abff17b07d7834a34c0deca996"


BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ===== Flask =====
app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


# ===== Render 유지 =====
def run_web():

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 10000))
    )


def keep_alive():

    t = Thread(target=run_web)

    t.start()


# ===== 날씨 =====
def get_weather(lat, lon):

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current_weather=true"
    )

    response = requests.get(
        url,
        timeout=10
    )

    data = response.json()

    print("날씨 데이터:")
    print(data)

    temp = data['current_weather']['temperature']

    weather_code = data['current_weather']['weathercode']

    if weather_code == 0:
        desc = "맑음 ☀️"

    elif weather_code <= 3:
        desc = "구름 조금 ⛅"

    elif weather_code <= 48:
        desc = "안개 🌫"

    elif weather_code <= 67:
        desc = "비 🌧"

    elif weather_code <= 77:
        desc = "눈 ❄️"

    else:
        desc = "흐림 ☁️"

    return temp, desc


# ===== 옷 추천 =====
def recommend_clothes(temp):

    if temp >= 28:
        return "반팔 + 반바지 🩳"

    elif temp >= 22:
        return "반팔 + 긴바지 👖"

    elif temp >= 17:
        return "얇은 긴팔 👕"

    elif temp >= 10:
        return "자켓 🧥"

    else:
        return "코트 + 니트 🧣"


# ===== 활동 추천 =====
def recommend_activity(temp, desc):

    if "비" in desc:
        return "키즈카페"

    elif temp >= 28:
        return "물놀이장"

    elif temp >= 20:
        return "어린이공원"

    elif temp >= 10:
        return "수목원"

    else:
        return "실내 키즈카페"


# ===== 장소 검색 =====
def search_nearby_places(lat, lon, keyword):

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    params = {
        "query": keyword,
        "x": lon,
        "y": lat,
        "radius": 10000,
        "size": 3
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    data = response.json()

    print("장소 검색:")
    print(data)

    places = []

    for place in data.get("documents", []):

        name = place.get("place_name", "장소명 없음")

        address = (
            place.get("road_address_name")
            or place.get("address_name")
            or "주소 없음"
        )

        naver_link = (
            f"https://map.naver.com/v5/search/"
            f"{quote(name, safe='')}"
        )

        place_text = (
            f"📍 {name}\n"
            f"🏠 {address}\n"
            f"🗺 <a href='{naver_link}'>지도 보기</a>"
        )

        places.append(place_text)

    if len(places) == 0:
        return "주변 추천 장소를 찾지 못했어요 😢"

    return "\n\n".join(places)


# ===== 이미지 검색 =====
def search_place_image(keyword):

    url = "https://dapi.kakao.com/v2/search/image"

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    params = {
        "query": keyword,
        "size": 1
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    data = response.json()

    print("이미지 검색:")
    print(data)

    documents = data.get("documents", [])

    if len(documents) > 0:
        return documents[0]["image_url"]

    return None


# ===== 위치 버튼 =====
def send_location_button(chat_id):

    url = f"{BASE_URL}/sendMessage"

    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📍 현재 위치 보내기",
                    "request_location": True
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": "📍 현재 위치를 보내주세요 😊",
            "reply_markup": keyboard
        },
        timeout=10
    )

    print(response.text)


# ===== 메시지 보내기 =====
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    try:

        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=10
        )

        print("메시지 전송:")
        print(response.text)

    except Exception as e:

        print("메시지 전송 오류:")
        print(e)


# ===== 사진 보내기 =====
def send_photo(chat_id, photo_url, caption=""):

    url = f"{BASE_URL}/sendPhoto"

    try:

        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML"
            },
            timeout=15
        )

        print("사진 전송:")
        print(response.text)

    except Exception as e:

        print("사진 전송 오류:")
        print(e)


# ===== 날씨 응답 =====
def send_weather_response(chat_id, lat, lon):

    print("위치 수신 성공")
    print(lat, lon)

    temp, desc = get_weather(lat, lon)

    clothes = recommend_clothes(temp)

    keyword = recommend_activity(temp, desc)

    places = search_nearby_places(
        lat,
        lon,
        keyword
    )

    image_keyword = f"{keyword} 아이와 가볼만한 곳"

    photo_url = search_place_image(
        image_keyword
    )

    reply = f"""📍 현재 위치 기반 추천

🌡 현재 기온: {temp}°C
☁️ 날씨: {desc}

👕 추천 코디
{clothes}

🎈 추천 장소
{places}
"""

    if photo_url:

        send_photo(
            chat_id,
            photo_url,
            "📸 추천 장소 이미지"
        )

    send_message(chat_id, reply)


# ===== 메시지 처리 =====
def handle_message(message):

    chat_id = message['chat']['id']

    chat_type = message['chat']['type']

    text = message.get('text')

    if text:
        text = text.strip()
    else:
        text = ""

    location = message.get("location")

    print("입력값:")
    print(message)

    # ===== 위치 받은 경우 =====
    if location:

        lat = location["latitude"]

        lon = location["longitude"]

        send_weather_response(
            chat_id,
            lat,
            lon
        )

        return

    # ===== 날씨 =====
    elif "날씨" in text:

        # 개인채팅
        if chat_type == "private":

            send_location_button(chat_id)

        # 그룹채팅
        else:

            send_message(
                chat_id,
                """📍 위치를 보내주시면

현재 위치 기반으로:

• 날씨
• 추천 코디
• 아이와 가볼만한 곳
• 장소 사진
• 네이버 지도 링크

를 추천해드려요 😊

📎 버튼 → 위치 → 현재 위치 보내기"""
            )

    # ===== 기타 =====
    else:

        send_message(
            chat_id,
            "날씨 라고 입력해주세요 😊"
        )


# ===== 업데이트 =====
def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 30
    }

    if offset:
        params["offset"] = offset

    try:

        res = requests.get(
            url,
            params=params,
            timeout=35
        )

        return res.json()

    except Exception as e:

        print("get_updates 오류:")
        print(e)

        return {"result": []}


# ===== 메인 =====
def main():

    offset = None

    while True:

        try:

            data = get_updates(offset)

            if (
                "result" in data
                and len(data["result"]) > 0
            ):

                for update in data["result"]:

                    if "message" in update:

                        try:

                            handle_message(
                                update["message"]
                            )

                        except Exception as e:

                            print("메시지 처리 오류:")
                            print(e)

                            send_message(
                                update["message"]["chat"]["id"],
                                f"오류 발생 😢\n{e}"
                            )

                    offset = (
                        update["update_id"] + 1
                    )

            time.sleep(1)

        except Exception as e:

            print("메인 루프 오류:")
            print(e)

            time.sleep(5)


# ===== 시작 =====
if __name__ == "__main__":

    print("봇 실행 중...")

    keep_alive()

    while True:

        try:

            main()

        except Exception as e:

            print("치명적 오류:")
            print(e)

            time.sleep(10)