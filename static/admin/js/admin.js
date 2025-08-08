// Access Auto Services Admin Panel JavaScript

class AdminPanel {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {};
        this.apiBaseUrl = '/api'; // Same server API endpoints
        this.currentBookings = [];
        this.currentServices = [];
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEventListeners();
        this.initializeCharts();
        this.showPage('dashboard');
    }

    checkAuth() {
        // For demo purposes, we'll skip auth check
        // In production, implement proper authentication
        console.log('Admin panel loaded');
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
            // Load dashboard statistics
            const [usersCount, bookingsCount, paymentsTotal, services] = await Promise.all([
                this.apiCall('/users/count/'),
                this.apiCall('/bookings/count/'),
                this.apiCall('/payments/total/'),
                this.apiCall('/services/')
            ]);

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
            const response = await this.apiCall('/bookings/');
            this.currentBookings = response.results || [];
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
            this.renderUsersTable(response.results || []);
        } catch (error) {
            console.error('Error loading users:', error);
            this.showError('Failed to load users');
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
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        return await response.json();
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
                        <div class="fw-bold">${booking.customer_first_name} ${booking.customer_last_name}</div>
                        <small class="text-muted">${booking.service.name} - ${this.formatDate(booking.booking_date)}</small>
                    </div>
                    <span class="badge ${this.getStatusBadgeClass(booking.status)} rounded-pill">
                        ${booking.status}
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
                        <div class="fw-bold">${user.first_name} ${user.last_name}</div>
                        <small class="text-muted">${user.email}</small>
                    </div>
                    <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'} rounded-pill">
                        ${user.booking_count} bookings
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
                    <td colspan="8" class="text-center text-muted">No bookings found</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = this.currentBookings.map(booking => `
            <tr>
                <td>#${booking.id}</td>
                <td>
                    ${booking.customer_first_name} ${booking.customer_last_name}<br>
                    <small class="text-muted">${booking.customer_email}</small>
                </td>
                <td>${booking.service.name}</td>
                <td>
                    ${this.formatDate(booking.booking_date)}<br>
                    <small class="text-muted">${booking.booking_time}</small>
                </td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(booking.status)}">
                        ${booking.status}
                    </span>
                </td>
                <td>
                    <span class="badge ${this.getPaymentStatusBadgeClass(booking.payment_status)}">
                        ${booking.payment_status}
                    </span>
                </td>
                <td>£${booking.amount.toFixed(2)}</td>
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
                    <td colspan="6" class="text-center text-muted">No users found</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = users.map(user => `
            <tr>
                <td>${user.first_name} ${user.last_name}</td>
                <td>${user.email}</td>
                <td>${user.booking_count}</td>
                <td>
                    <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>${this.formatDate(user.date_joined)}</td>
                <td>
                    <span class="badge ${user.is_staff ? 'bg-primary' : 'bg-light text-dark'}">
                        ${user.is_staff ? 'Staff' : 'Customer'}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    // CRUD Operations
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
                                                    <option value="${s.id}" ${booking && booking.service.id === s.id ? 'selected' : ''}>
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
                                                   value="${booking ? booking.amount : ''}" required>
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
                                        <div class="mb-3">
                                            <label class="form-label">Payment Status</label>
                                            <select class="form-select" name="payment_status">
                                                <option value="pending" ${booking && booking.payment_status === 'pending' ? 'selected' : ''}>Pending</option>
                                                <option value="completed" ${booking && booking.payment_status === 'completed' ? 'selected' : ''}>Completed</option>
                                                <option value="failed" ${booking && booking.payment_status === 'failed' ? 'selected' : ''}>Failed</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <div class="form-check mt-4">
                                                <input class="form-check-input" type="checkbox" name="is_paid" 
                                                       ${booking && booking.is_paid ? 'checked' : ''}>
                                                <label class="form-check-label">Paid</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="is_verified" 
                                                       ${booking && booking.is_verified ? 'checked' : ''}>
                                                <label class="form-check-label">Verified</label>
                                            </div>
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
            payment_status: formData.get('payment_status'),
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
        console.log(`Searching for "${query}" in ${pageId}`);
    }
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});

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

        // Logout functionality
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
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

    logout() {
        sessionStorage.removeItem('adminLoggedIn');
        sessionStorage.removeItem('adminUser');
        window.location.href = '/static/admin/login.html';
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
        document.title = `${this.getPageTitle(page)} - Access Auto Services Admin`;

        // Load page-specific data
        this.loadPageData(page);
        this.currentPage = page;
    }

    getPageTitle(page) {
        const titles = {
            dashboard: 'Dashboard',
            users: 'User Management',
            bookings: 'Booking Management',
            payments: 'Payment Management',
            services: 'Service Management',
            vehicles: 'Vehicle Management'
        };
        return titles[page] || 'Dashboard';
    }

    loadPageData(page) {
        switch (page) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'bookings':
                this.loadBookingsData();
                break;
            case 'payments':
                this.loadPaymentsData();
                break;
        }
    }

    handleSearch(query, pageId) {
        // Simple search implementation
        const rows = document.querySelectorAll(`#${pageId} tbody tr`);
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    initializeCharts() {
        // Initialize Chart.js charts
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
                    label: 'PayPal Bookings',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4
                }, {
                    label: 'DVLA Bookings',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Booking Trends (Real Data)'
                    }
                },
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
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Service Distribution (Real Data)'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    loadDashboardData() {
        this.loadDashboardStats();
        this.loadRecentBookings();
        this.loadRecentUsers();
        this.loadChartData();
        this.updateSidebarBadges();
    }

    async loadRecentBookings() {
        const container = document.getElementById('recentBookings');
        if (!container) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/bookings/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (!response.ok) throw new Error('Failed to fetch bookings');
            
            const data = await response.json();
            const bookings = (data.results || data).slice(0, 5); // Get first 5 bookings

            if (bookings.length === 0) {
                container.innerHTML = `
                    <div class="list-group-item text-center text-muted py-4">
                        <i class="bi bi-calendar-x me-2"></i>
                        No recent bookings found
                    </div>
                `;
            } else {
                container.innerHTML = bookings.map(booking => `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${booking.user?.first_name || 'Unknown'} ${booking.user?.last_name || 'User'}</h6>
                            <p class="mb-1">${booking.service_type} - #${booking.id}</p>
                            <small class="text-muted">${this.getRelativeTime(booking.created_at)}</small>
                        </div>
                        <span class="badge bg-${this.getStatusColor(booking.status)} rounded-pill">${booking.status}</span>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading recent bookings:', error);
            container.innerHTML = `
                <div class="list-group-item text-center text-muted">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Unable to load recent bookings
                </div>
            `;
        }
    }

    async loadRecentUsers() {
        const container = document.getElementById('recentUsers');
        if (!container) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/users/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (!response.ok) throw new Error('Failed to fetch users');
            
            const data = await response.json();
            const users = (data.results || data).slice(0, 5); // Get first 5 users

            if (users.length === 0) {
                container.innerHTML = `
                    <div class="list-group-item text-center text-muted py-4">
                        <i class="bi bi-people me-2"></i>
                        No recent users found
                    </div>
                `;
            } else {
                container.innerHTML = users.map(user => `
                    <div class="list-group-item">
                        <div class="d-flex align-items-center">
                            <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                ${(user.first_name?.[0] || 'U')}${(user.last_name?.[0] || '')}
                            </div>
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${user.first_name || 'Unknown'} ${user.last_name || 'User'}</h6>
                                <p class="mb-1">${user.email}</p>
                                <small class="text-muted">${this.getRelativeTime(user.date_joined)}</small>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading recent users:', error);
            container.innerHTML = `
                <div class="list-group-item text-center text-muted">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Unable to load recent users
                </div>
            `;
        }
    }

    async loadUsersData() {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/users/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (!response.ok) throw new Error('Failed to fetch users');
            
            const data = await response.json();
            const users = data.results || data;

            if (users.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">
                            <i class="bi bi-people me-2"></i>
                            No users found in the database
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = users.map(user => {
                    const fullName = `${user.first_name || 'Unknown'} ${user.last_name || 'User'}`;
                    const initials = `${user.first_name?.[0] || 'U'}${user.last_name?.[0] || ''}`;
                    const userType = user.is_staff ? 'staff' : 'customer';
                    const status = user.is_active ? 'active' : 'inactive';
                    
                    return `
                        <tr>
                            <td><input type="checkbox" class="form-check-input" value="${user.id}"></td>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px; font-size: 0.75rem;">
                                        ${initials}
                                    </div>
                                    ${fullName}
                                </div>
                            </td>
                            <td>${user.email}</td>
                            <td><span class="badge bg-${status === 'active' ? 'success' : 'secondary'}">${status}</span></td>
                            <td><span class="badge bg-${userType === 'staff' ? 'primary' : 'info'}">${userType}</span></td>
                            <td>${new Date(user.date_joined).toLocaleDateString()}</td>
                            <td>${user.booking_count || 0}</td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary" onclick="editUser(${user.id})">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-outline-danger" onclick="deleteUser(${user.id})">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (error) {
            console.error('Error loading users:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Unable to load users data. Please check your backend connection.
                    </td>
                </tr>
            `;
        }
    }

    async loadBookingsData() {
        const tbody = document.getElementById('bookingsTableBody');
        if (!tbody) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/bookings/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (!response.ok) throw new Error('Failed to fetch bookings');
            
            const data = await response.json();
            const bookings = data.results || data;

            if (bookings.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center text-muted py-4">
                            <i class="bi bi-calendar-x me-2"></i>
                            No bookings found in the database
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = bookings.map(booking => {
                    const customerName = booking.user ? 
                        `${booking.user.first_name || 'Unknown'} ${booking.user.last_name || 'User'}` : 
                        'Unknown Customer';
                    
                    const bookingDate = booking.booking_date ? 
                        new Date(booking.booking_date).toLocaleDateString() : 
                        'Not set';
                    
                    const bookingTime = booking.booking_time || 'Not set';
                    
                    return `
                        <tr>
                            <td><input type="checkbox" class="form-check-input" value="${booking.id}"></td>
                            <td>#${booking.id}</td>
                            <td>${customerName}</td>
                            <td>${booking.service_type || 'Unknown Service'}</td>
                            <td>${bookingDate} ${bookingTime}</td>
                            <td><span class="badge bg-${this.getStatusColor(booking.status)}">${booking.status}</span></td>
                            <td><span class="badge bg-${booking.payment_status === 'completed' ? 'success' : 'warning'}">${booking.payment_status || 'pending'}</span></td>
                            <td>£${(booking.amount || 0).toFixed(2)}</td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary" onclick="editBooking('${booking.id}')">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-outline-danger" onclick="deleteBooking('${booking.id}')">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (error) {
            console.error('Error loading bookings:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Unable to load bookings data. Please check your backend connection.
                    </td>
                </tr>
            `;
        }
    }

    getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'completed': 'success',
            'cancelled': 'danger',
            'active': 'success',
            'inactive': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toastContainer.removeChild(toast);
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }

    async loadDashboardStats() {
        try {
            // Load users count
            const usersResponse = await fetch(`${this.apiBaseUrl}/users/count/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (usersResponse.ok) {
                const usersData = await usersResponse.json();
                document.getElementById('totalUsers').textContent = usersData.total || 0;
                document.getElementById('newUsers').textContent = `+${usersData.new_this_week || 0} this week`;
            }

            // Load bookings count
            const bookingsResponse = await fetch(`${this.apiBaseUrl}/bookings/count/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (bookingsResponse.ok) {
                const bookingsData = await bookingsResponse.json();
                document.getElementById('totalBookings').textContent = bookingsData.total || 0;
                document.getElementById('todayBookings').textContent = `+${bookingsData.today || 0} today`;
            }

            // Load payments total
            const paymentsResponse = await fetch(`${this.apiBaseUrl}/payments/total/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (paymentsResponse.ok) {
                const paymentsData = await paymentsResponse.json();
                document.getElementById('totalRevenue').textContent = `£${(paymentsData.total || 0).toFixed(2)}`;
                document.getElementById('todayRevenue').textContent = `+£${(paymentsData.today || 0).toFixed(2)} today`;
            }

            // Load services count
            const servicesResponse = await fetch(`${this.apiBaseUrl}/services/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (servicesResponse.ok) {
                const servicesData = await servicesResponse.json();
                const activeServices = (servicesData.results || []).filter(s => s.active).length;
                document.getElementById('totalServices').textContent = activeServices;
                document.getElementById('servicesChange').textContent = 'PayPal & DVLA';
            }

        } catch (error) {
            console.error('Error loading dashboard stats:', error);
            // Set error state with better messaging
            document.getElementById('totalUsers').textContent = '0';
            document.getElementById('newUsers').textContent = 'No data available';
            document.getElementById('totalBookings').textContent = '0';
            document.getElementById('todayBookings').textContent = 'No data available';
            document.getElementById('totalRevenue').textContent = '£0.00';
            document.getElementById('todayRevenue').textContent = 'No data available';
            document.getElementById('totalServices').textContent = '0';
            document.getElementById('servicesChange').textContent = 'No data available';
        }
    }

    async updateSidebarBadges() {
        try {
            // Update sidebar badges with real counts
            const [usersResponse, bookingsResponse, servicesResponse] = await Promise.all([
                fetch(`${this.apiBaseUrl}/users/count/`),
                fetch(`${this.apiBaseUrl}/bookings/count/`),
                fetch(`${this.apiBaseUrl}/services/`)
            ]);

            if (usersResponse.ok) {
                const usersData = await usersResponse.json();
                const usersBadge = document.querySelector('a[data-page="users"] .badge');
                if (usersBadge) usersBadge.textContent = usersData.total || 0;
            }

            if (bookingsResponse.ok) {
                const bookingsData = await bookingsResponse.json();
                const bookingsBadge = document.querySelector('a[data-page="bookings"] .badge');
                if (bookingsBadge) bookingsBadge.textContent = bookingsData.total || 0;
            }

            if (servicesResponse.ok) {
                const servicesData = await servicesResponse.json();
                const vehiclesBadge = document.querySelector('a[data-page="vehicles"] .badge');
                if (vehiclesBadge) vehiclesBadge.textContent = (servicesData.results || []).length;
            }

        } catch (error) {
            console.error('Error updating sidebar badges:', error);
        }
    }

    getRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        return date.toLocaleDateString();
    }

    async loadChartData() {
        try {
            // Load booking trends data
            const trendsResponse = await fetch(`${this.apiBaseUrl}/bookings/trends/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (trendsResponse.ok) {
                const trendsData = await trendsResponse.json();
                this.updateBookingChart(trendsData);
            }

            // Load service distribution data
            const servicesResponse = await fetch(`${this.apiBaseUrl}/bookings/service-distribution/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (servicesResponse.ok) {
                const servicesData = await servicesResponse.json();
                this.updateServiceChart(servicesData);
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    updateBookingChart(data) {
        if (this.charts.booking) {
            if (data.labels && data.paypal_data && data.dvla_data) {
                this.charts.booking.data.labels = data.labels;
                this.charts.booking.data.datasets[0].data = data.paypal_data;
                this.charts.booking.data.datasets[1].data = data.dvla_data;
            } else {
                // Show empty state
                this.charts.booking.data.labels = ['No Data'];
                this.charts.booking.data.datasets[0].data = [0];
                this.charts.booking.data.datasets[1].data = [0];
            }
            this.charts.booking.update();
        }
    }

    updateServiceChart(data) {
        if (this.charts.service) {
            if (data.labels && data.values && data.values.length > 0) {
                this.charts.service.data.labels = data.labels;
                this.charts.service.data.datasets[0].data = data.values;
            } else {
                // Show empty state
                this.charts.service.data.labels = ['No Data'];
                this.charts.service.data.datasets[0].data = [1];
            }
            this.charts.service.update();
        }
    }

    async loadPaymentsData() {
        try {
            // Load payment statistics
            const paymentsResponse = await fetch(`${this.apiBaseUrl}/payments/total/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (paymentsResponse.ok) {
                const paymentsData = await paymentsResponse.json();
                document.getElementById('paypalRevenue').textContent = `£${(paymentsData.paypal || 0).toFixed(2)}`;
                document.getElementById('dvlaRevenue').textContent = `£${(paymentsData.dvla || 0).toFixed(2)}`;
                document.getElementById('totalPaymentRevenue').textContent = `£${(paymentsData.total || 0).toFixed(2)}`;
                document.getElementById('todayPaymentRevenue').textContent = `£${(paymentsData.today || 0).toFixed(2)}`;
            }

            // Load recent payments (using bookings data as proxy)
            const bookingsResponse = await fetch(`${this.apiBaseUrl}/bookings/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (bookingsResponse.ok) {
                const data = await bookingsResponse.json();
                const bookings = (data.results || data).filter(b => b.payment_status === 'completed').slice(0, 10);
                
                const tbody = document.getElementById('paymentsTableBody');
                if (tbody) {
                    if (bookings.length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="6" class="text-center text-muted py-4">
                                    <i class="bi bi-credit-card me-2"></i>
                                    No completed payments found
                                </td>
                            </tr>
                        `;
                    } else {
                        tbody.innerHTML = bookings.map(booking => {
                            const customerName = booking.user ? 
                                `${booking.user.first_name || 'Unknown'} ${booking.user.last_name || 'User'}` : 
                                'Unknown Customer';
                            
                            return `
                                <tr>
                                    <td>#${booking.id}</td>
                                    <td>${customerName}</td>
                                    <td><span class="badge bg-${booking.type === 'paypal' ? 'primary' : 'info'}">${booking.service_type}</span></td>
                                    <td>£${(booking.amount || 0).toFixed(2)}</td>
                                    <td><span class="badge bg-success">Completed</span></td>
                                    <td>${new Date(booking.created_at).toLocaleDateString()}</td>
                                </tr>
                            `;
                        }).join('');
                    }
                }
            }

        } catch (error) {
            console.error('Error loading payments data:', error);
            const tbody = document.getElementById('paymentsTableBody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted py-4">
                            <i class="bi bi-exclamation-triangle me-2"></i>
                            Unable to load payments data. Please check your backend connection.
                        </td>
                    </tr>
                `;
            }
        }
    }
}

// Global functions for button actions
function editUser(userId) {
    console.log('Edit user:', userId);
    // Implement edit user functionality
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        console.log('Delete user:', userId);
        // Implement delete user functionality
    }
}

function editBooking(bookingId) {
    console.log('Edit booking:', bookingId);
    // Implement edit booking functionality
}

function deleteBooking(bookingId) {
    if (confirm('Are you sure you want to delete this booking?')) {
        console.log('Delete booking:', bookingId);
        // Implement delete booking functionality
    }
}

function exportData(type) {
    console.log('Export data:', type);
    // Implement export functionality
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AdminPanel();
});