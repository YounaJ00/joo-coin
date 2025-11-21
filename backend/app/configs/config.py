"""
애플리케이션 설정 관리

.env 파일에서 환경 변수를 로드하고 검증합니다.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스

    .env 파일에서 환경 변수를 로드하고 검증합니다.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 애플리케이션
    APP_NAME: str = "DevDeb API"
    APP_VERSION: str = "1.0.0"

    # GPT API
    OPENAI_API_KEY: str = ""  # .env에서 로드됨

    # UPBIT API
    UPBIT_ACCESS_KEY: str = ""  # .env에서 로드됨
    UPBIT_SECRET_KEY: str = ""  # .env에서 로드됨

    # 데이터베이스 (MySQL)
    DATABASE_URL: str = ""  # .env에서 로드됨
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # CORS (쉼표로 구분된 문자열, 예: "http://localhost:3000,http://localhost:8080")
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS 오리진을 리스트로 반환"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


# 전역 설정 인스턴스
settings = Settings()
