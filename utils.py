from pytube import YouTube
from pathlib import Path
from loguru import logger
import gradio as gr
import openai
import json
import yaml
import re

# Customize by yourself
TRANSLATE_PROMPT = {
    "zh": "請幫我將這段文字翻譯成繁體中文"
}


class YTTranslator(object):
    def __init__(self, openai_cfg: dict):
        self.cfg = openai_cfg
        openai.api_key = self.cfg["api_key"]

    def build_interface(self):
        input_url_textbox = gr.Textbox(placeholder='Youtube video URL', label='URL')
        output_textbox = gr.Textbox(placeholder='Output text here', label='Transcript')
        ui_interface = gr.Interface(fn=lambda x: video2text(x,
                                                            self.cfg["audio_dir"],
                                                            lang=self.cfg["lang"]),
                                    inputs=input_url_textbox,
                                    outputs=output_textbox)
        return ui_interface

    def __call__(self, url):
        return video2text(url, self.cfg["audio_dir"], lang=self.cfg["lang"])


def download_audio_from_yt(url: str, save_dir: str) -> str:
    logger.info(f"[Download Audio] - start download audio from {url}")
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    mp3_file = save_dir.joinpath(audio.default_filename).with_suffix(".mp3")
    if not mp3_file.exists():
        audio.download(filename=str(mp3_file))
    return str(mp3_file)


def speech_to_english_text(audio_file: str):
    logger.info(f"[Speech2EngText] - start transcribe")
    cache_file = Path(audio_file).with_suffix(".json")
    if not cache_file.exists():
        file = open(audio_file, "rb")
        transcription = openai.Audio.translate("whisper-1", file)
        with open(cache_file, "w") as f:
            json.dump(transcription, f)
    else:
        with open(cache_file, "r") as f:
            transcription = json.load(f)
    logger.info(f"[Speech2EngText] - done")
    return transcription


def translate(eng_text: str, to_lang="zh"):
    logger.info(f"[Translate] - start translate")
    output_text = ""
    sentences = eng_text.split(".")
    batch_size = 32
    sid = 0
    while sid < len(sentences):
        eid = sid + batch_size
        paragraph = "".join(sentences[sid: eid])
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"{TRANSLATE_PROMPT[to_lang]}: {paragraph}"}]
        )
        output_text += completion.choices[0].message.content.strip()
        sid = eid
    logger.info(f"[Translate] - done")
    return output_text


def video2text(url, save_dir, lang="zh") -> str:
    mp3_file = download_audio_from_yt(url, save_dir)
    eng_transcription = speech_to_english_text(mp3_file)
    text = translate(eng_transcription["text"], to_lang=lang)
    return text


def load_yaml(yaml_file: str):
    loader = yaml.SafeLoader
    loader.add_implicit_resolver(
        u'tag:yaml.org,2002:float',
        re.compile(u'''^(?:[-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
                        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
                        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
                        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
                        |[-+]?\\.(?:inf|Inf|INF)
                        |\\.(?:nan|NaN|NAN))$''', re.X),
        list(u'-+0123456789.'))

    with open(yaml_file, "r") as f:
        cfg = yaml.load(f, Loader=loader)

    return cfg
