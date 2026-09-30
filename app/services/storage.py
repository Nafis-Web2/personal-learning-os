from pathlib import Path
from uuid import uuid4
ALLOWED={"image/jpeg","image/png","image/webp","application/pdf"}
MAX_BYTES=15*1024*1024
class LocalStorage:
    def __init__(self, root:str="var/uploads"): self.root=Path(root)
    def put(self, *, user_id:str, content_type:str, data:bytes)->dict:
        if content_type not in ALLOWED: raise ValueError("Unsupported file type")
        if len(data)>MAX_BYTES: raise ValueError("File exceeds 15 MB")
        ext={"image/jpeg":".jpg","image/png":".png","image/webp":".webp","application/pdf":".pdf"}[content_type]
        key=f"{user_id}/{uuid4()}{ext}"; path=self.root/key; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
        return {"storage_key":key,"size_bytes":len(data)}
storage=LocalStorage()
