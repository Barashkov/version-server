// API Configuration
const API_BASE = '/api/v1.0';
let auth = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupTabs();
    setupForms();
});

// Authentication
function checkAuth() {
    const savedAuth = localStorage.getItem('auth');
    if (savedAuth) {
        auth = JSON.parse(savedAuth);
        document.getElementById('loginModal').classList.add('hidden');
        document.getElementById('mainContent').classList.remove('hidden');
        loadAreas();
    }
}

function setupForms() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        auth = btoa(`${username}:${password}`);
        
        // Test auth
        fetch(`${API_BASE}/areas`, {
            headers: {
                'Authorization': `Basic ${auth}`
            }
        })
        .then(response => {
            if (response.ok) {
                localStorage.setItem('auth', JSON.stringify(auth));
                document.getElementById('loginModal').classList.add('hidden');
                document.getElementById('mainContent').classList.remove('hidden');
                loadAreas();
                showToast('Успешный вход!', 'success');
            } else {
                document.getElementById('loginError').textContent = 'Неверный логин или пароль';
                auth = null;
            }
        })
        .catch(error => {
            document.getElementById('loginError').textContent = 'Ошибка соединения';
            console.error('Auth error:', error);
        });
    });

    // Create area form
    document.getElementById('createAreaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const areaName = document.getElementById('areaName').value;
        createArea(areaName);
    });

    // Create service form
    document.getElementById('createServiceForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const area = document.getElementById('areaSelect').value;
        if (!area) {
            showToast('Выберите площадку', 'error');
            return;
        }
        
        const serviceData = {
            name: document.getElementById('serviceName').value,
            type: document.getElementById('serviceType').value,
            url: document.getElementById('serviceUrl').value,
            version: document.getElementById('serviceVersion').value,
            status: document.getElementById('serviceStatus').value
        };
        
        createService(area, serviceData);
    });

    // Edit service form
    document.getElementById('editServiceForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const area = document.getElementById('areaSelect').value;
        const serviceId = document.getElementById('editServiceId').value;
        
        const updateData = {
            name: document.getElementById('editServiceName').value,
            type: document.getElementById('editServiceType').value,
            url: document.getElementById('editServiceUrl').value,
            version: document.getElementById('editServiceVersion').value,
            status: document.getElementById('editServiceStatus').value
        };
        
        updateService(area, serviceId, updateData);
    });
}

