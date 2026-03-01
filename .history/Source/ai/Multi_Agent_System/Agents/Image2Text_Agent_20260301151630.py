from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from PIL import Image
import base64
import io

llm = ChatOllama(
    model="qwen2.5vl:3b",
    temperature=0,
    num_ctx=4096,
    num_predict=512
)

def encode_image_quality(image_path, max_size=1500):
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size))
    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

image_path = "../Program/Image/image1.png"
image_base64 = encode_image_quality(image_path)

OCR_PROMPT = """
Extract ALL visible text exactly as written.
Preserve Vietnamese diacritics.
Return plain text only.
"""

message = HumanMessage(
    content=[
        {"type": "text", "text": OCR_PROMPT},
        {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_base64}"
        }
    ]
)

response = llm.invoke([message])
print(response.content)