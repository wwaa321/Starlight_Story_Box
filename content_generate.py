
from openai import OpenAI

import base64
import xml.etree.ElementTree as ET
import mimetypes
tree=ET.parse("configuration/configuration.xml")
root=tree.getroot()
api_key_info=root.find("llm_setting/apikey").text
chat_model_info=root.find("llm_setting/chat_model").text
vision_modei_info=root.find("llm_setting/vision_model").text
base_url_info=root.find("llm_setting/base_url").text
system_prompt_vision="你是一个绘本图像识别器，你可以根据图像内容，生成图像描述"
system_prompt_chat="你是一个AI小说作者，你可以根据用户输入，生成小说内容"
temperature =0.7
max_tokens=4096




#qwen-----------------------start
def conversation_vision_stream(content,img_path):
    message=[{"role": "system", "content": "{}".format(system_prompt_vision)},
  ]



    # 获取图片的 MIME 类型
    mime_type, _ = mimetypes.guess_type(img_path)
    if mime_type is None:
        mime_type = "application/octet-stream"  # 默认 MIME 类型

    # 使用 base64 编码
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    message.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{encoded_string}",
                    "detail": "low"
                }
            },
            {
                "type": "text",
                "text": "{}".format(content)
            }
        ]
    })

    client = OpenAI(
    api_key=api_key_info,  
    base_url=base_url_info,
    )
    try:
        response=client.chat.completions.create(
            model=vision_modei_info,
            messages=message,

            stream=True
        )
        collected_chunks = []
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                collected_chunks.append(chunk.choices[0].delta.content)
                yield chunk.choices[0].delta.content



    except Exception as e:
        error_message = f"很抱歉，目前无法处理您的请求，请稍后再试。错误：{e}"
        message.append({"role": "assistant", "content": error_message})
        yield error_message








def conversation_chat_stream(content):
    message=[{"role": "system", "content": "{}".format(system_prompt_chat)},
  ]
  
    message.append({"role": "user", "content": "{}".format(content)})

    client = OpenAI(
    api_key=api_key_info,
    base_url=base_url_info,
    )
    try:
        response=client.chat.completions.create(
            model=chat_model_info,
            messages=message,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        collected_chunks = []
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                collected_chunks.append(chunk.choices[0].delta.content)
                yield chunk.choices[0].delta.content
        # 将完整响应添加到消息历史
        full_response = "".join(collected_chunks)
        message.append({"role": "assistant", "content": full_response})

    except Exception as e:
        error_message = f"很抱歉，目前无法处理您的请求，请稍后再试。错误：{e}"
        message.append({"role": "assistant", "content": error_message})
        yield error_message



