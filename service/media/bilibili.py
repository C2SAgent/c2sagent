import base64
import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).parent.parent.parent))

import asyncio
from core.db.base import DatabaseManager
from model import model_agent as models

from mcp.server.fastmcp import FastMCP
from api.apps.agent.config import settings

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)


mcp_server = FastMCP("Bilibili", port=3001)


# =================================================信息
class Bilibili:
    @staticmethod
    def sync_upload_and_post_bilibili(
        video_url: str,
        cover_url: str,
        video_title: str,
        video_desc: str,
        dynamic_text: str,
        HEADERS: dict,
        bili_jct: str,
    ):
        import os, json, tempfile

        # 1. 下载视频文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            video_path = tmp_video.name
            video_response = requests.get(video_url, stream=True)
            for chunk in video_response.iter_content(chunk_size=8192):
                tmp_video.write(chunk)

        # 2. 下载封面文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_cover:
            cover_path = tmp_cover.name
            cover_response = requests.get(cover_url)
            tmp_cover.write(cover_response.content)

        try:
            # 3. 预上传
            filename = os.path.basename(video_url.split("?")[0])  # 从URL获取文件名
            filesize = os.path.getsize(video_path)
            url = "https://member.bilibili.com/preupload"
            params = {
                "name": filename,
                "r": "upos",
                "profile": "ugcfx/bup",
            }
            pu = requests.get(url, params=params, headers=HEADERS).json()

            # 4. 上传元数据
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

            # 5. 分片上传
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
                    resp = requests.put(
                        url2, params=params3, headers=headers3, data=data
                    )
                    resp.raise_for_status()
                    etags.append(
                        {"partNumber": chunk + 1, "eTag": ""}
                    )  # 可从resp.headers取ETag

            # 6. 结束上传
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

            # 7. 上传封面
            url_cover = "https://member.bilibili.com/x/vu/web/cover/up"
            with open(cover_path, "rb") as f:
                b64data = base64.b64encode(f.read()).decode()
            data_cover = {
                "csrf": bili_jct,
                "cover": f"data:image/jpeg;base64,{b64data}",
            }
            cover_ret = requests.post(
                url_cover, data=data_cover, headers=HEADERS
            ).json()
            cover_url = cover_ret["data"]["url"]

            # 8. 预测分区
            url_pred = "https://member.bilibili.com/x/vupre/web/archive/types/predict"
            params_pred = {"csrf": bili_jct}
            files_pred = {"filename": (None, filename), "title": (None, video_title)}
            pred = requests.post(
                url_pred, params=params_pred, files=files_pred, headers=HEADERS
            ).json()
            tid = pred["data"][0]["id"]

            # 9. 推荐标签
            url_tag = "https://member.bilibili.com/x/vupre/web/tag/recommend"
            params_tag = {
                "subtype_id": tid,
                "title": video_title,
                "description": video_desc,
            }
            tag_ret = requests.get(url_tag, params=params_tag, headers=HEADERS).json()
            tags = ",".join([item["tag"] for item in tag_ret["data"]][:10])

            # 10. 投稿
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
                url_add,
                params=params_add,
                data=json.dumps(video_info),
                headers=headers_add,
            )
            return ret.json()
        finally:
            # 清理临时文件
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(cover_path):
                os.remove(cover_path)

    @mcp_server.tool()
    @staticmethod
    async def do_list_session(
        video_title: str,
        video_desc: str,
        dynamic_text: str,
        video_url: str,  # 改为OSS视频链接
        cover_url: str,  # 改为OSS封面链接
        user_id: int,
        sessdata: str,
        jct: str,
    ):
        """do_list_session

        Args:
            video_title (str): 这里为视频标题
            video_desc (str): 这里为视频描述
            dynamic_text (str): 这里是动态文本
            video_url (str): 这里是视频的oss链接，你需要调用视频生成工具来获取这个链接
            cover_url (str): 这里是封面的oss链接，你需要调用图片生成工具来获取这个链接
            user_id (int): 这里为用户ID
            以上都为必填参数

        Returns:
            {'code': 0, 'message': '0', 'ttl': 1, 'data': {'aid': 114974110256368, 'bvid': 'BV1KttjzjE2D'}}
        """
        if user_id:
            media = await db.fetch_one(
                models.AgentCard, name="bilibili", user_id=user_id
            )
            if not media:
                return {"code": -1, "message": "未找到对应的B站账号配置"}

        else:

            class Media:
                sessdata: str = ""  # "61ea3e83%2C1769495855%2C1698b%2A72CjDYCVqgH0H3lGnIyHPfwDOTGuGupmjdn1H9mXCZGLQgayD2lnQ2r5OsjaOhhsi2q08SVlpaVVE2R2tqX0ZOUEFWbEVXOXdmZWM2bEgyUzFkQlF2aTdSZ3Qxc2RBR0RNcld1VkpTbnY5Rmpfc204bjBDM0p3MTZXakh1OU9XZ3BEbzNJcGwya2lRIIEC"
                jct: str = ""  # "7ed34b88269f819f3086dbe067991e0e"

            media = Media()
            media.sessdata = sessdata
            media.jct = jct

        print(media.sessdata)
        print(media.jct)
        # 构造 HEADERS
        HEADERS = {
            "Cookie": f"SESSDATA={media.sessdata}; bili_jct={media.jct}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://member.bilibili.com/platform/upload/video/frame",
            "Origin": "https://member.bilibili.com",
            "Accept": "application/json, text/plain, */*",
        }

        try:
            # 投递主流程（同步代码跑在线程池，避免阻塞event loop）
            ret = await asyncio.to_thread(
                Bilibili.sync_upload_and_post_bilibili,
                video_url,
                cover_url,
                video_title,
                video_desc,
                dynamic_text,
                HEADERS,
                media.jct,
            )
            return ret
        except Exception as e:
            return {"code": -1, "message": f"投稿失败: {str(e)}"}


