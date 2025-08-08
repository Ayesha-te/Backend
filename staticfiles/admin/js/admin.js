// Access Auto Services Admin Panel JavaScript
// Version 2.0 - Updated with real data and CRUD operations
// Last updated: 2025-08-08

class AdminPanel {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {};
        this.apiBaseUrl = '/api'; // Same server API endpoints
        this.currentBookings = [];
        this.currentServices = [];
        this.currentUsers = [];
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEventListeners();
        this.initializeCharts();
        this.showPage('dashboard');
    }

    checkAuth() {
        // Check if user is logged in
        const isLoggedIn = sessionStorage.getItem('adminLoggedIn');
        if (!isLoggedIn) {
            window.location.href = '/static/admin/login.html';
            return;
        }
        console.log('Admin panel loaded for:', sessionStorage.getItem('adminUser'));
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.currentTarget.getAttribute('data-page');
                this.showPage(page);
            });
        });

        // Mobile sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('show');
            });
        }

        // Search functionality
        const searchInputs = document.querySelectorAll('.search-input');
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.handleSearch(e.target.value, e.target.closest('.page-content').id);
            });
        });
    }

    showPage(page) {
        // Hide all pages
        document.querySelectorAll('.page-content').forEach(pageEl => {
            pageEl.style.display = 'none';
        });

        // Show selected page
        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.style.display = 'block';
        }

        // Update sidebar active state
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-page="${page}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            pageTitle.textContent = this.getPageTitle(page);
        }

        // Load page-specific data
        this.loadPageData(page);
        this.currentPage = page;
        this.startAutoRefresh(page);
    }

    getPageTitle(page) {
        const titles = {
            dashboard: 'Dashboard',
            users: 'Users',
            bookings: 'Bookings',
            services: 'Services',
            payments: 'Payments',
            reports: 'Reports'
        };
        return titles[page] || 'Dashboard';
    }

    startAutoRefresh(page) {
        // Clear existing interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        // Set up auto-refresh for data pages (every 30 seconds)
        if (['users', 'bookings', 'services', 'dashboard'].includes(page)) {
            this.refreshInterval = setInterval(() => {
                console.log(`🔄 Auto-refreshing ${page} data...`);
                this.loadPageData(page);
                
                // Show a subtle indicator that data is being refreshed
                const indicator = document.createElement('div');
                indicator.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refreshing...';
                indicator.className = 'position-fixed top-0 end-0 bg-primary text-white px-3 py-1 rounded-bottom';
                indicator.style.zIndex = '9999';
                document.body.appendChild(indicator);
                
                setTimeout(() => {
                    if (indicator.parentNode) {
                        indicator.parentNode.removeChild(indicator);
                    }
                }, 2000);
            }, 30000); // 30 seconds
        }
    }

    updateLastRefreshTime(page) {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        console.log(`📊 ${page} data updated at ${timeString}`);
        
        // You could add a visual indicator here if needed
        const pageElement = document.getElementById(`${page}-page`);
        if (pageElement) {
            let indicator = pageElement.querySelector('.last-refresh');
            if (!indicator) {
                indicator = document.createElement('small');
                indicator.className = 'last-refresh text-muted';
                const header = pageElement.querySelector('h2');
                if (header) {
                    header.appendChild(indicator);
                }
            }
            indicator.textContent = ` (Updated: ${timeString})`;
        }
    }

    async loadPageData(page) {
        try {
            switch (page) {
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
                case 'users':
                    await this.loadUsersData();
                    break;
                case 'bookings':
                    await this.loadBookingsData();
                    break;
                case 'services':
                    await this.loadServicesData();
                    break;
                case 'payments':
                    await this.loadPaymentsData();
                    break;
                case 'reports':
                    await this.loadReportsData();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${page} data:`, error);
            this.showError(`Failed to load ${page} data`);
        }
    }

    async loadDashboardData() {
        try {
            console.log('Loading dashboard data...');
            // Load dashboard statistics
            const [usersCount, bookingsCount, paymentsTotal, services] = await Promise.all([
                this.apiCall('/users/count/'),
                this.apiCall('/bookings/count/'),
                this.apiCall('/payments/total/'),
                this.apiCall('/services/')
            ]);
            
            console.log('Dashboard data loaded:', { usersCount, bookingsCount, paymentsTotal, services });

            // Update stats cards
            this.updateElement('totalUsers', usersCount.total || 0);
            this.updateElement('newUsers', `+${usersCount.new_this_week || 0} this week`);
            
            this.updateElement('totalBookings', bookingsCount.total || 0);
            this.updateElement('todayBookings', `${bookingsCount.today || 0} today`);
            
            this.updateElement('totalRevenue', `£${(paymentsTotal.total || 0).toFixed(2)}`);
            this.updateElement('todayRevenue', `£${(paymentsTotal.today || 0).toFixed(2)} today`);
            
            this.updateElement('totalServices', services.results?.length || 0);
            this.updateElement('servicesChange', `${services.results?.filter(s => s.active).length || 0} active`);

            // Load charts
            await this.loadCharts();
            
            // Load recent data
            await this.loadRecentBookings();
            await this.loadRecentUsers();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadCharts() {
        try {
            const [trendsData, distributionData] = await Promise.all([
                this.apiCall('/bookings/trends/'),
                this.apiCall('/bookings/service-distribution/')
            ]);

            this.updateBookingChart(trendsData);
            this.updateServiceChart(distributionData);
        } catch (error) {
            console.error('Error loading charts:', error);
        }
    }

    async loadBookingsData() {
        try {
            console.log('Loading bookings data...');
            const response = await this.apiCall('/bookings/');
            console.log('Bookings response:', response);
            this.currentBookings = response.results || [];
            console.log('Current bookings:', this.currentBookings);
            this.renderBookingsTable();
        } catch (error) {
            console.error('Error loading bookings:', error);
            this.showError('Failed to load bookings');
        }
    }

    async loadServicesData() {
        try {
            const response = await this.apiCall('/services/');
            this.currentServices = response.results || [];
            this.renderServicesTable();
        } catch (error) {
            console.error('Error loading services:', error);
            this.showError('Failed to load services');
        }
    }

    async loadUsersData() {
        try {
            const response = await this.apiCall('/users/');
            this.currentUsers = response.results || [];
            this.renderUsersTable(this.currentUsers);
            this.updateLastRefreshTime('users');
        } catch (error) {
            console.error('Error loading users:', error);
            this.showError('Failed to load users');
        }
    }

    async loadBookingsData() {
        try {
            const response = await this.apiCall('/bookings/');
            this.currentBookings = response.results || [];
            this.renderBookingsTable(this.currentBookings);
            this.updateLastRefreshTime('bookings');
        } catch (error) {
            console.error('Error loading bookings:', error);
            this.showError('Failed to load bookings');
        }
    }

    async loadPaymentsData() {
        try {
            const response = await this.apiCall('/payments/total/');
            this.renderPaymentsData(response);
        } catch (error) {
            console.error('Error loading payments:', error);
            this.showError('Failed to load payments');
        }
    }

    async loadReportsData() {
        // Load reports data
        await this.loadCharts();
    }

    // Utility Functions
    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        console.log(`API Call: ${method} ${url}`, data);
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        // Add CSRF token for non-GET requests
        if (method !== 'GET') {
            const csrfToken = this.getCSRFToken();
            if (csrfToken) {
                options.headers['X-CSRFToken'] = csrfToken;
            }
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        console.log(`API Response: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
            
            let errorData = {};
            try {
                errorData = JSON.parse(errorText);
            } catch (e) {
                errorData = { error: errorText || `HTTP ${response.status}` };
            }
            
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('API Result:', result);
        return result;
    }

    getCSRFToken() {
        // Try to get CSRF token from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return null;
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-GB');
    }

    getStatusBadgeClass(status) {
        const classes = {
            'pending': 'bg-warning',
            'confirmed': 'bg-success',
            'cancelled': 'bg-danger',
            'completed': 'bg-primary'
        };
        return classes[status] || 'bg-secondary';
    }

    getPaymentStatusBadgeClass(status) {
        const classes = {
            'pending': 'bg-warning',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'refunded': 'bg-info'
        };
        return classes[status] || 'bg-secondary';
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showToast(message, type = 'info') {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    initializeCharts() {
        // Initialize empty charts
        this.initBookingChart();
        this.initServiceChart();
    }

    initBookingChart() {
        const ctx = document.getElementById('bookingChart');
        if (!ctx) return;

        this.charts.booking = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Bookings',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initServiceChart() {
        const ctx = document.getElementById('serviceChart');
        if (!ctx) return;

        this.charts.service = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    updateBookingChart(data) {
        if (!this.charts.booking) return;

        this.charts.booking.data.labels = data.labels || [];
        this.charts.booking.data.datasets[0].data = data.paypal_data || [];
        this.charts.booking.update();
    }

    updateServiceChart(data) {
        if (!this.charts.service) return;

        this.charts.service.data.labels = data.labels || [];
        this.charts.service.data.datasets[0].data = data.values || [];
        this.charts.service.update();
    }

    async loadRecentBookings() {
        try {
            const response = await this.apiCall('/bookings/');
            const recentBookings = (response.results || []).slice(0, 5);
            
            const container = document.getElementById('recentBookings');
            if (!container) return;

            if (recentBookings.length === 0) {
                container.innerHTML = '<div class="list-group-item text-center text-muted">No recent bookings</div>';
                return;
            }

            container.innerHTML = recentBookings.map(booking => `
                <div class="list-group-item d-flex justify-content-between align-items-start">
                    <div class="ms-2 me-auto">
                        <div class="fw-bold">${booking.customer_first_name || 'N/A'} ${booking.customer_last_name || ''}</div>
                        <small class="text-muted">${booking.service?.name || 'Unknown Service'} - ${this.formatDate(booking.booking_date)}</small>
                    </div>
                    <span class="badge ${this.getStatusBadgeClass(booking.status)} rounded-pill">
                        ${booking.status || 'pending'}
                    </span>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading recent bookings:', error);
        }
    }

    async loadRecentUsers() {
        try {
            const response = await this.apiCall('/users/');
            const recentUsers = (response.results || []).slice(0, 5);
            
            const container = document.getElementById('recentUsers');
            if (!container) return;

            if (recentUsers.length === 0) {
                container.innerHTML = '<div class="list-group-item text-center text-muted">No recent users</div>';
                return;
            }

            container.innerHTML = recentUsers.map(user => `
                <div class="list-group-item d-flex justify-content-between align-items-start">
                    <div class="ms-2 me-auto">
                        <div class="fw-bold">${user.first_name || ''} ${user.last_name || ''}</div>
                        <small class="text-muted">${user.email}</small>
                    </div>
                    <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'} rounded-pill">
                        ${user.booking_count || 0} bookings
                    </span>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading recent users:', error);
        }
    }

    renderPaymentsData(data) {
        const container = document.querySelector('#payments-page .row');
        if (!container) return;

        container.innerHTML = `
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Revenue</h5>
                        <h2 class="text-primary">£${(data.total || 0).toFixed(2)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Today</h5>
                        <h2 class="text-success">£${(data.today || 0).toFixed(2)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">This Week</h5>
                        <h2 class="text-info">£${(data.week || 0).toFixed(2)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">This Month</h5>
                        <h2 class="text-warning">£${(data.month || 0).toFixed(2)}</h2>
                    </div>
                </div>
            </div>
        `;
    }

    renderBookingsTable() {
        const tableBody = document.querySelector('#bookings-page tbody');
        if (!tableBody) return;

        if (this.currentBookings.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted">No bookings found</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = this.currentBookings.map(booking => `
            <tr>
                <td><input type="checkbox" class="form-check-input"></td>
                <td>#${booking.id}</td>
                <td>
                    ${booking.customer_first_name || 'N/A'} ${booking.customer_last_name || ''}<br>
                    <small class="text-muted">${booking.customer_email || 'N/A'}</small>
                </td>
                <td>${booking.service?.name || 'Unknown Service'}</td>
                <td>
                    ${this.formatDate(booking.booking_date)}<br>
                    <small class="text-muted">${booking.booking_time || 'N/A'}</small>
                </td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(booking.status)}">
                        ${booking.status || 'pending'}
                    </span>
                </td>
                <td>
                    <span class="badge ${booking.is_paid ? 'bg-success' : 'bg-warning'}">
                        ${booking.is_paid ? 'Paid' : 'Unpaid'}
                    </span>
                </td>
                <td>£${(booking.amount || booking.payment_amount || 0).toFixed(2)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="adminPanel.editBooking(${booking.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="adminPanel.deleteBooking(${booking.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    renderServicesTable() {
        const tableBody = document.querySelector('#services-page tbody');
        if (!tableBody) return;

        if (this.currentServices.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">No services found</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = this.currentServices.map(service => `
            <tr>
                <td>${service.code}</td>
                <td>${service.name}</td>
                <td>${service.description || 'N/A'}</td>
                <td>£${service.price.toFixed(2)}</td>
                <td>
                    <span class="badge ${service.active ? 'bg-success' : 'bg-secondary'}">
                        ${service.active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="adminPanel.editService(${service.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="adminPanel.deleteService(${service.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    renderUsersTable(users) {
        const tableBody = document.querySelector('#users-page tbody');
        if (!tableBody) return;

        if (users.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">No users found</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = users.map(user => `
            <tr>
                <td><input type="checkbox" class="form-check-input"></td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px; font-size: 12px;">
                            ${(user.first_name?.[0] || 'U')}${(user.last_name?.[0] || '')}
                        </div>
                        <div>
                            <div class="fw-bold">${user.first_name || ''} ${user.last_name || ''}</div>
                        </div>
                    </div>
                </td>
                <td>${user.email}</td>
                <td>
                    <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <span class="badge ${user.is_staff ? 'bg-primary' : 'bg-light text-dark'}">
                        ${user.is_staff ? 'Staff' : 'Customer'}
                    </span>
                </td>
                <td>${this.formatDate(user.date_joined)}</td>
                <td>
                    <span class="badge bg-info">${user.booking_count || 0}</span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="adminPanel.editUser(${user.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="adminPanel.deleteUser(${user.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // CRUD Operations
    // User Management
    async createUser(userData) {
        try {
            await this.apiCall('/users/', 'POST', userData);
            this.showSuccess('User created successfully');
            await this.loadUsersData();
        } catch (error) {
            this.showError('Failed to create user: ' + error.message);
        }
    }

    async editUser(userId) {
        try {
            const user = await this.apiCall(`/users/${userId}/`);
            this.showUserModal(user);
        } catch (error) {
            this.showError('Failed to load user details');
        }
    }

    async updateUser(userId, userData) {
        try {
            await this.apiCall(`/users/${userId}/`, 'PUT', userData);
            this.showSuccess('User updated successfully');
            await this.loadUsersData();
        } catch (error) {
            this.showError('Failed to update user: ' + error.message);
        }
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) return;

        try {
            await this.apiCall(`/users/${userId}/`, 'DELETE');
            this.showSuccess('User deleted successfully');
            await this.loadUsersData();
        } catch (error) {
            this.showError('Failed to delete user: ' + error.message);
        }
    }

    // Booking Management
    async createBooking(bookingData) {
        try {
            await this.apiCall('/bookings/', 'POST', bookingData);
            this.showSuccess('Booking created successfully');
            await this.loadBookingsData();
        } catch (error) {
            this.showError('Failed to create booking: ' + error.message);
        }
    }

    async editBooking(bookingId) {
        try {
            const booking = await this.apiCall(`/bookings/${bookingId}/`);
            this.showBookingModal(booking);
        } catch (error) {
            this.showError('Failed to load booking details');
        }
    }

    async updateBooking(bookingId, bookingData) {
        try {
            await this.apiCall(`/bookings/${bookingId}/`, 'PUT', bookingData);
            this.showSuccess('Booking updated successfully');
            await this.loadBookingsData();
        } catch (error) {
            this.showError('Failed to update booking: ' + error.message);
        }
    }

    async deleteBooking(bookingId) {
        if (!confirm('Are you sure you want to delete this booking?')) return;

        try {
            await this.apiCall(`/bookings/${bookingId}/`, 'DELETE');
            this.showSuccess('Booking deleted successfully');
            await this.loadBookingsData();
        } catch (error) {
            this.showError('Failed to delete booking: ' + error.message);
        }
    }

    async createService(serviceData) {
        try {
            await this.apiCall('/services/', 'POST', serviceData);
            this.showSuccess('Service created successfully');
            await this.loadServicesData();
        } catch (error) {
            this.showError('Failed to create service: ' + error.message);
        }
    }

    async editService(serviceId) {
        try {
            const service = await this.apiCall(`/services/${serviceId}/`);
            this.showServiceModal(service);
        } catch (error) {
            this.showError('Failed to load service details');
        }
    }

    async updateService(serviceId, serviceData) {
        try {
            await this.apiCall(`/services/${serviceId}/`, 'PUT', serviceData);
            this.showSuccess('Service updated successfully');
            await this.loadServicesData();
        } catch (error) {
            this.showError('Failed to update service: ' + error.message);
        }
    }

    async deleteService(serviceId) {
        if (!confirm('Are you sure you want to delete this service?')) return;

        try {
            await this.apiCall(`/services/${serviceId}/`, 'DELETE');
            this.showSuccess('Service deleted successfully');
            await this.loadServicesData();
        } catch (error) {
            this.showError('Failed to delete service: ' + error.message);
        }
    }

    // Modal Functions
    showUserModal(user = null) {
        const modalHtml = `
            <div class="modal fade" id="userModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${user ? 'Edit User' : 'New User'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="userForm">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email" 
                                           value="${user ? user.email : ''}" required>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">First Name</label>
                                            <input type="text" class="form-control" name="first_name" 
                                                   value="${user ? user.first_name : ''}">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Last Name</label>
                                            <input type="text" class="form-control" name="last_name" 
                                                   value="${user ? user.last_name : ''}">
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Password ${user ? '(leave blank to keep current)' : ''}</label>
                                    <input type="password" class="form-control" name="password" 
                                           ${!user ? 'required' : ''}>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="checkbox" name="is_active" 
                                                   ${user && user.is_active ? 'checked' : (!user ? 'checked' : '')}>
                                            <label class="form-check-label">Active</label>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="checkbox" name="is_staff" 
                                                   ${user && user.is_staff ? 'checked' : ''}>
                                            <label class="form-check-label">Staff</label>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="adminPanel.saveUser(${user ? user.id : null})">
                                ${user ? 'Update' : 'Create'} User
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('userModal');
        if (existingModal) existingModal.remove();

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('userModal'));
        modal.show();
    }

    showBookingModal(booking = null) {
        const modalHtml = `
            <div class="modal fade" id="bookingModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${booking ? 'Edit Booking' : 'New Booking'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="bookingForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Service</label>
                                            <select class="form-select" name="service_id" required>
                                                <option value="">Select Service</option>
                                                ${this.currentServices.map(s => `
                                                    <option value="${s.id}" ${booking && booking.service?.id === s.id ? 'selected' : ''}>
                                                        ${s.name} - £${s.price}
                                                    </option>
                                                `).join('')}
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Date</label>
                                            <input type="date" class="form-control" name="booking_date" 
                                                   value="${booking ? booking.booking_date : ''}" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Time</label>
                                            <input type="time" class="form-control" name="booking_time" 
                                                   value="${booking ? booking.booking_time : ''}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Amount</label>
                                            <input type="number" step="0.01" class="form-control" name="amount" 
                                                   value="${booking ? (booking.amount || booking.payment_amount) : ''}" required>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">First Name</label>
                                            <input type="text" class="form-control" name="customer_first_name" 
                                                   value="${booking ? booking.customer_first_name : ''}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Last Name</label>
                                            <input type="text" class="form-control" name="customer_last_name" 
                                                   value="${booking ? booking.customer_last_name : ''}">
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Email</label>
                                            <input type="email" class="form-control" name="customer_email" 
                                                   value="${booking ? booking.customer_email : ''}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Phone</label>
                                            <input type="tel" class="form-control" name="customer_phone" 
                                                   value="${booking ? booking.customer_phone : ''}">
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Address</label>
                                    <textarea class="form-control" name="customer_address" rows="2">${booking ? booking.customer_address : ''}</textarea>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="checkbox" name="is_paid" 
                                                   ${booking && booking.is_paid ? 'checked' : ''}>
                                            <label class="form-check-label">Paid</label>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-check mb-3">
                                            <input class="form-check-input" type="checkbox" name="is_verified" 
                                                   ${booking && booking.is_verified ? 'checked' : ''}>
                                            <label class="form-check-label">Verified</label>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="adminPanel.saveBooking(${booking ? booking.id : null})">
                                ${booking ? 'Update' : 'Create'} Booking
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('bookingModal');
        if (existingModal) existingModal.remove();

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
        modal.show();
    }

    showServiceModal(service = null) {
        const modalHtml = `
            <div class="modal fade" id="serviceModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${service ? 'Edit Service' : 'New Service'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="serviceForm">
                                <div class="mb-3">
                                    <label class="form-label">Service Code</label>
                                    <input type="text" class="form-control" name="code" 
                                           value="${service ? service.code : ''}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Service Name</label>
                                    <input type="text" class="form-control" name="name" 
                                           value="${service ? service.name : ''}" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Description</label>
                                    <textarea class="form-control" name="description" rows="3">${service ? service.description : ''}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Price (£)</label>
                                    <input type="number" step="0.01" class="form-control" name="price" 
                                           value="${service ? service.price : ''}" required>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="active" 
                                           ${service && service.active ? 'checked' : (!service ? 'checked' : '')}>
                                    <label class="form-check-label">Active</label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="adminPanel.saveService(${service ? service.id : null})">
                                ${service ? 'Update' : 'Create'} Service
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('serviceModal');
        if (existingModal) existingModal.remove();

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
        modal.show();
    }

    async saveUser(userId) {
        const form = document.getElementById('userForm');
        const formData = new FormData(form);
        
        const userData = {
            email: formData.get('email'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            is_active: formData.has('is_active'),
            is_staff: formData.has('is_staff')
        };

        // Only include password if it's provided
        const password = formData.get('password');
        if (password) {
            userData.password = password;
        }

        if (userId) {
            await this.updateUser(userId, userData);
        } else {
            await this.createUser(userData);
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
        modal.hide();
    }

    async saveBooking(bookingId) {
        const form = document.getElementById('bookingForm');
        const formData = new FormData(form);
        
        const bookingData = {
            service_id: parseInt(formData.get('service_id')),
            booking_date: formData.get('booking_date'),
            booking_time: formData.get('booking_time'),
            customer_first_name: formData.get('customer_first_name'),
            customer_last_name: formData.get('customer_last_name'),
            customer_email: formData.get('customer_email'),
            customer_phone: formData.get('customer_phone'),
            customer_address: formData.get('customer_address'),
            amount: parseFloat(formData.get('amount')),
            is_paid: formData.has('is_paid'),
            is_verified: formData.has('is_verified')
        };

        if (bookingId) {
            await this.updateBooking(bookingId, bookingData);
        } else {
            await this.createBooking(bookingData);
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
        modal.hide();
    }

    async saveService(serviceId) {
        const form = document.getElementById('serviceForm');
        const formData = new FormData(form);
        
        const serviceData = {
            code: formData.get('code'),
            name: formData.get('name'),
            description: formData.get('description'),
            price: parseFloat(formData.get('price')),
            active: formData.has('active')
        };

        if (serviceId) {
            await this.updateService(serviceId, serviceData);
        } else {
            await this.createService(serviceData);
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('serviceModal'));
        modal.hide();
    }

    handleSearch(query, pageId) {
        // Implement search functionality for each page
        const rows = document.querySelectorAll(`#${pageId} tbody tr`);
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }
}

// Export function for data
function exportData(type) {
    let data = [];
    let filename = '';
    
    switch(type) {
        case 'users':
            data = window.adminPanel.currentUsers || [];
            filename = 'users_export.csv';
            break;
        case 'bookings':
            data = window.adminPanel.currentBookings || [];
            filename = 'bookings_export.csv';
            break;
        case 'services':
            data = window.adminPanel.currentServices || [];
            filename = 'services_export.csv';
            break;
    }
    
    if (data.length === 0) {
        alert('No data to export');
        return;
    }
    
    // Convert to CSV
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => {
            const value = row[header];
            return typeof value === 'object' ? JSON.stringify(value) : value;
        }).join(','))
    ].join('\n');
    
    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Logout function
function logout() {
    sessionStorage.removeItem('adminLoggedIn');
    sessionStorage.removeItem('adminUser');
    window.location.href = '/static/admin/login.html';
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});