
from app.core.config import allowed_origins,is_production
def test_origins_are_env_driven(monkeypatch):
 monkeypatch.setenv('ALLOWED_ORIGINS','https://learn.example,https://preview.example/')
 assert allowed_origins()==['https://learn.example','https://preview.example']
def test_production_flag(monkeypatch):
 monkeypatch.setenv('APP_ENV','production')
 assert is_production()
def test_dev_bootstrap_disabled_in_production(monkeypatch):
 from fastapi.testclient import TestClient
 from app.main import app
 monkeypatch.setenv('APP_ENV','production');monkeypatch.setenv('LEARNING_OS_DEV_BOOTSTRAP','1')
 with TestClient(app) as c: assert c.post('/dev/bootstrap').status_code==404
