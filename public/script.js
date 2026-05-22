// Global State Management Matrix
let mediaItems = [];
let selectedFiles = new Set();

// DOM Element Targets
const matrixContainer = document.getElementById('matrixContainer');
const emptyState = document.getElementById('emptyState');
const itemCount = document.getElementById('itemCount');
const selectedCount = document.getElementById('selectedCount');
const actionBar = document.getElementById('actionBar');
const selectAllBtn = document.getElementById('selectAllBtn');
const mediaUpload = document.getElementById('mediaUpload');
const uploadStatus = document.getElementById('uploadStatus');
const themeToggle = document.getElementById('themeToggle');

// 1. DYNAMIC REPOSITORY RENDER MATRIX WITH INTERLEAVED AD SLIDERS
function renderMatrix() {
    matrixContainer.innerHTML = '';
    
    if (mediaItems.length === 0) {
        emptyState.classList.remove('hidden');
        itemCount.textContent = '(0)';
        return;
    }
    
    emptyState.classList.add('hidden');
    itemCount.textContent = `(${mediaItems.length})`;
    
    // Chunk media items into sets of 10 to inject Ad Navbars between blocks seamlessly
    const chunkSize = 10;
    for (let i = 0; i < mediaItems.length; i += chunkSize) {
        const chunk = mediaItems.slice(i, i + chunkSize);
        
        // A. Generate a 4-column fluid responsive grid for the current 10 items
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-2 md:grid-cols-4 gap-4';
        
        chunk.forEach(item => {
            const card = document.createElement('div');
            card.className = `relative rounded-xl overflow-hidden bg-slate-900 border transition-all group cursor-pointer ${
                selectedFiles.has(item.filename) ? 'border-cyberCyan scale-98 shadow-md' : 'border-slate-800 hover:border-slate-700'
            }`;
            
            // Render conditionally depending on whether file is an Image or MP4 Video
            const isVideo = item.file_type.includes('video') || item.filename.endsWith('.mp4');
            const mediaTag = isVideo 
                ? `<video src="${item.url}" class="w-full h-40 object-cover pointer-events-none" muted loop></video>`
                : `<img src="${item.url}" alt="${item.filename}" class="w-full h-40 object-cover pointer-events-none" loading="lazy">`;
                
            card.innerHTML = `
                ${mediaTag}
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-2 flex items-end">
                    <p class="text-[10px] font-mono truncate text-slate-300 w-full">${item.filename}</p>
                </div>
                <!-- Selection Target Overlay -->
                <div class="absolute top-2 left-2 w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                    selectedFiles.has(item.filename) 
                        ? 'bg-cyberCyan border-cyberCyan text-slate-950 font-bold text-xs' 
                        : 'bg-black/40 border-slate-500'
                }">
                    ${selectedFiles.has(item.filename) ? '✓' : ''}
                </div>
            `;
            
            // Toggle item state on click
            card.addEventListener('click', () => toggleSelection(item.filename));
            grid.appendChild(card);
        });
        
        matrixContainer.appendChild(grid);
        
        // B. Inject a Horizontal Ad Slider Navbar after every 10 items if more items remain
        if (i + chunkSize < mediaItems.length || mediaItems.length > 10) {
            const adNavbar = document.createElement('div');
            adNavbar.className = 'bg-slate-950 border border-dashed border-slate-800 rounded-xl p-3 my-6 overflow-hidden relative';
            adNavbar.innerHTML = `
                <div class="flex items-center justify-between mb-2 px-1">
                    <span class="text-[10px] font-mono tracking-widest text-slate-500 uppercase font-bold">⚡ SPONSORED_SUBNET // BREAKPOINT_${Math.floor(i/10) + 1}</span>
                    <span class="text-[9px] bg-slate-900 text-amber-400 border border-amber-900 px-1.5 py-0.2 rounded font-mono font-bold">AD</span>
                </div>
                <!-- Smooth Drag/Scroll Horizontal track slider wrapper -->
                <div class="flex gap-4 overflow-x-auto no-scrollbar scroll-smooth py-1 snap-x select-none">
                    <div class="min-w-[240px] md:min-w-[280px] bg-slate-900 rounded-lg p-3 border border-slate-800 flex items-center gap-3 snap-center">
                        <span class="text-2xl">💻</span>
                        <div class="overflow-hidden">
                            <h4 class="text-xs font-mono font-bold text-cyberCyan truncate">Cyber_Host Pro</h4>
                            <p class="text-[10px] text-slate-400 truncate">100% NVMe cloud nodes setup instantly.</p>
                        </div>
                    </div>
                    <div class="min-w-[240px] md:min-w-[280px] bg-slate-900 rounded-lg p-3 border border-slate-800 flex items-center gap-3 snap-center">
                        <span class="text-2xl">🔒</span>
                        <div class="overflow-hidden">
                            <h4 class="text-xs font-mono font-bold text-cyberNeon truncate">Proxy_Matrix VPN</h4>
                            <p class="text-[10px] text-slate-400 truncate">Encrypted node tunnels routing securely.</p>
                        </div>
                    </div>
                    <div class="min-w-[240px] md:min-w-[280px] bg-slate-900 rounded-lg p-3 border border-slate-800 flex items-center gap-3 snap-center">
                        <span class="text-2xl">☕</span>
                        <div class="overflow-hidden">
                            <h4 class="text-xs font-mono font-bold text-slate-200 truncate">Hacker_Juice Coffee</h4>
                            <p class="text-[10px] text-slate-400 truncate">High caffeine blends optimized for devs.</p>
                        </div>
                    </div>
                    <div class="min-w-[240px] md:min-w-[280px] bg-slate-900 rounded-lg p-3 border border-slate-800 flex items-center gap-3 snap-center">
                        <span class="text-2xl">⚡</span>
                        <div class="overflow-hidden">
                            <h4 class="text-xs font-mono font-bold text-indigo-400 truncate">Vercel Neon Core</h4>
                            <p class="text-[10px] text-slate-400 truncate">Deploy fullstack apps at global edges.</p>
                        </div>
                    </div>
                </div>
            `;
            matrixContainer.appendChild(adNavbar);
        }
    }
}

