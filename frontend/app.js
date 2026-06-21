// Initialize Lucide icons
lucide.createIcons();

// --- Configuration ---
// Make sure your backend is running on this URL
const API_BASE_URL = 'http://localhost:8001';

// In a real app we'd have login, but we'll mock auth for this demo
// by hardcoding a mock user JWT flow or bypassing it depending on backend.
// Note: Since we have actual JWT auth in FastAPI, we need to register/login a user first.
let authToken = localStorage.getItem('token');

// --- Routing Logic ---
function navigate(viewId) {
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show target view
    const target = document.getElementById(`view-${viewId}`);
    if (target) {
        target.classList.add('active');
        target.classList.add('fade-in');
    }

    // specific actions per view
    if (viewId === 'dashboard') {
        loadTrips();
    }
}

// --- App Logic ---

// Helper for authenticated fetch
async function apiFetch(endpoint, options = {}) {
    if (!authToken) {
        // Auto-register and login a dummy user for the demo to bypass auth walls smoothly
        await ensureMockUser();
    }

    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}

async function ensureMockUser() {
    try {
        // Try to login directly
        const formData = new URLSearchParams();
        formData.append('username', 'demo@trippilot.ai');
        formData.append('password', 'demo123');

        let res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        });

        if (!res.ok) {
            // Register first if login fails
            await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: "Demo User", email: "demo@trippilot.ai", password: "demo123" })
            });

            // Login again
            res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
        }
        
        const data = await res.json();
        authToken = data.access_token;
        localStorage.setItem('token', authToken);
    } catch (err) {
        console.error("Auth mock failed: Ensure your backend is running!", err);
    }
}

// --- Dashboard Logic ---
async function loadTrips() {
    const container = document.getElementById('trips-container');
    container.innerHTML = '<p class="text-gray-400">Loading your trips...</p>';

    try {
        const trips = await apiFetch('/trips/');
        
        if (trips.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-10 bg-white/5 rounded-2xl border border-white/10">
                    <p class="text-gray-400 mb-4">You don't have any trips yet.</p>
                    <button onclick="navigate('create-trip')" class="text-blue-400 hover:text-blue-300">Create your first trip</button>
                </div>
            `;
            return;
        }

        container.innerHTML = trips.map(trip => `
            <div class="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md cursor-pointer hover:border-blue-500/50 transition-colors transform hover:-translate-y-1">
                <div class="flex justify-between items-start mb-4">
                    <h3 class="text-2xl font-semibold text-white flex items-center">
                        <i data-lucide="plane" class="w-5 h-5 mr-2 text-blue-400"></i>
                        ${trip.destination}
                    </h3>
                </div>
                <div class="flex items-center text-gray-400 gap-6">
                    <span class="flex items-center"><i data-lucide="wallet" class="w-4 h-4 mr-2"></i> ₹${trip.budget}</span>
                    <span class="flex items-center"><i data-lucide="calendar" class="w-4 h-4 mr-2"></i> ${trip.days} Days</span>
                </div>
                <div class="mt-4 flex flex-wrap gap-2">
                    <span class="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded-lg">${trip.travel_style}</span>
                </div>
            </div>
        `).join('');
        
        lucide.createIcons(); // Re-initialize icons for new DOM elements
    } catch (err) {
        container.innerHTML = `<p class="text-red-400">Failed to load trips. Make sure your FastAPI backend is running.</p>`;
    }
}

// --- Form Handling ---
document.getElementById('create-trip-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const submitBtn = document.getElementById('submit-btn');
    const errorMsg = document.getElementById('error-message');
    
    // UI Loading state
    btnText.classList.add('hidden');
    btnSpinner.classList.remove('hidden');
    submitBtn.disabled = true;
    errorMsg.classList.add('hidden');

    const tripData = {
        destination: document.getElementById('destination').value,
        budget: parseFloat(document.getElementById('budget').value),
        days: parseInt(document.getElementById('days').value),
        travel_style: document.getElementById('travel-style').value
    };

    try {
        // The LangGraph workflow runs in the backend when this endpoint is hit!
        await apiFetch('/trips/', {
            method: 'POST',
            body: JSON.stringify(tripData)
        });
        
        // Success
        navigate('dashboard');
        e.target.reset(); // clear form
    } catch (err) {
        console.error(err);
        errorMsg.textContent = "Error planning trip. Is the backend and Gemini API configured properly?";
        errorMsg.classList.remove('hidden');
    } finally {
        // Reset UI
        btnText.classList.remove('hidden');
        btnSpinner.classList.add('hidden');
        submitBtn.disabled = false;
    }
});
