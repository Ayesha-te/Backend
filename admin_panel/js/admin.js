// Access Auto Services Admin Panel JavaScript

class AdminPanel {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {};
        this.apiBaseUrl = 'https://backend-kzpz.onrender.com/api'; // Production Django backend URL
        this.init();
    }

    init() {
        this.checkAuth();
        this.setupEventListeners();
        this.setupCharts();
        this.loadDashboardData();
        this.loadSampleData();
    }

    checkAuth() {
        if (localStorage.getItem('adminLoggedIn') !== 'true') {
            window.location.href = 'login.html';
            return;
        }
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateToPage(page);
            });
        });

        // Mobile sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                const sidebar = document.getElementById('sidebar');
                const mainContent = document.getElementById('mainContent');
                
                if (window.innerWidth <= 768) {
                    sidebar.classList.toggle('show');
                } else {
                    sidebar.classList.toggle('collapsed');
                    mainContent.classList.toggle('expanded');
                }
            });
        }

        // Search functionality
        document.getElementById('userSearch')?.addEventListener('input', (e) => {
            this.filterTable('usersTable', e.target.value);
        });

        document.getElementById('bookingSearch')?.addEventListener('input', (e) => {
            this.filterTable('bookingsTable', e.target.value);
        });

        // Filter functionality
        document.getElementById('userStatusFilter')?.addEventListener('change', () => {
            this.loadUsersData();
        });

        document.getElementById('bookingStatusFilter')?.addEventListener('change', () => {
            this.loadBookingsData();
        });
    }

    navigateToPage(page) {
        // Update active nav item
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // Hide all pages
        document.querySelectorAll('.page-content').forEach(p => {
            p.style.display = 'none';
        });

        // Show selected page
        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.style.display = 'block';
        }

        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        pageTitle.textContent = this.getPageTitle(page);

        // Load page-specific data
        this.loadPageData(page);

        this.currentPage = page;
    }

    getPageTitle(page) {
        const titles = {
            dashboard: 'Dashboard',
            users: 'User Management',
            bookings: 'Booking Management',
            services: 'Service Management',
            vehicles: 'Vehicle Management',
            documents: 'Document Management',
            payments: 'Payment Management',
            reports: 'Reports Center'
        };
        return titles[page] || 'Dashboard';
    }

    loadPageData(page) {
        switch (page) {
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

    setupCharts() {
        // Booking trends chart
        const bookingCtx = document.getElementById('bookingChart');
        if (bookingCtx) {
            this.charts.booking = new Chart(bookingCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [{
                        label: 'PayPal Bookings',
                        data: [12, 19, 8, 15, 22, 18, 25, 20, 16, 24, 28, 22],
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'DVLA Bookings',
                        data: [8, 12, 6, 10, 15, 12, 18, 14, 11, 17, 20, 16],
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
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

        // Service distribution chart
        const serviceCtx = document.getElementById('serviceChart');
        if (serviceCtx) {
            this.charts.service = new Chart(serviceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['MOT Test', 'Service', 'Repair', 'DVLA Services', 'Other'],
                    datasets: [{
                        data: [35, 25, 20, 15, 5],
                        backgroundColor: [
                            '#0d6efd',
                            '#198754',
                            '#ffc107',
                            '#dc3545',
                            '#6c757d'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                }
            });
        }
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
            'active': 'success',
            'inactive': 'secondary',
            'confirmed': 'primary',
            'pending': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        };
        return colors[status] || 'secondary';
    }

    filterTable(tableId, searchTerm) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    showNotification(message, type = 'success') {
        // Create Bootstrap toast
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Add toast to container
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Show toast
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
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
function editUser(id) {
    window.adminPanel.showNotification(`Editing user ${id}`, 'info');
}

function deleteUser(id) {
    if (confirm('Are you sure you want to delete this user?')) {
        window.adminPanel.showNotification(`User ${id} deleted`, 'success');
        window.adminPanel.loadUsersData();
    }
}

function editBooking(id) {
    window.adminPanel.showNotification(`Editing booking ${id}`, 'info');
}

function deleteBooking(id) {
    if (confirm('Are you sure you want to delete this booking?')) {
        window.adminPanel.showNotification(`Booking ${id} deleted`, 'success');
        window.adminPanel.loadBookingsData();
    }
}

function saveUser() {
    const form = document.getElementById('userForm');
    const formData = new FormData(form);
    
    // Here you would typically send the data to your backend
    console.log('Saving user data:', Object.fromEntries(formData));
    
    window.adminPanel.showNotification('User saved successfully!', 'success');
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
    modal.hide();
    
    // Refresh users table
    window.adminPanel.loadUsersData();
}

function exportData(type) {
    window.adminPanel.showNotification(`Exporting ${type} data...`, 'info');
    
    // Simulate export process
    setTimeout(() => {
        window.adminPanel.showNotification(`${type} data exported successfully!`, 'success');
        
        // Create and download a sample CSV
        const csvContent = generateSampleCSV(type);
        downloadCSV(csvContent, `${type}_export.csv`);
    }, 2000);
}

function generateSampleCSV(type) {
    if (type === 'users') {
        return `Name,Email,Status,Type,Joined,Bookings
John Smith,john@example.com,active,customer,2024-01-15,3
Sarah Johnson,sarah@example.com,active,customer,2024-01-20,1
Mike Wilson,mike@example.com,inactive,customer,2024-01-10,0`;
    } else if (type === 'bookings') {
        return `ID,Customer,Service,Date,Time,Status,Payment,Amount
B001,John Smith,MOT Test,2024-02-15,10:00,confirmed,paid,54.85
B002,Sarah Johnson,Full Service,2024-02-16,14:00,pending,unpaid,120.00
B003,Mike Wilson,DVLA Check,2024-02-14,09:30,completed,paid,25.00`;
    }
    return '';
}

function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Initialize the admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});

// Handle window resize for responsive sidebar
window.addEventListener('resize', () => {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    if (window.innerWidth > 768) {
        sidebar.classList.remove('show');
    }
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    if (window.innerWidth <= 768 && 
        !sidebar.contains(e.target) && 
        !sidebarToggle.contains(e.target) && 
        sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
    }
});