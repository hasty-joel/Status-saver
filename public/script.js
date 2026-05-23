let assetRegistry = [];
let selectedAssets = new Set();

async function fetchVaultFeed() {
    try {
        const response = await fetch('/api/media');
        assetRegistry = await response.json();
        renderVaultGrid();
    } catch (err) {
        console.error("Failed to query API architecture:", err);
    }
}

function renderVaultGrid() {
    const grid = document.getElementById('vaultGrid');
    grid.innerHTML = '';

    if (assetRegistry.length === 0) {
        grid.innerHTML = '<p style="color:#666; grid-column: 1/-1;">No records found inside database repository.</p>';
        return;
    }

    assetRegistry.forEach(asset => {
        const isSelected = selectedAssets.has(asset.filename);
        const card = document.createElement('div');
        card.className = `asset-card ${isSelected ? 'selected' : ''}`;
        
        let visualPreview = `<img src="${asset.url}" alt="asset">`;
        if (asset.file_type && asset.file_type.includes('video')) {
            visualPreview = `<video src="${asset.url}" muted playsinline></video>`;
        }

        card.innerHTML = `
            <div class="checkbox-container">
                <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="toggleAssetSelection('${asset.filename}')">
            </div>
            <div class="preview-box">
                ${visualPreview}
            </div>
            <div class="card-meta">
                <div class="filename-text" title="${asset.filename}">${asset.filename}</div>
            </div>
        `;
        grid.appendChild(card);
    });
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

async function uploadAsset(file) {
    if (!file) return;
    const feedback = document.getElementById('statusReport');
    feedback.innerText = "⚡ TRANSMITTING ASSET ARRAY BINARIES...";

    const packet = new FormData();
    packet.append('file', file);

    try {
        const response = await fetch('/api/upload', { method: 'POST', body: packet });
        if (response.ok) {
            feedback.innerText = "✅ ASSET STREAM STORED IN SUPABASE DATASTRUCTURES.";
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
        alert("Select at least one checklist item first.");
        return;
    }

    const targets = assetRegistry.filter(a => selectedAssets.has(a.filename));
    
    for (const item of targets) {
        try {
            // Fetch file as blob to force instant browser system downloads instead of opening a browser tab
            const res = await fetch(item.url);
            const blob = await res.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = item.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (e) {
            // Fallback download alternative
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

    // Format array variables for standard multpart form encoding architectures
    const packet = new FormData();
    selectedAssets.forEach(name => {
        packet.append('filenames', name);
    });

    try {
        const res = await fetch('/api/delete', { method: 'POST', body: packet });
        if (res.ok) {
            feedback.innerText = "🗑️ DELETION SEQUENCE COMPLETED SUCCESSFULLY.";
            selectedAssets.clear();
            fetchVaultFeed();
        } else {
            feedback.innerText = "❌ RUNTIME FAILED TO DROP TABLE TARGETS.";
        }
    } catch (err) {
        feedback.innerText = "❌ COMM LINK DROP ERROR.";
    }
}

// Initial application startup
fetchVaultFeed();
