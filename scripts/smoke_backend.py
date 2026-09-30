
import os, tempfile, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),"learning_os_smoke.db")
try: os.remove(dbfile)
except FileNotFoundError: pass
os.environ["DATABASE_URL"]="sqlite:///"+dbfile

from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    assert client.get("/health").status_code == 200
    status=client.get("/integration/status")
    assert status.status_code == 200 and status.json()["phase"]=="full_product_integration"

    u=client.post("/users",json={"display_name":"Smoke Test","timezone":"America/New_York"})
    assert u.status_code==200, u.text
    uid=u.json()["id"]

    today=client.get(f"/users/{uid}/today/next")
    assert today.status_code==200, today.text
    assert "next_action" in today.json()

    teacher=client.post(f"/users/{uid}/teacher/turn",params={"mode":"teach","topic":"Python loops","help_level":0})
    assert teacher.status_code==200, teacher.text

    personal=client.post(f"/users/{uid}/personalization/preview",params={"preferred":"visual"})
    assert personal.status_code==200, personal.text
    assert personal.json()["mastery_standards_changed"] is False

print("Backend HTTP smoke test passed.")
