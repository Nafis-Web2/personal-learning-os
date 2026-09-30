
from fastapi.testclient import TestClient
from app.main import app
def test_dev_bootstrap_is_opt_in(monkeypatch):
 monkeypatch.delenv('LEARNING_OS_DEV_BOOTSTRAP',raising=False)
 with TestClient(app) as c: assert c.post('/dev/bootstrap').status_code==404
def test_dev_bootstrap_creates_reusable_user(monkeypatch):
 monkeypatch.setenv('LEARNING_OS_DEV_BOOTSTRAP','1')
 with TestClient(app) as c:
  a=c.post('/dev/bootstrap');b=c.post('/dev/bootstrap')
  assert a.status_code==200 and a.json()['id']==b.json()['id']
