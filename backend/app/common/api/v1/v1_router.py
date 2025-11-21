"""
API v1 라우터

모든 v1 API 엔드포인트를 여기에 등록합니다.
"""

from fastapi import APIRouter

# API 라우터 생성
v1_router = APIRouter()

# 도메인별 라우터 등록
# prefix와 tags는 각 도메인의 api.py에서 이미 정의됨
# api_router.include_router(page_base_link_crawling_router)