async def main():

    video_title = "测试投稿"
    video_desc = "测试投稿"
    dynamic_text = "测试投稿"
    video_url = "https://ark-content-generation-cn-beijing.tos-cn-beijing.volces.com/doubao-seedance-1-0-pro/02175436470018300000000000000000000ffffac155fa0d630d2.mp4?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYWJkZTExNjA1ZDUyNDc3YzhjNTM5OGIyNjBhNDcyOTQ%2F20250805%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20250805T033226Z&X-Tos-Expires=86400&X-Tos-Signature=ab4cc9a59384097076b566af5f9552e94f09fd463939e8433bf30ebdf840183d&X-Tos-SignedHeaders=host"
    cover_url = "https://ark-content-generation-v2-cn-beijing.tos-cn-beijing.volces.com/doubao-seedream-3-0-t2i/021754468812617499895d87efaad9c7b3a5055ad65863c3c0451.jpeg?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYWJkZTExNjA1ZDUyNDc3YzhjNTM5OGIyNjBhNDcyOTQ%2F20250806%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20250806T082655Z&X-Tos-Expires=86400&X-Tos-Signature=71da2e0511058b1a5b085c2b2ab938be27f451e2decba0c839a91e0c257af297&X-Tos-SignedHeaders=host&x-tos-process=image%2Fwatermark%2Cimage_YXNzZXRzL3dhdGVybWFyay5wbmc_eC10b3MtcHJvY2Vzcz1pbWFnZS9yZXNpemUsUF8xNg%3D%3D"
    user_id = 35
    sessdata = "61ea3e83%2C1769495855%2C1698b%2A72CjDYCVqgH0H3lGnIyHPfwDOTGuGupmjdn1H9mXCZGLQgayD2lnQ2r5OsjaOhhsi2q08SVlpaVVE2R2tqX0ZOUEFWbEVXOXdmZWM2bEgyUzFkQlF2aTdSZ3Qxc2RBR0RNcld1VkpTbnY5Rmpfc204bjBDM0p3MTZXakh1OU9XZ3BEbzNJcGwya2lRIIEC"
    jct = "7ed34b88269f819f3086dbe067991e0e"
    result = await Bilibili.do_list_session(
        video_title,
        video_desc,
        dynamic_text,
        video_url,
        cover_url,
        user_id="",
        sessdata=sessdata,
        jct=jct,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())

# def main():
#     mcp_server.run(transport="streamable-http")
