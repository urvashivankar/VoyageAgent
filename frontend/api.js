function readLocalTrips() {
    return JSON.parse(localStorage.getItem('tp_trips') || '[]');
}

function writeLocalTrips(trips) {
    localStorage.setItem('tp_trips', JSON.stringify(trips));
}

const TP_CURRENCIES = {
    INR: { symbol: '₹', rate: 1 },
    USD: { symbol: '$', rate: 0.012 },
    AED: { symbol: 'د.إ', rate: 0.044 },
    EUR: { symbol: '€', rate: 0.011 },
};

function getSelectedCurrency() {
    return localStorage.getItem('tp_currency') || 'INR';
}

function setSelectedCurrency(currency) {
    if (TP_CURRENCIES[currency]) {
        localStorage.setItem('tp_currency', currency);
    }
}

function convertFromINR(amount, currency = getSelectedCurrency()) {
    const numeric = Number(amount || 0);
    const rate = TP_CURRENCIES[currency]?.rate || 1;
    return numeric * rate;
}

function formatCurrency(amountInINR, currency = getSelectedCurrency()) {
    const meta = TP_CURRENCIES[currency] || TP_CURRENCIES.INR;
    const converted = convertFromINR(amountInINR, currency);
    const maximumFractionDigits = currency === 'INR' ? 0 : 2;
    return `${meta.symbol}${converted.toLocaleString(undefined, { maximumFractionDigits })}`;
}

function readSavedItems(type = null) {
    const items = JSON.parse(localStorage.getItem('tp_saved_items') || '[]');
    return type ? items.filter(item => item.type === type) : items;
}

function writeSavedItems(items) {
    localStorage.setItem('tp_saved_items', JSON.stringify(items));
}

function pushNotification(title, message, type = 'info') {
    const notifications = JSON.parse(localStorage.getItem('tp_notifications') || '[]');
    notifications.unshift({
        id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
        title,
        message,
        type,
        read: false,
        created_at: new Date().toISOString(),
    });
    localStorage.setItem('tp_notifications', JSON.stringify(notifications.slice(0, 25)));
    window.dispatchEvent(new CustomEvent('tp:notification'));
}

function showToast(message) {
    let host = document.getElementById('toast-host');
    if (!host) {
        host = document.createElement('div');
        host.id = 'toast-host';
        host.style.cssText = 'position:fixed;right:1rem;bottom:1rem;display:grid;gap:.75rem;z-index:9999;';
        document.body.appendChild(host);
    }
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = 'padding:.85rem 1rem;border-radius:.75rem;background:rgba(16,185,129,.95);color:white;font-weight:700;box-shadow:0 18px 40px rgba(0,0,0,.35);transform:translateY(8px);opacity:0;transition:all .25s ease;';
    host.appendChild(toast);
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    });
    setTimeout(() => {
        toast.style.transform = 'translateY(8px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 250);
    }, 2400);
}

function normalizeTrip(result, sourceData = {}) {
    return {
        id: result.id || (crypto.randomUUID ? crypto.randomUUID() : String(Date.now())),
        created_at: result.created_at || new Date().toISOString(),
        destination: result.destination || sourceData.destination,
        budget: Number(result.budget ?? sourceData.budget ?? 0),
        days: Number(result.days ?? sourceData.days ?? 1),
        travelers: Number(result.travelers ?? sourceData.travelers ?? 1),
        travel_style: result.travel_style || sourceData.travel_style || 'Relaxing',
        hero_image: result.hero_image || '',
        currency: result.currency || 'INR',
        trip_type: result.trip_type || 'Domestic',
        budget_feasibility: result.budget_feasibility || 'Good',
        budget_allocation: result.budget_allocation || {},
        hotel_recommendations: result.hotel_recommendations || [],
        attractions: result.attractions || [],
        itinerary: result.itinerary || [],
        total_estimated_cost: Number(result.total_estimated_cost ?? result.budget ?? sourceData.budget ?? 0),
        travel_tips: result.travel_tips || {},
        ai_reasoning: result.ai_reasoning || [],
        agent_status: result.agent_status || [],
        generation_mode: result.generation_mode || 'unknown',
        generation_note: result.generation_note || '',
        is_saved: result.is_saved ?? false,
        is_favorite: result.is_favorite ?? false,
    };
}

async function createTrip(tripData) {
    const result = await authFetch('/trips/', {
        method: 'POST',
        body: JSON.stringify(tripData),
    });

    const trip = normalizeTrip(result, tripData);
    const trips = readLocalTrips();
    trips.unshift(trip);
    writeLocalTrips(trips);
    localStorage.setItem('tp_last_trip', JSON.stringify(trip));
    pushNotification('Trip generated', `${trip.destination} itinerary is ready.`, 'success');
    return trip;
}

async function getTrips() {
    return readLocalTrips();
}

async function getTrip(id) {
    const trips = readLocalTrips();
    const trip = trips.find(item => String(item.id) === String(id));
    if (trip) return trip;

    const stored = localStorage.getItem('tp_last_trip');
    if (stored) {
        const lastTrip = JSON.parse(stored);
        if (String(lastTrip.id) === String(id)) return lastTrip;
    }

    throw new Error('Trip not found in local storage.');
}

async function saveTripSelection(tripId, type, item) {
    const saved = readSavedItems();
    const record = {
        id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
        trip_id: tripId,
        type,
        item,
        created_at: new Date().toISOString(),
    };
    saved.unshift(record);
    writeSavedItems(saved);

    try {
        await authFetch(`/trips/${tripId}/save-selection`, {
            method: 'POST',
            body: JSON.stringify({ type, item }),
        });
    } catch (e) {
        console.warn('Server save unavailable; kept locally.', e);
    }

    const label = type === 'hotel' ? 'Hotel saved' : type === 'attraction' ? 'Attraction saved' : 'Saved to plan';
    pushNotification(label, `${item.name || item.title || 'Selection'} was added to your itinerary.`, 'success');
    showToast(`${label} to itinerary`);
    return record;
}

function deleteTrip(tripId) {
    const trips = readLocalTrips().filter(t => String(t.id) !== String(tripId));
    writeLocalTrips(trips);
    pushNotification('Trip deleted', 'Trip was removed from your plans.', 'info');
    showToast('Trip deleted');
}

function duplicateTrip(tripId) {
    const trips = readLocalTrips();
    const original = trips.find(t => String(t.id) === String(tripId));
    if (!original) return null;
    const copy = { ...JSON.parse(JSON.stringify(original)) };
    copy.id = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
    copy.created_at = new Date().toISOString();
    copy.destination = original.destination + ' (Copy)';
    trips.unshift(copy);
    writeLocalTrips(trips);
    pushNotification('Trip duplicated', `Copy of ${original.destination} created.`, 'success');
    showToast('Trip duplicated');
    return copy;
}

function toggleFavorite(tripId) {
    const trips = readLocalTrips();
    const trip = trips.find(t => String(t.id) === String(tripId));
    if (!trip) return;
    trip.is_favorite = !trip.is_favorite;
    writeLocalTrips(trips);
    showToast(trip.is_favorite ? 'Added to favorites ❤️' : 'Removed from favorites');
    return trip.is_favorite;
}

async function apiFetch(path, options = {}) {
    return authFetch(path, options);
}
