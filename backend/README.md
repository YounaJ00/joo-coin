# Backend

## Alembic 마이그레이션

### 마이그레이션 적용
```bash
uv run alembic upgrade head
```

### 마이그레이션 롤백
```bash
uv run alembic downgrade -1
```

### 새 마이그레이션 생성
```bash
uv run alembic revision --autogenerate -m "설명"
```
