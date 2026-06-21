const API_BASE = 'http://localhost:8000';

function getToken() {
    return localStorage.getItem('tp_token');
}

function setToken(token) {
    localStorage.setItem('tp_token', token);
}

function clearToken() {
    localStorage.removeItem('tp_token');
    localStorage.removeItem('tp_user');
}

function setUser(user) {
    localStorage.setItem('tp_user', JSON.stringify(user));
}

function getUser() {
    const raw = localStorage.getItem('tp_user');
    return raw ? JSON.parse(raw) : null;
}

function requireAuth() {
    if (!getToken()) {
        window.location.href = 'login.html';
    }
}

function logout() {
    clearToken();
    window.location.href = 'login.html';
}

async function authFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
    };

    const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    if (!response.ok) {
        let errMsg = `API Error: ${response.status} ${response.statusText}`;
        try {
            const errData = await response.json();
            if (errData.detail) errMsg = Array.isArray(errData.detail)
                ? errData.detail.map(item => item.msg || JSON.stringify(item)).join(', ')
                : errData.detail;
        } catch (e) {
            // Keep default message.
        }
        throw new Error(errMsg);
    }
    return response.json();
}

async function register(name, email, mobile) {
    const user = {
        id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
        name: name.trim(),
        email: email.trim(),
        mobile: mobile.trim(),
        created_at: new Date().toISOString(),
    };

    const users = JSON.parse(localStorage.getItem('tp_users') || '[]');
    const existing = users.find(item => item.email.toLowerCase() === user.email.toLowerCase());
    if (existing) {
        throw new Error('Email already registered locally. Please sign in instead.');
    }

    users.push(user);
    localStorage.setItem('tp_users', JSON.stringify(users));
    setUser(user);
    setToken('local_demo_token');
    return user;
}

async function login(email) {
    const normalizedEmail = email.trim().toLowerCase();
    const users = JSON.parse(localStorage.getItem('tp_users') || '[]');
    let user = users.find(item => item.email.toLowerCase() === normalizedEmail);

    if (!user) {
        user = {
            id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
            name: normalizedEmail.split('@')[0] || 'Traveler',
            email: normalizedEmail,
            mobile: '',
            created_at: new Date().toISOString(),
        };
        users.push(user);
        localStorage.setItem('tp_users', JSON.stringify(users));
    }

    setUser(user);
    setToken('local_demo_token');
    return { access_token: 'local_demo_token' };
}
