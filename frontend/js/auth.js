// ============================================
// AUTHENTICATION
// ============================================

const API_BASE = 'http://localhost:5000/api';
const TOKEN_KEY = 'hotel_auth_token';
const USER_KEY = 'hotel_user';

// ============================================
// LOGIN - FIXED
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('btnLogout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    const loginBtn = document.getElementById('loginBtn');
    const loginUsername = document.getElementById('loginUsername');
    const loginPassword = document.getElementById('loginPassword');
    const loginError = document.getElementById('loginError');
    
    if (loginBtn) {
        loginBtn.addEventListener('click', async function() {
            const username = loginUsername.value.trim();
            const password = loginPassword.value.trim();
            
            // Clear previous error
            if (loginError) {
                loginError.style.display = 'none';
                loginError.textContent = '';
            }
            
            // Validate
            if (!username || !password) {
                if (loginError) {
                    loginError.textContent = 'Please enter username and password';
                    loginError.style.display = 'block';
                }
                return;
            }
            
            try {
                loginBtn.textContent = 'Logging in...';
                loginBtn.disabled = true;
                
                console.log('Attempting login for:', username);
                
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json' 
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                console.log('Login response:', data);
                
                if (!response.ok || !data.success) {
                    throw new Error(data.error || data.message || 'Login failed');
                }
                
                // Save token and user info
                localStorage.setItem(TOKEN_KEY, data.data.token);
                localStorage.setItem(USER_KEY, JSON.stringify({
                    username: data.data.username,
                    role: data.data.role,
                    guest_id: data.data.guest_id
                }));
                
                console.log('Login successful! Redirecting...');
                
                // Redirect to dashboard
                window.location.href = 'dashboard.html';
                
            } catch (error) {
                console.error('Login error:', error);
                if (loginError) {
                    loginError.textContent = error.message || 'Network error. Please try again.';
                    loginError.style.display = 'block';
                }
                loginBtn.textContent = 'Sign In';
                loginBtn.disabled = false;
            }
        });
    }
    
    // Enter key support
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const loginBtn = document.getElementById('loginBtn');
            if (loginBtn) {
                loginBtn.click();
            }
        }
    });
});

// ============================================
// CHECK AUTH ON PAGE LOAD
// ============================================
function checkAuth() {
    const token = localStorage.getItem(TOKEN_KEY);
    const currentPage = window.location.pathname;
    
    // If on dashboard and no token, redirect to login
    if (currentPage.includes('dashboard.html') && !token) {
        window.location.href = 'index.html';
        return false;
    }
    
    // If on login page and have token, redirect to dashboard
    if (currentPage.includes('index.html') && token) {
        window.location.href = 'dashboard.html';
        return false;
    }
    
    return true;
}

// ============================================
// GET USER INFO
// ============================================
function getUser() {
    try {
        const user = localStorage.getItem(USER_KEY);
        return user ? JSON.parse(user) : null;
    } catch {
        return null;
    }
}

function isAdmin() {
    const user = getUser();
    return user && user.role === 'admin';
}

function getAuthHeaders() {
    const token = localStorage.getItem(TOKEN_KEY);
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// ============================================
// LOGOUT
// ============================================
function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = 'index.html';
}

// ============================================
// API CLIENT
// ============================================
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...options.headers
    };
    
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
        logout();
        throw new Error('Session expired. Please login again.');
    }
    
    return response;
}

// ============================================
// RUN CHECK AUTH
// ============================================
checkAuth();