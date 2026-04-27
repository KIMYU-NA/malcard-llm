from google import genai
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM = '''당신은 러시아어권 한국어 학습자를 위한 친절한 발음 선생님입니다.
러시아어에는 없는 한국어 특유의 발음(ㅓ, ㅡ, 받침, 경음/격음 구분 등)을 학습자가 어려워한다는 걸 염두에 두세요.
피드백은 아래 규칙을 따라 작성해주세요:
1. 첫 문장은 반드시 격려로 시작하세요.
2. 점수가 낮은 항목(자음/모음/유창성)을 중심으로 핵심 교정 포인트 1~2개만 짚어주세요.
3. 교정 방법은 "혀를 어디에 두세요" 같이 입 모양, 혀 위치로 쉽게 설명해주세요.
4. 전문 용어(IPA 기호 등)는 절대 쓰지 마세요.
5. 전체 2~3문장으로 간결하게 써주세요.'''

samples_dir = Path('samples')
json_files = list(samples_dir.glob('*.json'))

print(f'샘플 파일 {len(json_files)}개 발견\n')
print('=' * 60)

results = []

for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    feedback_input = data.get('llm_feedback_input', {})
    ref_text = feedback_input.get('reference_text', '')
    score = feedback_input.get('score_breakdown', {})
    issues = feedback_input.get('issues', [])

    issue_lines = '\n'.join([
        f"- [{issue['severity']}] {issue['description']} (교정 팁: {issue['tip']})"
        for issue in issues[:5]
    ])

    prompt = f"""
정답 문장: {ref_text}

발음 점수 (100점 만점):
- 전체: {score.get('overall', 0):.1f}점
- 자음 정확도: {score.get('consonant', 0):.1f}점
- 모음 정확도: {score.get('vowel', 0):.1f}점
- 받침 정확도: {score.get('coda', 0):.1f}점
- 유창성: {score.get('fluency_like', 0):.1f}점 (30점 만점 기준)

주요 발음 오류 (심각한 것부터):
{issue_lines}

위 정보를 바탕으로 러시아어권 학습자에게 친절하고 실용적인 발음 피드백을 작성해주세요.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=SYSTEM + '\n\n' + prompt
            )
            break
        except Exception as e:
            if attempt < 2:
                print(f'  재시도 중... ({attempt+1}/3)')
                time.sleep(30)
            else:
                print(f'  실패: {e}')
                response = None
                break

    if response is None:
        continue

    feedback = response.text

    print(f'파일: {json_file.name}')
    print(f'문장: {ref_text[:40]}...')
    print(f'점수: 전체 {score.get("overall", 0):.1f} / 자음 {score.get("consonant", 0):.1f} / 모음 {score.get("vowel", 0):.1f} / 받침 {score.get("coda", 0):.1f} / 유창성 {score.get("fluency_like", 0):.1f}')
    print(f'피드백: {feedback}')
    print('-' * 60)

    results.append({
        'file': json_file.name,
        'reference_text': ref_text,
        'score': {
            'overall': round(score.get('overall', 0), 2),
            'consonant': round(score.get('consonant', 0), 2),
            'vowel': round(score.get('vowel', 0), 2),
            'coda': round(score.get('coda', 0), 2),
            'fluency_like': round(score.get('fluency_like', 0), 2),
        },
        'feedback': feedback
    })

    time.sleep(15)

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n결과가 results.json에 저장됐어요!')