// 2. NETWORK CONTROLLERS (TALKING TO FASTAPI BACKEND)
async function fetchVaultMedia() {
    try {
        const response = await fetch('/api/media');
        if (response.ok) {
            mediaItems = await response.json();
            renderMatrix();
        }
    } catch (err) {
        console.error("Matrix synchronizer dropped package connection:", err);
    }
}

async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    uploadStatus.classList.remove('hidden', 'text-red-400', 'text-cyberNeon');
    uploadStatus.classList.add('text-cyberCyan', 'animate-pulse');
    uploadStatus.textContent = `⚡ TRANSMITTING: ${file.name.toUpperCase()} TO SUPABASE_...`;

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            uploadStatus.classList.remove('cyberCyan', 'animate-pulse');
            uploadStatus.classList.add('text-cyberNeon');
            uploadStatus.textContent = '📦 TRANSMISSION STATUS: COMPLETE_';
            mediaUpload.value = ''; // clear input
            setTimeout(() => uploadStatus.classList.add('hidden'), 3000);
            await fetchVaultMedia(); // Refresh live content layout
        } else {
            throw new Error('Upload rejected by server');
        }
    } catch (err) {
        uploadStatus.classList.remove('text-cyberCyan', 'animate-pulse');
        uploadStatus.classList.add('text-red-400');
        uploadStatus.textContent = '❌ TRANSMISSION REJECTED: UPLOAD_FAILURE';
    }
}

// 3. SELECTION & ACTION DRAWER INTERACTION PIPELINES
function toggleSelection(filename) {
    if (selectedFiles.has(filename)) {
        selectedFiles.delete(filename);
    } else {
        selectedFiles.add(filename);
    }
    updateActionBarState();
    renderMatrix();
}

function updateActionBarState() {
    selectedCount.textContent = selectedFiles.size;
    if (selectedFiles.size > 0) {
        actionBar.classList.remove('translate-y-full');
    } else {
        actionBar.classList.add('translate-y-full');
    }
}

selectAllBtn.addEventListener('click', () => {
    if (selectedFiles.size === mediaItems.length) {
        selectedFiles.clear();
        selectAllBtn.textContent = '[ ] Select_All';
    } else {
        mediaItems.forEach(item => selectedFiles.add(item.filename));
        selectAllBtn.textContent = '[X] Clear_All';
    }
    updateActionBarState();
    renderMatrix();
});

// 4. BATCH ACTIONS (SAVE AND PURGE MATRIX DATA)
document.getElementById('batchDeleteBtn').addEventListener('click', async () => {
    if (!confirm(`Are you sure you want to permanently purge ${selectedFiles.size} asset(s) from the vault matrix?`)) return;
    
    const formData = new FormData();
    selectedFiles.forEach(name => formData.append('filenames', name));
    
    try {
        const response = await fetch('/api/delete', { method: 'POST', body: formData });
        if (response.ok) {
            selectedFiles.clear();
            updateActionBarState();
            await fetchVaultMedia();
        }
    } catch (err) {
        alert("Matrix delete operation runtime exception failed.");
    }
});

document.getElementById('batchDownloadBtn').addEventListener('click', () => {
    mediaItems.forEach(item => {
        if (selectedFiles.has(item.filename)) {
            const link = document.createElement('a');
            link.href = item.url;
            link.download = item.filename;
            link.target = '_blank'; // Fail-safe for cross-origin assets
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });
});

// 5. LIGHT / DARK TERMINAL CONTROLLER 
themeToggle.addEventListener('click', () => {
    const html = document.documentElement;
    if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        html.classList.add('light');
        localStorage.setItem('theme', 'light');
    } else {
        html.classList.remove('light');
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
});

// INITIAL LOADING BOOT UP PIPELINE
document.addEventListener('DOMContentLoaded', () => {
    // Preserve local theme settings if set
    if (localStorage.getItem('theme') === 'light') {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
    }
    mediaUpload.addEventListener('change', handleFileUpload);
    fetchVaultMedia();
});
