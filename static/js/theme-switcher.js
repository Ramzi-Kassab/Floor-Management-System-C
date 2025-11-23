/**
 * Theme Switcher for Logistics Management System
 */

(function() {
    'use strict';
    
    const STORAGE_KEY = 'logistics-theme';
    const DEFAULT_THEME = 'light';
    
    const themes = {
        light: { name: 'Light', icon: 'bi-sun-fill', color: '#ffffff' },
        dark: { name: 'Dark', icon: 'bi-moon-stars-fill', color: '#1a1a1a' },
        blue: { name: 'Blue', icon: 'bi-droplet-fill', color: '#0066cc' },
        green: { name: 'Green', icon: 'bi-tree-fill', color: '#2e7d32' },
        'high-contrast': { name: 'High Contrast', icon: 'bi-circle-half', color: '#000000' }
    };
    
    function getCurrentTheme() {
        return localStorage.getItem(STORAGE_KEY) || DEFAULT_THEME;
    }
    
    function setTheme(themeName) {
        if (!themes[themeName]) {
            themeName = DEFAULT_THEME;
        }
        document.documentElement.setAttribute('data-theme', themeName);
        localStorage.setItem(STORAGE_KEY, themeName);
        updateToggleButton(themeName);
    }
    
    function updateToggleButton(themeName) {
        const btn = document.getElementById('theme-toggle-btn');
        if (btn) {
            const icon = btn.querySelector('i');
            if (icon) {
                Object.values(themes).forEach(t => icon.classList.remove(t.icon));
                icon.classList.add(themes[themeName].icon);
            }
        }
    }
    
    function createThemeSwitcher() {
        const currentTheme = getCurrentTheme();
        const switcher = document.createElement('div');
        switcher.className = 'theme-switcher';
        
        let optionsHTML = '<h6 class="mb-3">Choose Theme</h6>';
        for (const [key, config] of Object.entries(themes)) {
            const checkmark = key === currentTheme ? '<i class="bi bi-check2 ms-auto"></i>' : '';
            optionsHTML += '<div class="theme-option" data-theme="' + key + '">' +
                '<div class="theme-color-preview" style="background-color: ' + config.color + '"></div>' +
                '<span>' + config.name + '</span>' + checkmark + '</div>';
        }
        
        switcher.innerHTML = '<button id="theme-toggle-btn" class="theme-toggle-btn">' +
            '<i class="bi ' + themes[currentTheme].icon + '"></i></button>' +
            '<div id="theme-options" class="theme-options">' + optionsHTML + '</div>';
        
        document.body.appendChild(switcher);
        
        document.getElementById('theme-toggle-btn').addEventListener('click', function() {
            document.getElementById('theme-options').classList.toggle('show');
        });
        
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', function() {
                setTheme(this.getAttribute('data-theme'));
                document.getElementById('theme-options').classList.remove('show');
            });
        });
        
        document.addEventListener('click', function(e) {
            const switcher = document.querySelector('.theme-switcher');
            if (switcher && !switcher.contains(e.target)) {
                document.getElementById('theme-options').classList.remove('show');
            }
        });
    }
    
    function init() {
        setTheme(getCurrentTheme());
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createThemeSwitcher);
        } else {
            createThemeSwitcher();
        }
    }
    
    window.ThemeSwitcher = { setTheme, getCurrentTheme };
    init();
})();

// Responsive utilities
(function() {
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) || window.innerWidth < 768;
    }
    
    function updateMobileClass() {
        document.body.classList[isMobileDevice() ? 'add' : 'remove']('mobile-device');
    }
    
    function enhanceResponsiveTables() {
        document.querySelectorAll('.table-responsive table').forEach(table => {
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            table.querySelectorAll('tbody tr').forEach(row => {
                row.querySelectorAll('td').forEach((cell, index) => {
                    if (headers[index]) cell.setAttribute('data-label', headers[index]);
                });
            });
        });
    }
    
    function init() {
        updateMobileClass();
        enhanceResponsiveTables();
        window.addEventListener('resize', () => setTimeout(updateMobileClass, 250));
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
