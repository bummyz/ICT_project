# AI 답변 생성 코드 준비
import openai

openai.api_key = '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'

def get_ai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# 테스트할 텍스트를 입력해 주세요
response_text = get_ai_response("안녕하세요")
print("AI Response: ", response_text)
