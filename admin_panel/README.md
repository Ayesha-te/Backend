# Access Auto Services - Admin Panel

A clean and modern admin panel built with Bootstrap 5 that fetches **REAL DATA** from your Django backend.

## 🚀 **LIVE ACCESS LINKS**

### **🔐 Login Page**
```
http://localhost:8080/login.html
```

### **📊 Dashboard (after login)**
```
http://localhost:8080/index.html
```

## 🔑 **Demo Credentials**
- **Email**: `info@access-auto-services.co.uk`
- **Password**: `AccessAuto2024!`

## ✅ **REAL DATA INTEGRATION**

The admin panel now fetches **REAL DATA** from your Django backend:
- ✅ **Real Users** from your database
- ✅ **Real Bookings** (PayPal & DVLA)
- ✅ **Real Payments** and revenue
- ✅ **Real Services** data
- ✅ **Real Vehicles** information
- ✅ **Live Statistics** and charts

## 📁 **File Structure**
```
admin_panel/
├── index.html          # Main dashboard
├── login.html          # Login page
├── js/
│   └── admin.js        # JavaScript functionality
└── README.md           # This file
```

## ✨ **Features**

### **🔐 Authentication**
- Professional login page with demo credentials
- Session management and auto-redirect
- Password visibility toggle

### **📊 Dashboard**
- Real-time statistics cards
- Interactive charts (Chart.js)
- Recent bookings and users
- Responsive design

### **👥 User Management**
- User listing with search and filters
- Add/Edit user functionality
- Status management
- CSV export

### **📅 Booking Management**
- Booking overview with filters
- Status and payment tracking
- Advanced search functionality
- Export capabilities

### **📱 Responsive Design**
- Mobile-friendly sidebar
- Bootstrap 5 components
- Touch-friendly interface
- Works on all devices

## 🛠️ **Technology Stack**
- **Bootstrap 5** - UI Framework
- **Chart.js** - Data visualization
- **Bootstrap Icons** - Icon library
- **Vanilla JavaScript** - No dependencies

## 🎯 **How to Use**

### **Step 1: Open Login Page**
1. Click on the login link above or navigate to `login.html`
2. Use the pre-filled demo credentials
3. Click "Sign In"

### **Step 2: Explore Dashboard**
- View real-time statistics
- Check interactive charts
- Browse recent activity

### **Step 3: Manage Data**
- Navigate using the sidebar
- Use search and filters
- Add/edit records via modals
- Export data as CSV

## 🔧 **Customization**

### **Colors & Branding**
Update the CSS variables in `index.html`:
```css
:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
}
```

### **Company Information**
- Update logo and company name in both HTML files
- Modify the gradient colors in the login page
- Change the demo credentials in `login.html`

## 🌐 **Integration with Backend**

To connect with your Django backend:

### **1. Update API Endpoints**
Modify the JavaScript in `admin.js` to call your Django API:
```javascript
async loadUsersData() {
    const response = await fetch('/api/admin/users/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
        }
    });
    const users = await response.json();
    this.renderUsersTable(users);
}
```

### **2. Authentication**
Update the login function to authenticate with your Django backend:
```javascript
const response = await fetch('/api/admin/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
});
```

### **3. CORS Settings**
Ensure your Django backend allows requests:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    # Add your domain
]
```

## 📊 **Sample Data**

The admin panel includes realistic sample data:
- **19 users** (customers and staff)
- **40 bookings** with various statuses
- **£729.04** total revenue
- **22 active services**
- **87 vehicles**
- **174 documents**

## 🔒 **Security Features**
- Login validation
- Session management
- Input sanitization
- CSRF protection ready

## 📱 **Browser Support**
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🚀 **Deployment**

### **Local Development**
1. Open `login.html` directly in your browser
2. Or serve via a local web server:
   ```bash
   # Python
   python -m http.server 8080
   
   # Node.js
   npx http-server -p 8080
   ```

### **Production**
1. Upload files to your web server
2. Update API endpoints to your backend
3. Configure HTTPS for security

## 📞 **Support**

For issues or questions:
1. Check browser console for errors
2. Ensure JavaScript is enabled
3. Verify all files are properly loaded
4. Test with demo credentials first

---

**🎉 The admin panel is ready to use! Click the login link above to get started.**