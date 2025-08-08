// Version file to force cache refresh
window.ADMIN_VERSION = '2.0.1';
window.LAST_UPDATED = '2025-08-08T15:00:00Z';

// Force reload if version mismatch
const storedVersion = localStorage.getItem('admin_version');
if (storedVersion !== window.ADMIN_VERSION) {
    localStorage.setItem('admin_version', window.ADMIN_VERSION);
    console.log('Admin panel updated to version', window.ADMIN_VERSION);
}