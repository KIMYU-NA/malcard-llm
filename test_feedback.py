from google import genai
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM = '''당신은 러시아어권 한국어 학습자를 위한 발음 교정 전문가입니다.
아래 발음 분석 결과를 보고 학습자에게 자연스럽고 친절한 피드백을 2~3문장으로 작성해주세요.
전문 용어(IPA 기호 등)는 쓰지 말고, 쉬운 말로 설명해주세요.'''

samples_dir = Path('samples')
json_files = list(samples_dir.glob('*.json'))

print(f'샘플 파일 {len(json_files)}개 발견\n')
print('=' * 60)

for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    feedback_input = data.get('llm_feedback_input', {})
    ref_text = feedback_input.get('reference_text', '')
    score = feedback_input.get('score_breakdown', {})
    issues = feedback_input.get('issues', [])

    prompt = f"""
정답 문장: {ref_text}
전체 점수: {score.get('overall', 0):.1f}점
자음 점수: {score.get('consonant', 0):.1f}점
모음 점수: {score.get('vowel', 0):.1f}점

주요 오류:
{chr(10).join([f"- {issue['description']} (교정 팁: {issue['tip']})" for issue in issues[:3]])}

위 결과를 바탕으로 학습자에게 격려와 함께 핵심 교정 포인트를 알려주세요.
"""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=SYSTEM + '\n\n' + prompt
    )

    print(f'파일: {json_file.name}')
    print(f'문장: {ref_text[:40]}...')
    print(f'점수: {score.get("overall", 0):.1f}점')
    print(f'피드백: {response.text}')
    print('-' * 60)

    time.sleep(15)