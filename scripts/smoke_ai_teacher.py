
import os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
dbfile=os.path.join(tempfile.gettempdir(),"learning_os_ai_smoke.db")
try:os.remove(dbfile)
except FileNotFoundError:pass
os.environ["DATABASE_URL"]="sqlite:///"+dbfile
os.environ["AI_PROVIDER"]="mock"
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as c:
    u=c.post("/users",json={"display_name":"AI Smoke","timezone":"America/New_York"})
    assert u.status_code==200,u.text
    uid=u.json()["id"]
    r=c.post(f"/users/{uid}/teacher/live",json={"mode":"teach","topic":"Python loops","learner_input":"I know a loop repeats code","help_level":2})
    assert r.status_code==200,r.text
    assert r.json()["provider"]=="mock"
    a=c.post(f"/users/{uid}/teacher/live",json={"mode":"assessment","topic":"Python loops","learner_input":"","help_level":5})
    assert a.status_code==200,a.text
    assert a.json()["help_level"]==0
print("AI Teacher endpoint smoke test passed.")
