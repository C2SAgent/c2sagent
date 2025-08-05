from datetime import datetime
from fastapi import Body, FastAPI, File, Query, Request, Depends, UploadFile
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse, ListResponse
from core.db.base import DatabaseManager
from model import model_agent as models
from core.db.base_mongo import MongoDBManager
from api.apps.agent.config import settings

from api.utils.database import engine

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI(on_startup=[init_db])

import os
import aiofiles
import uuid
import base64
import requests
import asyncio
from fastapi import FastAPI, Request, UploadFile, File, Body, Depends
from pydantic import BaseModel

app = FastAPI()

# ---- 投稿主流程（同步） ----
def sync_upload_and_post_bilibili(
    video_path, cover_path, video_title, video_desc, dynamic_text, HEADERS, bili_jct
):
    import os, json

    # 1. 预上传
    filename = os.path.basename(video_path)
    filesize = os.path.getsize(video_path)
    # 预上传
    url = "https://member.bilibili.com/preupload"
    params = {
        "name": filename,
        "r": "upos",
        "profile": "ugcfx/bup",
    }
    pu = requests.get(url, params=params, headers=HEADERS).json()

    # 2. 上传元数据
    endpoint = pu["endpoint"]
    upos_uri = pu["upos_uri"]
    auth = pu["auth"]
    chunk_size = pu["chunk_size"]
    biz_id = pu["biz_id"]

    url2 = f"https:{endpoint}{upos_uri.replace('upos://', '/')}"
    params2 = {
        "uploads": "",
        "output": "json",
        "profile": "ugcfx/bup",
        "filesize": filesize,
        "partsize": chunk_size,
        "biz_id": biz_id,
    }
    headers2 = HEADERS.copy()
    headers2["X-Upos-Auth"] = auth
    pm = requests.post(url2, params=params2, headers=headers2).json()

    # 3. 分片上传
    upload_id = pm["upload_id"]
    chunks = (filesize + chunk_size - 1) // chunk_size
    etags = []
    with open(video_path, "rb") as f:
        for chunk in range(chunks):
            start = chunk * chunk_size
            f.seek(start)
            data = f.read(chunk_size)
            size = len(data)
            params3 = {
                "partNumber": chunk + 1,
                "uploadId": upload_id,
                "chunk": chunk,
                "chunks": chunks,
                "size": size,
                "start": start,
                "end": start + size,
                "total": filesize,
            }
            headers3 = HEADERS.copy()
            headers3["X-Upos-Auth"] = auth
            headers3["Content-Type"] = "application/octet-stream"
            headers3["Content-Length"] = str(size)
            resp = requests.put(url2, params=params3, headers=headers3, data=data)
            resp.raise_for_status()
            etags.append({"partNumber": chunk + 1, "eTag": ""})  # 可从resp.headers取ETag
    # 4. 结束上传
    params4 = {
        "output": "json",
        "name": filename,
        "profile": "ugcfx/bup",
        "uploadId": upload_id,
        "biz_id": biz_id,
    }
    headers4 = HEADERS.copy()
    headers4["X-Upos-Auth"] = auth
    headers4["Content-Type"] = "application/json"
    body = json.dumps({"parts": etags})
    requests.post(url2, params=params4, headers=headers4, data=body)

    # 5. 上传封面
    url_cover = "https://member.bilibili.com/x/vu/web/cover/up"
    with open(cover_path, "rb") as f:
        b64data = base64.b64encode(f.read()).decode()
    data_cover = {"csrf": bili_jct, "cover": f"data:image/jpeg;base64,{b64data}"}
    cover_ret = requests.post(url_cover, data=data_cover, headers=HEADERS).json()
    cover_url = cover_ret["data"]["url"]

    # 6. 预测分区
    url_pred = "https://member.bilibili.com/x/vupre/web/archive/types/predict"
    params_pred = {"csrf": bili_jct}
    files_pred = {"filename": (None, filename), "title": (None, video_title)}
    pred = requests.post(
        url_pred, params=params_pred, files=files_pred, headers=HEADERS
    ).json()
    tid = pred["data"][0]["id"]

    # 7. 推荐标签
    url_tag = "https://member.bilibili.com/x/vupre/web/tag/recommend"
    params_tag = {
        "subtype_id": tid,
        "title": video_title,
        "description": video_desc,
    }
    tag_ret = requests.get(url_tag, params=params_tag, headers=HEADERS).json()
    tags = ",".join([item["tag"] for item in tag_ret["data"]][:10])

    # 8. 投稿
    video_info = {
        "videos": [
            {
                "filename": upos_uri.split("/")[-1].split(".")[0],  # 无扩展名
                "title": video_title,
                "desc": "",
                "cid": biz_id,
            }
        ],
        "cover": cover_url,
        "title": video_title,
        "copyright": 1,
        "tid": tid,
        "tag": tags,
        "desc_format_id": 9999,
        "desc": video_desc,
        "recreate": -1,
        "dynamic": dynamic_text,
        "interactive": 0,
        "act_reserve_create": 0,
        "no_disturbance": 0,
        "no_reprint": 1,
        "subtitle": {"open": 0, "lan": ""},
        "dolby": 0,
        "lossless_music": 0,
        "up_selection_reply": False,
        "up_close_reply": False,
        "up_close_danmu": False,
        "web_os": 3,
        "csrf": bili_jct,
    }
    url_add = "https://member.bilibili.com/x/vu/web/add/v3"
    params_add = {"csrf": bili_jct}
    headers_add = HEADERS.copy()
    headers_add["Content-Type"] = "application/json"
    ret = requests.post(
        url_add, params=params_add, data=json.dumps(video_info), headers=headers_add
    )
    return ret.json()


async def do_list_session(
    video_title: str = Body(...),
    video_desc: str = Body(""),
    dynamic_text: str = Body(""),
    files: UploadFile = File(...),
    cover_path: UploadFile = File(...),
    user_id: int = Body(...),
):
    # 1. 异步保存文件
    file_uid = str(uuid.uuid4())
    video_name = f"{file_uid}_{files.filename}"
    cover_name = f"{file_uid}_{cover_path.filename}"
    video_path = f"/tmp/{video_name}"
    cover_file_path = f"/tmp/{cover_name}"

    async with aiofiles.open(video_path, "wb") as out_video:
        await out_video.write(await files.read())
    async with aiofiles.open(cover_file_path, "wb") as out_cover:
        await out_cover.write(await cover_path.read())

    media = await db.fetch_one(models.AgentCard, name="bilibili", user_id=user_id)
    # 2. 构造 HEADERS
    HEADERS = {
        "Cookie": f"SESSDATA={media.sessdata}; bili_jct={media.jct}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://member.bilibili.com/platform/upload/video/frame",
        "Origin": "https://member.bilibili.com",
        "Accept": "application/json, text/plain, */*",
    }

    try:
        # 3. 投递主流程（同步代码跑在线程池，避免阻塞event loop）
        ret = await asyncio.to_thread(
            sync_upload_and_post_bilibili,
            video_path,
            cover_file_path,
            video_title,
            video_desc,
            dynamic_text,
            HEADERS,
            media.bili_jct,
        )
        return ret
    except Exception as e:
        return {}
    finally:
        # 4. 删除临时文件
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(cover_file_path):
            os.remove(cover_file_path)
