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

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception:
    supabase = None

@app.get("/api/root")
def server_root_status():
    """Simple status check route to verify api engine mapping is online."""
    return {"api_engine": "online", "routing_mode": "native_rewrites"}

@app.get("/api/health")
def health_check():
    """Verifies API status and database connectivity details."""
    return {"status": "online", "database_connected": supabase is not None}

@app.post("/api/upload")
async def upload_media(file: UploadFile = File(...)):
    """Receives file chunks, pushes to Supabase Storage, and adds records to database."""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database credentials missing or invalid.")
        
    try:
        file_bytes = await file.read()
        filename = file.filename
        file_type = file.content_type or "application/octet-stream"
        bucket_name = "media-vault"
        
        # Upload binary stream directly to Supabase storage bucket
        supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": file_type, "upsert": "true"}
        )
        
        # Fetch the cloud resource URL path
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        # Insert entry metadata straight into your PostgreSQL database tracking sheet
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
    """Queries and returns the full list of media items sorted chronologically."""
    if not supabase:
        return []
    try:
        response = supabase.table("statuses").select("*").order("created_at", descending=True).execute()
        return response.data
    except Exception:
        return []

@app.post("/api/delete")
def delete_media(filenames: list[str] = Form(...)):
    """Accepts checklist arrays, deletes media files from bucket, and clears records from DB."""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection down.")
        
    try:
        bucket_name = "media-vault"
        
        # Format list parsing safely for different form submissions
        if isinstance(filenames, str):
            filenames = [filenames]
            
        # Clear raw media tracking files out of cloud storage bins
        supabase.storage.from_(bucket_name).remove(filenames)
        
        # Delete row entries from Postgres data logs
        for name in filenames:
            supabase.table("statuses").delete().eq("filename", name).execute()
            
        return {"success": True, "deleted_count": len(filenames)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
