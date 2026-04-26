from volcenginesdkarkruntime import Ark
from django.conf import settings


def get_llm_client():
    return Ark(
        api_key=settings.LLM_API_KEY,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )


SYSTEM_PROMPT = """你是一个专业的宠物健康顾问，名叫"毛毛助手"。
你的职责是：
1. 回答宠物健康、喂养、疫苗、驱虫等方面的问题
2. 给出科学合理的养宠建议
3. 如果问题超出你的能力范围，建议用户咨询专业兽医

回答要求：
- 语言亲切友好，通俗易懂
- 控制在300字以内
- 涉及严重症状时，提醒用户及时就医"""


def ask_llm(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-20:])

    messages.append({"role": "user", "content": user_message})

    client = get_llm_client()
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,  # 填你的接入点ID
        messages=messages,
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content
