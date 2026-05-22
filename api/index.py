import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
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

# --- SERVE FRONTEND DIRECTLY FROM MEMORY ---
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEON_VAULT // Status Saver</title>
        <style>
            :root {
                --neon-green: #00ff66;
                --neon-blue: #00f0ff;
                --dark-bg: #0a0a0c;
                --terminal-gray: #1a1a24;
            }
            body {
                background-color: var(--dark-bg);
                color: #ffffff;
                font-family: 'Courier New', Courier, monospace;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .terminal-container {
                width: 100%;
                max-width: 800px;
                background-color: var(--terminal-gray);
                border: 2px solid var(--neon-blue);
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
                border-radius: 8px;
                padding: 20px;
                box-sizing: border-box;
            }
            h1 {
                color: var(--neon-green);
                text-shadow: 0 0 10px rgba(0, 255, 102, 0.4);
                margin-top: 0;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 10px;
                background: rgba(0, 255, 102, 0.1);
                border: 1px solid var(--neon-green);
                color: var(--neon-green);
                font-size: 12px;
                margin-bottom: 20px;
            }
            .upload-zone {
                border: 2px dashed var(--neon-green);
                padding: 30px;
                text-align: center;
                cursor: pointer;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            .upload-zone:hover {
                background: rgba(0, 255, 102, 0.05);
                box-shadow: 0 0 15px rgba(0, 255, 102, 0.2);
            }
            input[type="file"] {
                display: none;
            }
            .media-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .media-card {
                background: #111116;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 10px;
                position: relative;
            }
            .media-card img, .media-card video {
                width: 100%;
                height: 120px;
                object-fit: cover;
                border-radius: 2px;
            }
            .delete-btn {
                background: #ff3366;
                color: white;
                border: none;
                padding: 4px 8px;
                font-family: monospace;
                cursor: pointer;
                width: 100%;
                margin-top: 8px;
            }
        </style>
    </head>
    <body>
        <div class="terminal-container">
            <h1>⚡ NEON_VAULT v2.0</h1>
            <div class="status-badge">SYSTEM STATE: ONLINE</div>
            
            <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                <p>⚡ DRAG & DROP OR CLICK TO INJECT MEDIA ASSETS ⚡</p>
                <input type="file" id="fileInput" onchange="handleUpload(this.files[0])">
            </div>

            <div id="uploadStatus"></div>
            <h3>📂 ARCHIVED STATUS FEED</h3>
            <div class="media-grid" id="mediaGrid"></div>
        </div>

        <script>
            async function loadMedia() {
                try {
                    const res = await fetch('/api/media');
                    const data = await res.json();
                    const grid = document.getElementById('mediaGrid');
                    grid.innerHTML = '';
                    
                    data.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'media-card';
                        
                        let element = `<img src="${item.url}" alt="media">`;
                        if (item.file_type && item.file_type.includes('video')) {
                            element = `<video src="${item.url}" controls></video>`;
                        }
                        
                        card.innerHTML = `
                            ${element}
                            <button class="delete-btn" onclick="deleteMedia('${item.filename}')">DELETE</button>
                        `;
                        grid.appendChild(card);
                    });
                } catch (err) {
                    console.error("Failed to load feed", err);
                }
            }

            async function handleUpload(file) {
                if (!file) return;
                const statusDiv = document.getElementById('uploadStatus');
                statusDiv.innerText = "⚡ INJECTING ASSET INTO REPOSITORY...";
                
                const formData = new FormData();
                formData.append('file', file);

                try {
                    const res = await fetch('/api/upload', { method: 'POST', body: formData });
                    if (res.ok) {
                        statusDiv.innerText = "✅ ASSET INJECTED SUCCESSFULY.";
                        loadMedia();
                    } else {
                        statusDiv.innerText = "❌ UPLOAD RUNTIME CRASH.";
                    }
                } catch (err) {
                    statusDiv.innerText = "❌ PIPELINE ERROR.";
                }
            }

            async function deleteMedia(filename) {
                if (!confirm("Confirm asset deletion?")) return;
                const formData = new FormData();
                formData.append('filenames', filename);

                try {
                    await fetch('/api/delete', { method: 'POST', body: formData });
                    loadMedia();
                } catch (err) {
                    console.error("Delete sequence failed", err);
                }
            }

            // Bootstrap application
            loadMedia();
        </script>
    </body>
    </html>
    """
# -------------------------------------------

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
        
        supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": file_type, "upsert": "true"}
        )
        
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
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
        supabase.storage.from_(bucket_name).remove(filenames)
        
        # FastAPI handles form array fields nicely; handle singular strings safely
        if isinstance(filenames, str):
            filenames = [filenames]
            
        for name in filenames:
            supabase.table("statuses").delete().eq("filename", name).execute()
            
        return {"success": True, "deleted_count": len(filenames)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
