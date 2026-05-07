import requests
import time
from urllib.parse import quote

# ===== 설정 =====
BOT_TOKEN = "8615496573:AAH7JRA50W5SR0NbLlYfwTOYcI0hcGLXxmg"
KAKAO_API_KEY = "ef1b18abff17b07d7834a34c0deca996"
CHAT_ID = "5192558336"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ===== 오늘 날씨 가져오기 =====
def get_weather():

    url = "https://api.open-meteo.com/v1/forecast?latitude=35.82&longitude=128.74&current_weather=true"

    data = requests.get(url).json()

    print("날씨 데이터:")
    print(data)

    temp = data['current_weather']['temperature']
    weather_code = data['current_weather']['weathercode']

    # 날씨 상태 변환
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


# ===== 내일 날씨 =====
def get_tomorrow_weather():
    return get_weather()


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


# ===== 카카오 장소 검색 =====
def search_places(keyword):

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    params = {
        "query": keyword,
        "size": 3
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    data = response.json()

    print("카카오 장소 검색:")
    print(data)

    places = []

    for place in data.get('documents', []):

        name = place.get('place_name', '장소명 없음')

        address = (
            place.get('road_address_name')
            or place.get('address_name')
            or '주소 없음'
        )

        # 네이버 지도 링크
        encoded_name = quote(name)
        naver_link = f"https://map.naver.com/v5/search/{encoded_name}"

        places.append(
            f"""📍 {name}
🏠 {address}
🗺 {naver_link}"""
        )

    # 검색 결과 없을 때
    if len(places) == 0:
        return "추천 장소를 찾지 못했어요 😢"

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


# ===== 아이와 가볼만한 곳 추천 =====
def recommend_activity(temp, desc):

    # 비 오는 날
    if "비" in desc:

        keyword = "경산 키즈카페"
        places = search_places(keyword)

        text = f"""🎨 오늘은 비가 와요!

추천 장소:
{places}
"""

    # 더운 날
    elif temp >= 28:

        keyword = "경산 물놀이장"
        places = search_places(keyword)

        text = f"""💦 날씨가 더워요!

추천 장소:
{places}
"""

    # 야외활동 좋은 날
    elif temp >= 20:

        keyword = "경산 어린이공원"
        places = search_places(keyword)

        text = f"""🌳 야외활동 하기 좋아요!

추천 장소:
{places}
"""

    # 선선한 날
    elif temp >= 10:

        keyword = "경산 수목원"
        places = search_places(keyword)

        text = f"""🚶 산책하기 좋은 날씨예요!

추천 장소:
{places}
"""

    # 추운 날
    else:

        keyword = "경산 실내 키즈카페"
        places = search_places(keyword)

        text = f"""☕ 날씨가 추워요!

추천 장소:
{places}
"""

    return text, keyword


# ===== 텔레그램 메시지 보내기 =====
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text
        }
    )

    print("텔레그램 응답:")
    print(response.text)


# ===== 텔레그램 사진 보내기 =====
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

    print("사진 전송 응답:")
    print(response.text)


# ===== 메시지 처리 =====
def handle_message(message):

    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    print("입력값:", text)

    # ===== 내일 날씨 =====
    if "내일" in text:

        temp, desc = get_tomorrow_weather()

        clothes = recommend_clothes(temp)

        activity_text, keyword = recommend_activity(temp, desc)

        reply = f"""🌤 내일 날씨

🌡 기온: {temp}°C
☁️ 상태: {desc}

👕 추천 코디
{clothes}

🎈 아이와 가볼만한 곳
{activity_text}
"""

    # ===== 오늘 날씨 =====
    elif "날씨" in text:

        temp, desc = get_weather()

        clothes = recommend_clothes(temp)

        activity_text, keyword = recommend_activity(temp, desc)

        reply = f"""🌤 오늘 날씨

🌡 기온: {temp}°C
☁️ 상태: {desc}

👕 추천 코디
{clothes}

🎈 아이와 가볼만한 곳
{activity_text}
"""

    else:

        reply = "날씨 또는 내일 날씨라고 입력해주세요 😊"
        keyword = "경산 키즈카페"

    # ===== 장소 사진 검색 =====
    photo_url = search_place_image(keyword)

    # ===== 사진 있으면 사진 전송 =====
    if photo_url:

        send_photo(
            chat_id,
            photo_url,
            reply
        )

    # ===== 사진 없으면 텍스트만 전송 =====
    else:

        send_message(chat_id, reply)


# ===== 업데이트 가져오기 =====
def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 10
    }

    if offset:
        params["offset"] = offset

    res = requests.get(url, params=params)

    print("업데이트 응답:")
    print(res.text)

    return res.json()


# ===== 메인 실행 =====
def main():

    offset = None

    while True:

        try:

            data = get_updates(offset)

            if "result" in data and len(data["result"]) > 0:

                for update in data["result"]:

                    if "message" in update:

                        try:
                            handle_message(update["message"])

                        except Exception as e:
                            print("메시지 처리 오류:", e)

                    offset = update["update_id"] + 1

            time.sleep(1)

        except Exception as e:

            print("메인 루프 오류:", e)
            time.sleep(5)


# ===== 실행 시작 =====
if __name__ == "__main__":

    print("봇 실행 중...")
    main()