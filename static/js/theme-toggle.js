// Enhanced Theme Management for All Pages
class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme() || 'dark';
        this.init();
    }
    
    init() {
        // Apply theme immediately
        this.applyTheme(this.currentTheme, false);
        
        // Setup toggle button when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupToggleButton());
        } else {
            this.setupToggleButton();
        }
        
        console.log(`🎨 ThemeManager initialized: ${this.currentTheme}`);
    }
    
    getStoredTheme() {
        try {
            return localStorage.getItem('chess-theme');
        } catch (e) {
            console.warn('localStorage not available');
            return null;
        }
    }
    
    getSystemTheme() {
        try {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        } catch (e) {
            return 'dark'; // fallback
        }
    }
    
    setStoredTheme(theme) {
        try {
            localStorage.setItem('chess-theme', theme);
        } catch (e) {
            console.warn('Could not save theme to localStorage');
        }
    }
    
    applyTheme(theme, animate = true) {
        const root = document.documentElement;
        
        // Add transition for smooth theme switching
        if (animate) {
            root.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                root.style.transition = '';
            }, 300);
        }
        
        if (theme === 'light') {
            root.setAttribute('data-theme', 'light');
        } else {
            root.removeAttribute('data-theme');
            theme = 'dark'; // normalize
        }
        
        this.currentTheme = theme;
        this.setStoredTheme(theme);
        this.updateToggleButton(theme);
        
        // Dispatch event for other components
        try {
            window.dispatchEvent(new CustomEvent('themeChanged', { 
                detail: { theme: theme } 
            }));
        } catch (e) {
            // Fallback for older browsers
            console.log(`Theme changed to: ${theme}`);
        }
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme, true);
        this.showThemeChangeNotification(newTheme);
        console.log(`🎨 Theme toggled to: ${newTheme}`);
    }
    
    updateToggleButton(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        const toggleText = toggleBtn?.querySelector('.toggle-text');
        
        if (toggleText) {
            toggleText.textContent = theme === 'dark' ? 'Dark' : 'Light';
        }
        
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
        }
    }
    
    setupToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        
        if (toggleBtn) {
            // Remove any existing listeners
            const newToggleBtn = toggleBtn.cloneNode(true);
            toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);
            
            newToggleBtn.addEventListener('click', () => {
                this.toggleTheme();
                
                // Visual feedback
                newToggleBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    newToggleBtn.style.transform = '';
                }, 150);
            });
            
            // Update button state
            this.updateToggleButton(this.currentTheme);
        }
    }
    
    showThemeChangeNotification(theme) {
        // Remove any existing notifications
        const existing = document.querySelector('.theme-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `
            <span class="theme-icon">${theme === 'dark' ? '🌙' : '☀️'}</span>
            <span>${theme === 'dark' ? 'Dark' : 'Light'} mode activated</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

// Initialize theme manager immediately
window.themeManager = new ThemeManager();

// Also handle page navigation (for SPA-like behavior)
document.addEventListener('DOMContentLoaded', function() {
    if (window.themeManager) {
        window.themeManager.setupToggleButton();
    }
});
