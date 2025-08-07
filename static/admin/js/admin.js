// Access Auto Services Admin Panel JavaScript

class AdminPanel {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {};
        this.apiBaseUrl = '/api'; // Same server API endpoints
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEventListeners();
        this.initializeCharts();
        this.showPage('dashboard');
    }

    checkAuth() {
        if (!sessionStorage.getItem('adminLoggedIn')) {
            window.location.href = '/static/admin/login.html';
            return;
        }
        
        // Set user info
        const userEmail = sessionStorage.getItem('adminUser');
        const userNameElement = document.getElementById('userName');
        if (userNameElement && userEmail) {
            userNameElement.textContent = userEmail.split('@')[0];
        }
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
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'PayPal Bookings',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4
                }, {
                    label: 'DVLA Bookings',
                    data: [2, 3, 20, 5, 1, 4],
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
                        text: 'Booking Trends'
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
                labels: ['PayPal Services', 'DVLA Services'],
                datasets: [{
                    data: [65, 35],
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
                        text: 'Service Distribution'
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
            // Set error state
            document.getElementById('totalUsers').textContent = 'Error';
            document.getElementById('totalBookings').textContent = 'Error';
            document.getElementById('totalRevenue').textContent = 'Error';
            document.getElementById('totalServices').textContent = 'Error';
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
        if (this.charts.booking && data.labels && data.paypal_data && data.dvla_data) {
            this.charts.booking.data.labels = data.labels;
            this.charts.booking.data.datasets[0].data = data.paypal_data;
            this.charts.booking.data.datasets[1].data = data.dvla_data;
            this.charts.booking.update();
        }
    }

    updateServiceChart(data) {
        if (this.charts.service && data.labels && data.values) {
            this.charts.service.data.labels = data.labels;
            this.charts.service.data.datasets[0].data = data.values;
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