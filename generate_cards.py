from google import genai
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM = '''You are a Korean language expert creating pronunciation practice cards for Russian-speaking learners.
STRICT RULES:
- Write ONLY in the JSON format specified. No extra text, no markdown, no explanations.
- Korean sentences must be natural and commonly used in daily life.
- Russian translation must be accurate and natural.
- phoneme_focus must be a specific Korean sound that Russian speakers find difficult (e.g. ㄹ, ㅓ, ㅡ, 받침, 경음, 격음).'''

CATEGORIES = [
    ('생활문장', '일상생활에서 자주 쓰는 문장', 20),
    ('관용구', '한국어 관용 표현이 포함된 문장', 20),
    ('상황형회화', '특정 상황에서 쓰는 대화 문장', 20),
    ('기초단어', '기초 단어를 활용한 짧은 문장', 20),
]

all_cards = []

for category, description, count in CATEGORIES:
    print(f'{category} 생성 중...')

    prompt = f"""
카테고리: {category}
설명: {description}
개수: {count}개

아래 JSON 배열 형식으로만 응답하세요. 다른 텍스트는 절대 쓰지 마세요.

[
  {{
    "category": "{category}",
    "korean": "한국어 예문",
    "russian": "러시아어 번역",
    "phoneme_focus": "집중 연습할 음소 (예: ㄹ)"
  }}
]
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=SYSTEM + '\n\n' + prompt
            )
            text = response.text.strip()
            # 마크다운 코드블록 제거
            text = text.replace('```json', '').replace('```', '').strip()
            cards = json.loads(text)
            all_cards.extend(cards)
            print(f'  {len(cards)}개 생성 완료')
            break
        except Exception as e:
            if attempt < 2:
                print(f'  재시도 중... ({attempt+1}/3)')
                time.sleep(30)
            else:
                print(f'  실패: {e}')
                break

    time.sleep(15)

with open('cards.json', 'w', encoding='utf-8') as f:
    json.dump(all_cards, f, ensure_ascii=False, indent=2)

print(f'\n총 {len(all_cards)}개 예문이 cards.json에 저장됐어요!')