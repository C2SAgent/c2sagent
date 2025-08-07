import os
from openai import OpenAI
from volcenginesdkarkruntime import Ark


class volcano:
    def __init__(self, key):
        self.key = key

    async def text_to_video(self, text):
        client = Ark(self.key)
        generation = client.content_generation.tasks.create(
            model="doubao-seedance-1-0-pro-250528",
            content=[{"text": f"{text}--ratio 16:9", "type": "text"}],
        )
        resp = client.content_generation.tasks.get(generation["id"])
        return resp

    async def text_to_image(self, text):
        client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.key,
        )

        generation = client.images.generate(
            prompt=text,
            model="doubao-seedream-3-0-t2i-250415",
            response_format="url",
            size="1024x1024",
        )
        return generation["data"][0]["url"]
