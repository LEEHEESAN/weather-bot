import requests
import time
from urllib.parse import quote

from flask import Flask
from threading import Thread

# ===== 설정 =====
BOT_TOKEN = "8615496573:AAH7JRA50W5SR0NbLlYfwTOYcI0hcGLXxmg"
KAKAO_API_KEY = "ef1b18abff17b07d7834a34c0deca996"
CHAT_ID = "5192558336"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ===== Flask 웹서버 =====
app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run_web():
    app.run(host='0.0.0.0', port=10000)


def keep_alive():
    t = Thread(target=run_web)
    t.start()


# ===== 위치 기반 날씨 =====
def get_weather(lat, lon):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    data = requests.get(url).json()

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
        "radius": 5000,
        "size": 3
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
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

        # 네이버 지도 링크
        naver_link = f"https://map.naver.com/v5/search/{quote(name, safe='')}"

        places.append(
            f"""📍 {name}
🏠 {address}
🗺 <a href='{naver_link}'>지도 보기</a>"""
        )

    if len(places) == 0:
        return "주변 추천 장소를 찾지 못했어요 😢"

    return "\n\n".join(places)


# ===== 장소 이미지 검색 =====
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
        params=params
    )

    data = response.json()

    print("이미지 검색:")
    print(data)

    documents = data.get("documents", [])

    if len(documents) > 0:
        return documents[0]["image_url"]

    return None


# ===== 텔레그램 메시지 보내기 =====
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
    )

    print("메시지 전송:")
    print(response.text)


# ===== 사진 보내기 =====
def send_photo(chat_id, photo_url, caption=""):

    url = f"{BASE_URL}/sendPhoto"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption
        }
    )

    print("사진 전송:")
    print(response.text)


# ===== 메시지 처리 =====
def handle_message(message):

    chat_id = message['chat']['id']

    text = message.get('text', '').strip()

    location = message.get("location")

    print("입력값:")
    print(message)

    # ===== 위치 기반 =====
    if location:

        lat = location["latitude"]
        lon = location["longitude"]

        # 날씨
        temp, desc = get_weather(lat, lon)

        # 코디 추천
        clothes = recommend_clothes(temp)

        # 활동 추천
        keyword = recommend_activity(temp, desc)

        # 장소 검색
        places = search_nearby_places(
            lat,
            lon,
            keyword
        )

        # 이미지 검색
        image_keyword = f"{keyword} 경산"

        photo_url = search_place_image(
            image_keyword
        )

        # 답변 생성
        reply = f"""📍 현재 위치 기반 추천

🌡 현재 기온: {temp}°C
☁️ 날씨: {desc}

👕 추천 코디
{clothes}

🎈 추천 장소
{places}
"""

        # 사진 먼저 보내기
        if photo_url:

            send_photo(
                chat_id,
                photo_url,
                "📸 추천 장소 이미지"
            )

        # 텍스트 따로 보내기
        send_message(chat_id, reply)

        return

    # ===== 날씨 입력 =====
    elif "날씨" in text:

        reply = """📍 위치를 보내주시면

현재 위치 기반으로:

• 날씨
• 추천 코디
• 아이와 갈만한 곳
• 장소 사진
• 네이버 지도 링크

를 추천해드려요 😊

📎 버튼 → 위치 → 현재 위치 보내기
"""

        send_message(chat_id, reply)

    # ===== 기타 =====
    else:

        send_message(
            chat_id,
            "날씨 또는 위치를 보내주세요 😊"
        )


# ===== 업데이트 가져오기 =====
def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 10
    }

    if offset:
        params["offset"] = offset

    res = requests.get(
        url,
        params=params
    )

    print("업데이트 응답:")
    print(res.text)

    return res.json()


# ===== 메인 =====
def main():

    offset = None

    while True:

        try:

            data = get_updates(offset)

            if "result" in data and len(data["result"]) > 0:

                for update in data["result"]:

                    if "message" in update:

                        try:

                            handle_message(
                                update["message"]
                            )

                        except Exception as e:

                            print("메시지 처리 오류:")
                            print(e)

                    offset = update["update_id"] + 1

            time.sleep(1)

        except Exception as e:

            print("메인 루프 오류:")
            print(e)

            time.sleep(5)


# ===== 시작 =====
if __name__ == "__main__":

    print("봇 실행 중...")

    keep_alive()

    main()