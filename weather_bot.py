import requests
import time

# ===== 설정 =====
BOT_TOKEN = "8615496573:AAH7JRA50W5SR0NbLlYfwTOYcI0hcGLXxmg"
CHAT_ID = "5192558336"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 오늘 날씨
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=35.82&longitude=128.74&current_weather=true"

    data = requests.get(url).json()

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

# 내일 날씨
def get_tomorrow_weather():
    return get_weather()

# 옷 추천
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

# 메시지 보내기
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

# 메시지 처리 (🔥 핵심 수정 완료)
def handle_message(message):
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()

    print("입력값:", text)  # ← 함수 안으로 이동

    if "내일" in text:
        temp, desc = get_tomorrow_weather()
        clothes = recommend_clothes(temp)

        reply = f"""🌤 내일 날씨
기온: {temp}°C
상태: {desc}

👕 추천 코디
{clothes}
"""

    elif "날씨" in text:
        temp, desc = get_weather()
        clothes = recommend_clothes(temp)

        reply = f"""🌤 오늘 날씨
기온: {temp}°C
상태: {desc}

👕 추천 코디
{clothes}
"""
    else:
        reply = "날씨 또는 내일 날씨라고 입력해주세요 😊"

    send_message(chat_id, reply)

# 업데이트 받기
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

# 메인
def main():
    offset = None

    while True:
        data = get_updates(offset)

        if "result" in data and len(data["result"]) > 0:
            for update in data["result"]:

                if "message" in update:
                    handle_message(update["message"])

                offset = update["update_id"] + 1

        time.sleep(1)
       
if __name__ == "__main__":
    print("봇 실행 중...")
    main()