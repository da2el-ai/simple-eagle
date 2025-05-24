from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import os
import requests
from modules.eagle_api import eagle_api

class ImageRequest(BaseModel):
    path: str

app = FastAPI()

# APIルーター
from fastapi import APIRouter
api_router = APIRouter()

@api_router.get("/recent")
async def get_recent_images():
    """
    Eagle APIから最新の画像一覧を取得
    """
    try:
        return eagle_api.get_recent_images()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/folders")
async def get_folders():
    """
    Eagle APIからフォルダ一覧を取得
    """
    try:
        return eagle_api.get_folder_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/get_thumbnail_image")
async def get_thumbnail_image(id):
    """
    アイテムIDからサムネイル画像を取得
    """
    try:
        result = eagle_api.get_thumbnail_image(id)
        if result is None:
            raise HTTPException(status_code=404, detail="Image not found")
        
        content, content_type = result
        return Response(content=content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/get_image")
async def get_image(id: str, ext: str = "png", max_file_size: int = 1480, quality: int = 85):
    """
    アイテムIDからオリジナル画像を取得
    - max_file_size: 最大容量をKB単位で指定。これ以上ならjpeg圧縮をかける。0なら圧縮しない
    - quality: jpeg圧縮率。0または無指定なら85を適用
    """
    try:
        # qualityが0の場合は85に設定
        if quality == 0:
            quality = 85
            
        result = eagle_api.get_image(id, ext, max_file_size, quality)
        if result is None:
            raise HTTPException(status_code=404, detail="Image not found")
        
        content, content_type = result
        return Response(content=content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターをインクルード
app.include_router(api_router, prefix="/api/eagle")

# 静的ファイルのマウント
app.mount("/", StaticFiles(directory="dist", html=True), name="static")
