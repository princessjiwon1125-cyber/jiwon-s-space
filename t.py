# 06_image_chbi.py
from openai import OpenAI
from dotenv import load_dotenv
import base64

load_dotenv("key.env")
client = OpenAI()

image_path = "ddd.png"

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

base64_image = encode_image(image_path)

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "이 이미지 속 인물을 치비(Chibi) 캐릭터로 변환하기 위한 설명을 작성해주세요. "
                        "얼굴 특징, 헤어스타일, 옷차림, 색상 특징을 유지하고 "
                        "머리는 크게, 몸은 작고 귀엽게 과장된 비율로 묘사해주세요."
                    )
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]
)

character_prompt = response.output_text
print("치비 캐릭터 프롬프트 생성 완료\n")
print(character_prompt)


# 2️⃣ 생성된 설명 → 치비 캐릭터 이미지 생성
image_result = client.images.generate(
    model="gpt-image-1",
    prompt=character_prompt,
    size="1024x1024",
    n=1
)

# base64 이미지 디코딩 후 저장
image_base64 = image_result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

with open("chibi_character.png", "wb") as f:
    f.write(image_bytes)

print("\n이미지 저장 완료: chibi_character.png")
