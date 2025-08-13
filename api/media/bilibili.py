from fastapi import Body, FastAPI, Request

from service.media.bilibili import Bilibili

app = FastAPI()


@app.post("/bilibili/upload")
async def do_bilibili_upload(
    request: Request,
    video_title: str = Body(...),
    video_desc: str = Body(""),
    dynamic_text: str = Body(""),
    video_url: str = Body(...),
    cover_url: str = Body(...),
    user_id: int = Body(None),
    sessdata: str = Body(""),
    jct: str = Body(""),
):
    result = await Bilibili.do_list_session(
        video_title,
        video_desc,
        dynamic_text,
        video_url,
        cover_url,
        user_id,
        sessdata,
        jct,
    )
    return result


@app.get("/bilibili/get_url")
async def do_bilibili_get_url():
    result = {
        "video_url": "https://ark-content-generation-cn-beijing.tos-cn-beijing.volces.com/doubao-seedance-1-0-pro/02175436470018300000000000000000000ffffac155fa0d630d2.mp4?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYWJkZTExNjA1ZDUyNDc3YzhjNTM5OGIyNjBhNDcyOTQ%2F20250805%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20250805T033226Z&X-Tos-Expires=86400&X-Tos-Signature=ab4cc9a59384097076b566af5f9552e94f09fd463939e8433bf30ebdf840183d&X-Tos-SignedHeaders=host",
        "cover_url": "https://ark-content-generation-v2-cn-beijing.tos-cn-beijing.volces.com/doubao-seedream-3-0-t2i/021754468812617499895d87efaad9c7b3a5055ad65863c3c0451.jpeg?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYWJkZTExNjA1ZDUyNDc3YzhjNTM5OGIyNjBhNDcyOTQ%2F20250806%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20250806T082655Z&X-Tos-Expires=86400&X-Tos-Signature=71da2e0511058b1a5b085c2b2ab938be27f451e2decba0c839a91e0c257af297&X-Tos-SignedHeaders=host&x-tos-process=image%2Fwatermark%2Cimage_YXNzZXRzL3dhdGVybWFyay5wbmc_eC10b3MtcHJvY2Vzcz1pbWFnZS9yZXNpemUsUF8xNg%3D%3D",
    }
    return result


@app.get("/hello")
async def hello():
    return {"message": "Hello World"}
