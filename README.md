# YouTube Video to Traditional Chinese text

## Blog
https://medium.com/@hongjunyanlab/video-to-chinese-text-whisper-gpt-3-5-turbo-12cd57e74b7a

## Edit Config
- config.yaml
  ```yaml
  OPENAI:
    api_key: ""  # 請輸入你的api key, 若沒有，可以到https://platform.openai.com/account/api-keys，然後按`Create new secret key` 
    lang: "zh"  # 目前只支援繁體中文
    audio_dir: "./audio_dir"  # 從youtube下載的語音檔會存在這裡
  ```

## How to use
- 方式一: 本機執行
  - Step1: 下載並安裝[anaconda](https://www.anaconda.com/)
  - Step2: 執行`conda env create -f conda.yaml`
  - Step3: 執行`conda activate ytvideo2text` or `activate ytvideo2text`
  - Step4: 執行`python main.py`
- 方式二: 使用Container(推薦使用)
  - Step1: 安裝[Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Step2: 執行`docker compose build`
  - Step3: 執行`docker compose up -d`
  - Step4: 停止服務，請執行`docker compose down`

使用UI操作: http://127.0.0.1:8080/ui

使用python串接:
```python
import requests
import json


url = "https://www.youtube.com/watch?v=q1u3JzLaIlo&ab_channel=TEDxTalks"
resp = requests.get("http://127.0.0.1:8080/video_url_to_text", params={"url": url})
text = json.loads(resp.text)["text"]
print(text)
```
