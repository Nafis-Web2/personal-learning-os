
import os,sys,subprocess
os.environ.setdefault("LEARNING_OS_DEV_BOOTSTRAP","1")
os.environ.setdefault("AI_PROVIDER","mock")
print("Starting Learning OS API on http://localhost:8000")
print("In another terminal: cd frontend && npm install && npm run dev")
subprocess.run([sys.executable,"-m","uvicorn","app.main:app","--reload","--host","127.0.0.1","--port","8000"],check=False)
