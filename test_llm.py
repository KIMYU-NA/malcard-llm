from google import genai
from groq import Groq
import os
import time
from dotenv import load_dotenv

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

SYSTEM = '당신은 러시아어권 한국어 학습자를 위한 발음 교정 교사입니다. 1~2문장으로 쉽고 자연스럽게 교정 메시지를 작성하세요.'

PROMPTS = [
    ('짧은 교정', '학습자가 "버스"를 발화했습니다. 첫 음소 /p/ 감지. 1문장 교정 안내.'),
    ('긴 교정', '학습자가 "지하철 몇 호선이에요?"를 발화했습니다. 받침 ㄹ 누락, 끝 억양 상승. 오류 위치와 교정 방법을 각 1문장씩 설명해주세요.'),
]

GEMINI_MODELS = [
    ('Gemini 3.1 Flash-Lite', 'gemini-3.1-flash-lite-preview'),
    ('Gemini 3 Flash', 'gemini-3-flash-preview'),
    ('Gemini 2.5 Flash', 'gemini-2.5-flash'),
    ('Gemini 2.5 Flash-Lite', 'gemini-2.5-flash-lite'),
]

for label, user_msg in PROMPTS:
    print(f'\n[{label}]')
    print('-' * 60)
    for model_name, model_id in GEMINI_MODELS:
        try:
            t0 = time.time()
            r = gemini_client.models.generate_content(
                model=model_id,
                contents=SYSTEM + '\n\n' + user_msg
            )
            t = time.time() - t0
            print(f'  {model_name:<25} {t:>6.2f}s')
            print(f'  응답: {r.text[:100]}')
        except Exception as e:
            print(f'  {model_name:<25} 오류: {str(e)[:60]}')
        print()

    t0 = time.time()
    r_groq = groq_client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': user_msg}
        ]
    )
    t_groq = time.time() - t0
    print(f'  {"Groq(Llama)":<25} {t_groq:>6.2f}s')
    print(f'  응답: {r_groq.choices[0].message.content[:200]}')