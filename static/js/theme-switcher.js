/**
 * Theme Switcher for Logistics Management System
 * Enhanced with custom color controls
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'logistics-theme';
    const CUSTOM_COLORS_KEY = 'logistics-custom-colors';
    const DEFAULT_THEME = 'light';

    const themes = {
        light: { name: 'Light', icon: 'bi-sun-fill', color: '#ffffff' },
        dark: { name: 'Dark', icon: 'bi-moon-stars-fill', color: '#1a1a1a' },
        blue: { name: 'Blue', icon: 'bi-droplet-fill', color: '#0066cc' },
        green: { name: 'Green', icon: 'bi-tree-fill', color: '#2e7d32' },
        'high-contrast': { name: 'High Contrast', icon: 'bi-circle-half', color: '#000000' },
        custom: { name: 'Custom', icon: 'bi-palette-fill', color: '#9c27b0' }
    };

    function getCurrentTheme() {
        return localStorage.getItem(STORAGE_KEY) || DEFAULT_THEME;
    }

    function getCustomColors() {
        const saved = localStorage.getItem(CUSTOM_COLORS_KEY);
        return saved ? JSON.parse(saved) : {
            bgColor: '#ffffff',
            textColor: '#212529',
            bgSecondary: '#f8f9fa',
            textSecondary: '#6c757d'
        };
    }

    function saveCustomColors(colors) {
        localStorage.setItem(CUSTOM_COLORS_KEY, JSON.stringify(colors));
    }

    function applyCustomColors(colors) {
        const root = document.documentElement;
        root.style.setProperty('--bg-color', colors.bgColor);
        root.style.setProperty('--text-color', colors.textColor);
        root.style.setProperty('--bg-secondary', colors.bgSecondary);
        root.style.setProperty('--text-secondary', colors.textSecondary);

        // Auto-adjust border color based on background
        const borderColor = adjustColorBrightness(colors.bgColor, -20);
        root.style.setProperty('--border-color', borderColor);

        // Auto-adjust card background
        const cardBg = adjustColorBrightness(colors.bgColor, -5);
        root.style.setProperty('--card-bg', cardBg);
    }

    function adjustColorBrightness(color, percent) {
        // Convert hex to RGB
        const num = parseInt(color.replace('#', ''), 16);
        const r = (num >> 16) + Math.round(2.55 * percent);
        const g = ((num >> 8) & 0x00FF) + Math.round(2.55 * percent);
        const b = (num & 0x0000FF) + Math.round(2.55 * percent);

        // Clamp values
        const clamp = (val) => Math.max(0, Math.min(255, val));

        return '#' + (0x1000000 + (clamp(r) << 16) + (clamp(g) << 8) + clamp(b))
            .toString(16).slice(1);
    }

    function setTheme(themeName) {
        if (!themes[themeName]) {
            themeName = DEFAULT_THEME;
        }
        document.documentElement.setAttribute('data-theme', themeName);
        localStorage.setItem(STORAGE_KEY, themeName);

        // If custom theme, apply custom colors
        if (themeName === 'custom') {
            applyCustomColors(getCustomColors());
        }

        updateToggleButton(themeName);
        updateCustomColorInputs();
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

    function updateCustomColorInputs() {
        const colors = getCustomColors();
        const inputs = {
            'custom-bg-color': colors.bgColor,
            'custom-text-color': colors.textColor,
            'custom-bg-secondary': colors.bgSecondary,
            'custom-text-secondary': colors.textSecondary
        };

        for (const [id, value] of Object.entries(inputs)) {
            const input = document.getElementById(id);
            if (input) input.value = value;
        }
    }

    function createThemeSwitcher() {
        const currentTheme = getCurrentTheme();
        const switcher = document.createElement('div');
        switcher.className = 'theme-switcher';

        let optionsHTML = '<h6 class="mb-3"><i class="bi bi-palette"></i> Theme Options</h6>';

        // Preset themes
        optionsHTML += '<div class="theme-presets mb-3">';
        for (const [key, config] of Object.entries(themes)) {
            if (key !== 'custom') {
                const checkmark = key === currentTheme ? '<i class="bi bi-check2 ms-auto"></i>' : '';
                optionsHTML += '<div class="theme-option" data-theme="' + key + '">' +
                    '<div class="theme-color-preview" style="background-color: ' + config.color + '"></div>' +
                    '<span>' + config.name + '</span>' + checkmark + '</div>';
            }
        }
        optionsHTML += '</div>';

        // Custom theme section
        optionsHTML += '<hr class="my-3">';
        optionsHTML += '<h6 class="mb-3"><i class="bi bi-sliders"></i> Custom Colors</h6>';
        optionsHTML += '<div class="custom-theme-controls">';

        optionsHTML += '<div class="color-control mb-2">' +
            '<label for="custom-bg-color" class="form-label small mb-1">Background Color</label>' +
            '<div class="input-group input-group-sm">' +
            '<input type="color" id="custom-bg-color" class="form-control form-control-color" value="' + getCustomColors().bgColor + '">' +
            '<input type="text" class="form-control color-hex-input" value="' + getCustomColors().bgColor + '" readonly>' +
            '</div></div>';

        optionsHTML += '<div class="color-control mb-2">' +
            '<label for="custom-text-color" class="form-label small mb-1">Text Color</label>' +
            '<div class="input-group input-group-sm">' +
            '<input type="color" id="custom-text-color" class="form-control form-control-color" value="' + getCustomColors().textColor + '">' +
            '<input type="text" class="form-control color-hex-input" value="' + getCustomColors().textColor + '" readonly>' +
            '</div></div>';

        optionsHTML += '<div class="color-control mb-2">' +
            '<label for="custom-bg-secondary" class="form-label small mb-1">Secondary Background</label>' +
            '<div class="input-group input-group-sm">' +
            '<input type="color" id="custom-bg-secondary" class="form-control form-control-color" value="' + getCustomColors().bgSecondary + '">' +
            '<input type="text" class="form-control color-hex-input" value="' + getCustomColors().bgSecondary + '" readonly>' +
            '</div></div>';

        optionsHTML += '<div class="color-control mb-3">' +
            '<label for="custom-text-secondary" class="form-label small mb-1">Secondary Text</label>' +
            '<div class="input-group input-group-sm">' +
            '<input type="color" id="custom-text-secondary" class="form-control form-control-color" value="' + getCustomColors().textSecondary + '">' +
            '<input type="text" class="form-control color-hex-input" value="' + getCustomColors().textSecondary + '" readonly>' +
            '</div></div>';

        optionsHTML += '<button id="apply-custom-theme-btn" class="btn btn-primary btn-sm w-100">' +
            '<i class="bi bi-check-circle"></i> Apply Custom Theme</button>';

        optionsHTML += '</div>';

        switcher.innerHTML = '<button id="theme-toggle-btn" class="theme-toggle-btn" title="Theme Options">' +
            '<i class="bi ' + themes[currentTheme].icon + '"></i></button>' +
            '<div id="theme-options" class="theme-options">' + optionsHTML + '</div>';

        document.body.appendChild(switcher);

        // Theme toggle button
        document.getElementById('theme-toggle-btn').addEventListener('click', function() {
            document.getElementById('theme-options').classList.toggle('show');
        });

        // Preset theme options
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', function() {
                setTheme(this.getAttribute('data-theme'));
                document.getElementById('theme-options').classList.remove('show');
            });
        });

        // Custom color inputs - update hex display
        document.querySelectorAll('input[type="color"]').forEach(input => {
            input.addEventListener('input', function() {
                const hexInput = this.nextElementSibling;
                if (hexInput) hexInput.value = this.value;
            });
        });

        // Apply custom theme button
        const applyBtn = document.getElementById('apply-custom-theme-btn');
        if (applyBtn) {
            applyBtn.addEventListener('click', function() {
                const colors = {
                    bgColor: document.getElementById('custom-bg-color').value,
                    textColor: document.getElementById('custom-text-color').value,
                    bgSecondary: document.getElementById('custom-bg-secondary').value,
                    textSecondary: document.getElementById('custom-text-secondary').value
                };
                saveCustomColors(colors);
                setTheme('custom');
                document.getElementById('theme-options').classList.remove('show');
            });
        }

        // Close on outside click
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

    window.ThemeSwitcher = { setTheme, getCurrentTheme, getCustomColors, applyCustomColors };
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
