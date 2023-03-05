from fastapi import FastAPI
import uvicorn
import gradio as gr
from utils import YTTranslator, load_yaml

config = load_yaml("./config.yaml")
app = FastAPI()
yt_translator = YTTranslator(config["OPENAI"])
app = gr.mount_gradio_app(app, yt_translator.build_interface(), path="/ui")


@app.get("/")
def index():
    return {"message": "app is running"}


@app.get("/video_url_to_text")
def video_url_to_text(url: str):
    text = yt_translator(url)
    return {"text": text}


uvicorn.run(app, host="0.0.0.0", port=8080)
