import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

app = FastAPI()

# Enable cross-origin calls safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase Client using Vercel Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    supabase: Client = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

@app.get("/api/health")
def health_check():
    return {"status": "online", "database_connected": supabase is not None}

@app.post("/api/upload")
async def upload_media(file: UploadFile = File(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database credentials missing or invalid.")
        
    try:
        file_bytes = await file.read()
        filename = file.filename
        file_type = file.content_type or "application/octet-stream"
        
        bucket_name = "media-vault"
        
        # Upload raw binary file straight into your Supabase Storage Bucket
        supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": file_type, "upsert": "true"}
        )
        
        # Grab the permanent public cloud link to that file
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        # Save file reference information down into your PostgreSQL Table
        db_data = {
            "filename": filename,
            "file_type": file_type,
            "url": public_url
        }
        supabase.table("statuses").insert(db_data).execute()
        
        return {"success": True, "url": public_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/media")
def fetch_media():
    if not supabase:
        return []
    try:
        response = supabase.table("statuses").select("*").order("created_at", descending=True).execute()
        return response.data
    except Exception:
        return []

@app.post("/api/delete")
def delete_media(filenames: list[str] = Form(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection down.")
        
    try:
        bucket_name = "media-vault"
        # FIXED: Corrected .from_image() to native bucket caller .from_()
        supabase.storage.from_(bucket_name).remove(filenames)
        
        for name in filenames:
            supabase.table("statuses").delete().eq("filename", name).execute()
            
        return {"success": True, "deleted_count": len(filenames)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