// API Functions
async function apiRequest(endpoint, options = {}) {
    showLoading(true);
    
    const defaultOptions = {
        headers: {
            'Authorization': `Basic ${auth}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, { ...options, ...defaultOptions });
        const data = await response.json();
        
        showLoading(false);
        
        if (!response.ok) {
            throw new Error(data.error || 'API Error');
        }
        
        return data;
    } catch (error) {
        showLoading(false);
        showToast(error.message, 'error');
        throw error;
    }
}

// Tabs
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(`${tabName}Tab`).classList.add('active');
        });
    });
}

// Areas Functions
async function loadAreas() {
    try {
        const data = await apiRequest('/areas');
        const areasList = document.getElementById('areasList');
        const areaSelect = document.getElementById('areaSelect');
        
        // Update area select
        areaSelect.innerHTML = '<option value="">Выберите площадку</option>';
        data.areas.forEach(area => {
            const option = document.createElement('option');
            option.value = area;
            option.textContent = area;
            areaSelect.appendChild(option);
        });
        
        // Update areas list
        if (data.areas.length === 0) {
            areasList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📍</div>
                    <div class="empty-state-text">Нет площадок. Создайте первую площадку!</div>
                </div>
            `;
            return;
        }
        
        areasList.innerHTML = data.areas.map(area => `
            <div class="item-card">
                <div class="item-header">
                    <div class="item-title">${area}</div>
                    <div class="item-actions">
                        <button class="btn btn-sm btn-primary" onclick="loadAreaServices('${area}')">Просмотр сервисов</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteArea('${area}')">Удалить</button>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading areas:', error);
    }
}

async function createArea(areaName) {
    try {
        await apiRequest(`/area/${areaName}`, { method: 'POST' });
        closeModal('createAreaModal');
        document.getElementById('createAreaForm').reset();
        loadAreas();
        showToast(`Площадка "${areaName}" создана!`, 'success');
    } catch (error) {
        console.error('Error creating area:', error);
    }
}

async function deleteArea(areaName) {
    if (!confirm(`Вы уверены, что хотите удалить площадку "${areaName}" со всеми сервисами?`)) {
        return;
    }
    
    try {
        await apiRequest(`/area/${areaName}`, { method: 'DELETE' });
        loadAreas();
        showToast(`Площадка "${areaName}" удалена!`, 'success');
    } catch (error) {
        console.error('Error deleting area:', error);
    }
}

// Services Functions
async function loadServices() {
    const area = document.getElementById('areaSelect').value;
    if (!area) {
        document.getElementById('servicesList').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚙️</div>
                <div class="empty-state-text">Выберите площадку для просмотра сервисов</div>
            </div>
        `;
        return;
    }
    
    await loadAreaServices(area);
}

async function loadAreaServices(area) {
    try {
        // Set the area in select if not already set
        const areaSelect = document.getElementById('areaSelect');
        areaSelect.value = area;
        
        // Switch to services tab
        document.querySelector('[data-tab="services"]').click();
        
        const data = await apiRequest(`/services/${area}`);
        const servicesList = document.getElementById('servicesList');
        const services = data[area] || [];
        
        if (services.length === 0) {
            servicesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚙️</div>
                    <div class="empty-state-text">В площадке "${area}" нет сервисов</div>
                </div>
            `;
            return;
        }
        
        servicesList.innerHTML = services.map(service => `
            <div class="item-card">
                <div class="item-header">
                    <div class="item-title">${service.name}</div>
                    <div class="item-badge">${service.type}</div>
                </div>
                <div class="item-details">
                    <div class="item-detail">
                        <div class="item-detail-label">ID</div>
                        <div class="item-detail-value">${service.id}</div>
                    </div>
                    <div class="item-detail">
                        <div class="item-detail-label">URL</div>
                        <div class="item-detail-value">${service.url}</div>
                    </div>
                    <div class="item-detail">
                        <div class="item-detail-label">Версия</div>
                        <div class="item-detail-value">${service.version || 'Не указана'}</div>
                    </div>
                    <div class="item-detail">
                        <div class="item-detail-label">Статус</div>
                        <div class="item-detail-value">${service.status || 'Не указан'}</div>
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-sm btn-warning" onclick="showEditServiceModal(${service.id})">Редактировать</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteService(${service.id})">Удалить</button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

async function createService(area, serviceData) {
    try {
        await apiRequest(`/services/${area}`, {
            method: 'POST',
            body: JSON.stringify(serviceData)
        });
        closeModal('createServiceModal');
        document.getElementById('createServiceForm').reset();
        loadAreaServices(area);
        showToast('Сервис создан!', 'success');
    } catch (error) {
        console.error('Error creating service:', error);
    }
}

async function updateService(area, serviceId, updateData) {
    try {
        const data = await apiRequest(`/services/${area}/${serviceId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
        closeModal('editServiceModal');
        loadAreaServices(area);
        showToast('Сервис обновлен!', 'success');
    } catch (error) {
        console.error('Error updating service:', error);
    }
}

async function deleteService(serviceId) {
    const area = document.getElementById('areaSelect').value;
    if (!area) {
        showToast('Выберите площадку', 'error');
        return;
    }
    
    if (!confirm('Вы уверены, что хотите удалить этот сервис?')) {
        return;
    }
    
    try {
        await apiRequest(`/services/${area}/${serviceId}`, { method: 'DELETE' });
        loadAreaServices(area);
        showToast('Сервис удален!', 'success');
    } catch (error) {
        console.error('Error deleting service:', error);
    }
}

async function showEditServiceModal(serviceId) {
    const area = document.getElementById('areaSelect').value;
    if (!area) {
        showToast('Выберите площадку', 'error');
        return;
    }
    
    try {
        const data = await apiRequest(`/services/${area}/${serviceId}`);
        const service = data.service;
        
        document.getElementById('editServiceId').value = service.id;
        document.getElementById('editServiceName').value = service.name;
        document.getElementById('editServiceType').value = service.type;
        document.getElementById('editServiceUrl').value = service.url;
        document.getElementById('editServiceVersion').value = service.version || '';
        document.getElementById('editServiceStatus').value = service.status || '';
        
        document.getElementById('editServiceModal').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading service:', error);
    }
}

// Modal Functions
function showCreateAreaModal() {
    document.getElementById('createAreaModal').classList.remove('hidden');
}

function showCreateServiceModal() {
    const area = document.getElementById('areaSelect').value;
    if (!area) {
        showToast('Выберите площадку', 'error');
        return;
    }
    document.getElementById('createServiceModal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// UI Helpers
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Close modals on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.add('hidden');
        }
    });
});
