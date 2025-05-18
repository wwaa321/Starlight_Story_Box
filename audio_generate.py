import dashscope
from dashscope.audio.tts_v2 import *
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET


tree=ET.parse("configuration/configuration.xml")
root=tree.getroot()
api_key_info=root.find("llm_setting/apikey").text



audio_folder="audio_files" # 有声书籍的音频文件存放目录
dashscope.api_key=api_key_info

model = "cosyvoice-v1"




def create_audio(content,audio_role,file_name):
    match audio_role:
        case "龙小白":
            voice="longxiaobai"
        case "龙老铁":
            voice="longlaotie"
        case "龙书":
            voice="longshu"
        case "龙妙":
            voice="longmiao"
        case "龙悦":
            voice="longyue"
        case "龙媛":
            voice="longyuan"
        case "龙飞":
            voice="longfei"
        case "龙杰力豆":
            voice="longjielidou"
        case "龙彤":
            voice="longtong"
        case "龙祥":
            voice="longxiang"
    file_path=Path(audio_folder)
    if not file_path.exists():
        file_path.mkdir(parents=True, exist_ok=True)
    synthesizer = SpeechSynthesizer(model=model, voice=voice)
    audio = synthesizer.call(content)
    file_created_time=datetime.now().strftime("%Y%m%d%H%M%S")
    audio_path=f'{file_path}/{file_name}_{file_created_time}.mp3'
    with open(audio_path, 'wb') as f:
        f.write(audio)
    return audio_path

