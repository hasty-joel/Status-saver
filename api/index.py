import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

# Safe initialization of Supabase Client
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

# --- SERVE FULL FRONTEND ENGINE DIRECTLY FROM MEMORY ---
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MATRIX_VAULT // Core Control</title>
        <style>
            :root {
                --neon-green: #00ff66;
                --neon-blue: #00f0ff;
                --dark-bg: #0a0a0c;
                --panel-bg: #12121a;
                --border-color: #222230;
            }
            body {
                background-color: var(--dark-bg);
                color: #ffffff;
                font-family: 'Courier New', Courier, monospace;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
            }
            header {
                border-bottom: 2px solid var(--neon-blue);
                padding-bottom: 10px;
                margin-bottom: 30px;
            }
            h1 {
                color: var(--neon-green);
                margin: 0;
                text-shadow: 0 0 10px rgba(0, 255, 102, 0.3);
            }
            .upload-card {
                background-color: var(--panel-bg);
                border: 1px solid var(--neon-blue);
                padding: 20px;
                border-radius: 4px;
                margin-bottom: 30px;
            }
            .drop-zone {
                border: 2px dashed #333344;
                padding: 30px;
                text-align: center;
                cursor: pointer;
                transition: 0.3s;
            }
            .drop-zone:hover {
                border-color: var(--neon-green);
                background: rgba(0, 255, 102, 0.02);
            }
            .batch-actions {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
                background: #111116;
                padding: 15px;
                border: 1px solid var(--border-color);
                align-items: center;
            }
            button {
                background: transparent;
                color: var(--neon-blue);
                border: 1px solid var(--neon-blue);
                padding: 8px 16px;
                font-family: monospace;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover {
                background: rgba(0, 240, 255, 0.1);
                box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
            }
            button.danger {
                color: #ff3366;
                border-color: #ff3366;
            }
            button.danger:hover {
                background: rgba(255, 51, 102, 0.1);
                box-shadow: 0 0 10px rgba(255, 51, 102, 0.3);
            }
            .vault-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                gap: 20px;
            }
            .asset-card {
                background: var(--panel-bg);
                border: 1px solid var(--border-color);
                border-radius: 4px;
                overflow: hidden;
                position: relative;
                transition: 0.2s;
                cursor: pointer;
            }
            .asset-card.selected {
                border-color: var(--neon-green) !important;
                box-shadow: 0 0 15px rgba(0, 255, 102, 0.3);
            }
            .preview-box {
                width: 100%;
                height: 150px;
                background: #000;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                pointer-events: none;
            }
            .preview-box img, .preview-box video {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .card-meta {
                padding: 12px;
                font-size: 13px;
                background: rgba(0,0,0,0.3);
                pointer-events: none;
            }
            .filename-text {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .selection-indicator {
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 10;
                background: rgba(0, 0, 0, 0.85);
                color: #fff;
                border: 1px solid #333;
                width: 22px;
                height: 22px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                border-radius: 3px;
                transition: 0.2s;
            }
            .asset-card.selected .selection-indicator {
                background: var(--neon-green);
                border-color: var(--neon-green);
                color: #000;
            }
            .counter-badge {
                margin-left: auto;
                color: var(--neon-green);
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>⚡ MATRIX_VAULT // CORE INTERFACE</h1>
                <p>System Layer: Serving Directly From Python Core Memory</p>
            </header>

            <div class="upload-card">
                <div class="drop-zone" onclick="document.getElementById('filePicker').click()">
                    <p>⚙️ CLICK OR DRAG ASSETS HERE TO INJECT INTO THE CLOUD ARRAY ⚙️</p>
                    <input type="file" id="filePicker" style="display:none" onchange="uploadAsset(this.files[0])">
                </div>
                <div id="statusReport" style="margin-top:10px; color:var(--neon-green)"></div>
            </div>

            <h2>📦 ARCHIVED ASSETS</h2>
            
            <div class="batch-actions">
                <button onclick="toggleSelectAll()">Select/Deselect All</button>
                <button onclick="downloadSelected()">📥 Download Selected</button>
                <button class="danger" onclick="deleteSelected()">🗑️ Delete Selected</button>
                <div class="counter-badge" id="counterDisplay">Selected: 0</div>
            </div>

            <div class="vault-grid" id="vaultGrid"></div>
        </div>

        <script>
            let assetRegistry = [];
            let selectedAssets = new Set();

            async function fetchVaultFeed() {
                try {
                    const response = await fetch('/api/media');
                    const rawData = await response.json();
                    
                    assetRegistry = rawData.map((item, index) => {
                        const filename = item.filename || item.file_name || item.name || item.id || `asset_${index}`;
                        const url = item.url || item.public_url || item.file_url;
                        const file_type = item.file_type || item.type || (url && url.includes('.mp4') ? 'video/mp4' : 'image/jpeg');
                        return { ...item, filename, url, file_type };
                    });
                    
                    renderVaultGrid();
                } catch (err) {
                    console.error("Failed to query API architecture:", err);
                }
            }

            function renderVaultGrid() {
                const grid = document.getElementById('vaultGrid');
                grid.innerHTML = '';

                if (!assetRegistry || assetRegistry.length === 0) {
                    grid.innerHTML = '<p style="color:#666; grid-column: 1/-1;">No records found inside database repository.</p>';
                    updateCounter();
                    return;
                }

                assetRegistry.forEach(asset => {
                    const isSelected = selectedAssets.has(asset.filename);
                    const card = document.createElement('div');
                    card.className = `asset-card ${isSelected ? 'selected' : ''}`;
                    card.onclick = () => toggleAssetSelection(asset.filename);
                    
                    let visualPreview = `<img src="${asset.url}" alt="asset">`;
                    if (asset.file_type && asset.file_type.includes('video')) {
                        visualPreview = `<video src="${asset.url}" muted playsinline></video>`;
                    }

                    card.innerHTML = `
                        <div class="selection-indicator">${isSelected ? '✓' : ''}</div>
                        <div class="preview-box">
                            ${visualPreview}
                        </div>
                        <div class="card-meta">
                            <div class="filename-text" title="${asset.filename}">${asset.filename}</div>
                        </div>
                    `;
                    grid.appendChild(card);
                });
                
                updateCounter();
            }

            function toggleAssetSelection(filename) {
                if (selectedAssets.has(filename)) {
                    selectedAssets.delete(filename);
                } else {
                    selectedAssets.add(filename);
                }
                renderVaultGrid();
            }

            function toggleSelectAll() {
                if (selectedAssets.size === assetRegistry.length) {
                    selectedAssets.clear();
                } else {
                    selectedAssets = new Set(assetRegistry.map(a => a.filename));
                }
                renderVaultGrid();
            }

            function updateCounter() {
                document.getElementById('counterDisplay').innerText = `Selected: ${selectedAssets.size}`;
            }

            async function uploadAsset(file) {
                if (!file) return;
                const feedback = document.getElementById('statusReport');
                feedback.innerText = "⚡ TRANSMITTING ASSET ARRAY BINARIES...";

                const packet = new FormData();
                packet.append('file', file);

                try {
                    const response = await fetch('/api/upload', { method: 'POST', body: packet });
                    if (response.ok) {
                        feedback.innerText = "✅ ASSET STORED SUCCESSFULLY.";
                        fetchVaultFeed();
                    } else {
                        feedback.innerText = "❌ PIPELINE REJECTED ASSET PAYLOAD.";
                    }
                } catch (err) {
                    feedback.innerText = "❌ PLATFORM TRANSACTION FAULT.";
                }
            }

            async function downloadSelected() {
                if (selectedAssets.size === 0) {
                    alert("Select at least one item first.");
                    return;
                }

                const targets = assetRegistry.filter(a => selectedAssets.has(a.filename));
                
                for (const item of targets) {
                    try {
                        const res = await fetch(item.url);
                        const blob = await res.blob();
                        const link = document.createElement('a');
                        link.href = URL.createObjectURL(blob);
                        link.download = item.filename;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    } catch (e) {
                        window.open(item.url, '_blank');
                    }
                }
            }

            async function deleteSelected() {
                if (selectedAssets.size === 0) {
                    alert("No items selected for removal.");
                    return;
                }

                if (!confirm(`Purge ${selectedAssets.size} asset records permanently?`)) return;

                const feedback = document.getElementById('statusReport');
                feedback.innerText = "⚙️ PURGING DATA NODES...";

                const packet = new FormData();
                // Send comma-separated string to avoid FastAPI array form issues
                const filenamesArray = Array.from(selectedAssets);
                packet.append('filenames_str', filenamesArray.join(','));

                try {
                    const res = await fetch('/api/delete', { method: 'POST', body: packet });
                    if (res.ok) {
                        feedback.innerText = "🗑️ DELETION SEQUENCE COMPLETED SUCCESSFULLY.";
                        selectedAssets.clear();
                        fetchVaultFeed();
                    } else {
                        feedback.innerText = "❌ RUNTIME FAILED TO DROP TARGETS.";
                    }
                } catch (err) {
                    feedback.innerText = "❌ COMM LINK DROP ERROR.";
                }
            }

            // Bootstrap application
            fetchVaultFeed();
        </script>
    </body>
    </html>
    """
# -------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {"status": "online", "database_connected": supabase is not None}

@app.post("/api/upload")
async def upload_media(file: UploadFile = File(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection configuration missing.")
        
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
def delete_media(filenames_str: str = Form(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection down.")
        
    try:
        bucket_name = "media-vault"
        
        # Split string back into a clean list of individual items
        filenames = [name.strip() for name in filenames_str.split(",") if name.strip()]
        if not filenames:
            return {"success": True, "deleted_count": 0}
            
        supabase.storage.from_(bucket_name).remove(filenames)
        
        for name in filenames:
            supabase.table("statuses").delete().or_(f"filename.eq.{name},file_name.eq.{name}").execute()
            
        return {"success": True, "deleted_count": len(filenames)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
