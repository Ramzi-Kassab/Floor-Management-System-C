/**
 * Bit Design Hub - Professional Interactive Table
 * Enterprise-grade custom table controller with Excel-like features
 */

class BitDesignHubTable {
    constructor(tableId) {
        this.table = document.getElementById(tableId);
        if (!this.table) {
            console.error(`Table with ID '${tableId}' not found`);
            return;
        }

        this.tbody = this.table.querySelector('tbody');
        this.thead = this.table.querySelector('thead');

        // State management
        this.state = {
            expandedDesigns: new Set(),
            selectedRow: null,
            sortColumns: [], // Array of {column: index, direction: 'asc'|'desc'}
            filters: [], // Array of {column: index, condition: string, value: any}
            hiddenColumns: new Set(),
            columnOrder: [],
            preferences: {}
        };

        // Load saved preferences
        this.loadPreferences();

        // Initialize all features
        this.init();
    }

    /**
     * Initialize all table features
     */
    init() {
        console.log('Initializing Bit Design Hub Table...');

        // Phase 1 features
        this.initExpandCollapse();
        this.initCellHover();
        this.initSorting();
        this.initFiltering();
        this.initToolbar();

        // Phase 2 features
        this.initColumnManagement();
        this.initKeyboardNavigation();

        // Phase 3 features
        this.initAccessibility();

        console.log('Table initialized successfully');
    }

    /* ============================================
       EXPAND/COLLAPSE FUNCTIONALITY
       ============================================ */

    initExpandCollapse() {
        // Hide all level rows initially
        const levelRows = this.tbody.querySelectorAll('.level-row');
        levelRows.forEach(row => {
            row.style.display = 'none';
        });

        // Add click handler to design rows
        const designRows = this.tbody.querySelectorAll('.design-row');
        designRows.forEach(row => {
            row.addEventListener('click', (e) => {
                // Don't trigger if clicking a link or button
                if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || e.target.closest('a') || e.target.closest('button')) {
                    return;
                }
                this.toggleDesignRow(row);
            });
        });
    }

    toggleDesignRow(row) {
        const designId = row.getAttribute('data-design-id');
        if (!designId) return;

        const levelRows = this.tbody.querySelectorAll(`.level-row-${designId}`);
        const icon = row.querySelector('.toggle-icon');
        const isExpanded = this.state.expandedDesigns.has(designId);

        if (isExpanded) {
            // Collapse
            levelRows.forEach(levelRow => {
                this.slideUp(levelRow);
            });
            if (icon) {
                icon.classList.remove('expanded');
            }
            this.state.expandedDesigns.delete(designId);
        } else {
            // Expand
            levelRows.forEach(levelRow => {
                this.slideDown(levelRow);
            });
            if (icon) {
                icon.classList.add('expanded');
            }
            this.state.expandedDesigns.add(designId);
        }

        this.savePreferences();
    }

    expandAll() {
        const designRows = this.tbody.querySelectorAll('.design-row');
        designRows.forEach(row => {
            const designId = row.getAttribute('data-design-id');
            if (!this.state.expandedDesigns.has(designId)) {
                this.toggleDesignRow(row);
            }
        });
    }

    collapseAll() {
        const designRows = this.tbody.querySelectorAll('.design-row');
        designRows.forEach(row => {
            const designId = row.getAttribute('data-design-id');
            if (this.state.expandedDesigns.has(designId)) {
                this.toggleDesignRow(row);
            }
        });
    }

    // Smooth slide animations
    slideDown(element) {
        element.style.display = 'table-row';
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';

        setTimeout(() => {
            element.style.transition = 'opacity 300ms ease, transform 300ms ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 10);
    }

    slideUp(element) {
        element.style.transition = 'opacity 300ms ease, transform 300ms ease';
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';

        setTimeout(() => {
            element.style.display = 'none';
            element.style.transition = '';
        }, 300);
    }

    /* ============================================
       EXCEL-STYLE CELL HOVER
       ============================================ */

    initCellHover() {
        // Add cell-hoverable class to all data cells
        const cells = this.tbody.querySelectorAll('td');
        cells.forEach(cell => {
            // Don't add hover to level row cells with colspan
            if (!cell.hasAttribute('colspan')) {
                cell.classList.add('cell-hoverable');
            }
        });
    }

    /* ============================================
       MULTI-COLUMN SORTING
       ============================================ */

    initSorting() {
        const headers = this.thead.querySelectorAll('th');

        headers.forEach((header, index) => {
            // Skip the first column (toggle icon)
            if (index === 0) return;

            header.classList.add('sortable-header');
            header.setAttribute('data-column-index', index);

            // Add sort indicator
            const indicator = document.createElement('span');
            indicator.className = 'sort-indicator';
            header.appendChild(indicator);

            // Add click handler
            header.addEventListener('click', (e) => {
                // Check if Shift key is pressed for multi-column sort
                const isMultiSort = e.shiftKey;
                this.sortByColumn(index, isMultiSort);
            });
        });
    }

    sortByColumn(columnIndex, isMultiSort = false) {
        // Find if this column is already being sorted
        const existingSort = this.state.sortColumns.findIndex(s => s.column === columnIndex);

        if (!isMultiSort) {
            // Single column sort - clear all other sorts
            this.state.sortColumns = [];
        }

        if (existingSort !== -1) {
            // Column is already sorted - cycle through: asc -> desc -> none
            const currentDirection = this.state.sortColumns[existingSort].direction;

            if (currentDirection === 'asc') {
                this.state.sortColumns[existingSort].direction = 'desc';
            } else if (currentDirection === 'desc') {
                this.state.sortColumns.splice(existingSort, 1);
            }
        } else {
            // New sort column - add as ascending
            this.state.sortColumns.push({
                column: columnIndex,
                direction: 'asc'
            });
        }

        this.applySorting();
        this.updateSortIndicators();
        this.savePreferences();
    }

    applySorting() {
        if (this.state.sortColumns.length === 0) {
            return; // No sorting applied
        }

        const designRows = Array.from(this.tbody.querySelectorAll('.design-row'));

        designRows.sort((a, b) => {
            for (let sort of this.state.sortColumns) {
                const cellA = a.children[sort.column];
                const cellB = b.children[sort.column];

                if (!cellA || !cellB) continue;

                let valueA = this.getCellValue(cellA);
                let valueB = this.getCellValue(cellB);

                // Compare values
                let comparison = 0;
                if (typeof valueA === 'number' && typeof valueB === 'number') {
                    comparison = valueA - valueB;
                } else {
                    comparison = String(valueA).localeCompare(String(valueB));
                }

                if (comparison !== 0) {
                    return sort.direction === 'asc' ? comparison : -comparison;
                }
            }
            return 0;
        });

        // Reorder rows in DOM
        designRows.forEach(row => {
            const designId = row.getAttribute('data-design-id');
            this.tbody.appendChild(row);

            // Move associated level rows
            const levelRows = this.tbody.querySelectorAll(`.level-row-${designId}`);
            levelRows.forEach(levelRow => {
                this.tbody.appendChild(levelRow);
            });
        });
    }

    getCellValue(cell) {
        // Try to extract numeric value
        const text = cell.textContent.trim();

        // Check if it's a number
        const num = parseFloat(text.replace(/[^0-9.-]/g, ''));
        if (!isNaN(num)) {
            return num;
        }

        // Check if it's a date
        const date = new Date(text);
        if (!isNaN(date.getTime())) {
            return date.getTime();
        }

        return text;
    }

    updateSortIndicators() {
        // Clear all indicators
        const headers = this.thead.querySelectorAll('.sortable-header');
        headers.forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
            const priorityBadge = header.querySelector('.sort-priority');
            if (priorityBadge) {
                priorityBadge.remove();
            }
        });

        // Add indicators for sorted columns
        this.state.sortColumns.forEach((sort, index) => {
            const header = this.thead.querySelector(`[data-column-index="${sort.column}"]`);
            if (header) {
                header.classList.add(`sort-${sort.direction}`);

                // Add priority badge for multi-column sort
                if (this.state.sortColumns.length > 1) {
                    const badge = document.createElement('span');
                    badge.className = 'sort-priority';
                    badge.textContent = index + 1;
                    header.appendChild(badge);
                }
            }
        });
    }

    /* ============================================
       ADVANCED FILTERING
       ============================================ */

    initFiltering() {
        const headers = this.thead.querySelectorAll('th');

        headers.forEach((header, index) => {
            // Skip first column (toggle icon)
            if (index === 0) return;

            // Add filter icon
            const filterIcon = document.createElement('i');
            filterIcon.className = 'bi bi-funnel filter-icon';
            filterIcon.setAttribute('data-column-index', index);
            header.appendChild(filterIcon);

            // Create filter dropdown
            const dropdown = this.createFilterDropdown(index);
            header.style.position = 'relative';
            header.appendChild(dropdown);

            // Toggle dropdown on icon click
            filterIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFilterDropdown(dropdown);
            });
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.filter-dropdown')) {
                this.closeAllFilterDropdowns();
            }
        });
    }

    createFilterDropdown(columnIndex) {
        const dropdown = document.createElement('div');
        dropdown.className = 'filter-dropdown';
        dropdown.setAttribute('data-column-index', columnIndex);

        dropdown.innerHTML = `
            <div class="mb-2">
                <label class="form-label" style="font-size: 0.875rem; margin-bottom: 4px;">Condition</label>
                <select class="filter-condition-select">
                    <option value="contains">Contains</option>
                    <option value="equals">Equals</option>
                    <option value="starts_with">Starts With</option>
                    <option value="ends_with">Ends With</option>
                    <option value="not_equals">Not Equals</option>
                    <option value="greater_than">Greater Than</option>
                    <option value="less_than">Less Than</option>
                    <option value="between">Between</option>
                    <option value="is_empty">Is Empty</option>
                    <option value="is_not_empty">Is Not Empty</option>
                </select>
            </div>
            <div class="mb-2">
                <label class="form-label" style="font-size: 0.875rem; margin-bottom: 4px;">Value</label>
                <input type="text" class="filter-value-input" placeholder="Enter value...">
            </div>
            <div class="filter-buttons">
                <button class="filter-apply-btn">Apply</button>
                <button class="filter-clear-btn">Clear</button>
            </div>
        `;

        // Add event listeners
        const applyBtn = dropdown.querySelector('.filter-apply-btn');
        const clearBtn = dropdown.querySelector('.filter-clear-btn');

        applyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.applyFilter(columnIndex, dropdown);
        });

        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearFilter(columnIndex);
            this.closeFilterDropdown(dropdown);
        });

        return dropdown;
    }

    toggleFilterDropdown(dropdown) {
        const isVisible = dropdown.classList.contains('show');
        this.closeAllFilterDropdowns();
        if (!isVisible) {
            dropdown.classList.add('show');
        }
    }

    closeFilterDropdown(dropdown) {
        dropdown.classList.remove('show');
    }

    closeAllFilterDropdowns() {
        const dropdowns = this.table.querySelectorAll('.filter-dropdown');
        dropdowns.forEach(d => d.classList.remove('show'));
    }

    applyFilter(columnIndex, dropdown) {
        const condition = dropdown.querySelector('.filter-condition-select').value;
        const value = dropdown.querySelector('.filter-value-input').value;

        // Remove existing filter for this column
        this.state.filters = this.state.filters.filter(f => f.column !== columnIndex);

        // Add new filter if value is provided
        if (value || condition === 'is_empty' || condition === 'is_not_empty') {
            this.state.filters.push({
                column: columnIndex,
                condition: condition,
                value: value
            });

            // Mark filter icon as active
            const icon = this.thead.querySelector(`[data-column-index="${columnIndex}"].filter-icon`);
            if (icon) {
                icon.classList.add('active');
            }
        }

        this.applyFiltering();
        this.updateFilterChips();
        this.closeFilterDropdown(dropdown);
        this.savePreferences();
    }

    clearFilter(columnIndex) {
        this.state.filters = this.state.filters.filter(f => f.column !== columnIndex);

        // Remove active state from filter icon
        const icon = this.thead.querySelector(`[data-column-index="${columnIndex}"].filter-icon`);
        if (icon) {
            icon.classList.remove('active');
        }

        this.applyFiltering();
        this.updateFilterChips();
        this.savePreferences();
    }

    clearAllFilters() {
        this.state.filters = [];

        // Remove active state from all filter icons
        const icons = this.thead.querySelectorAll('.filter-icon');
        icons.forEach(icon => icon.classList.remove('active'));

        this.applyFiltering();
        this.updateFilterChips();
        this.savePreferences();
    }

    applyFiltering() {
        const designRows = this.tbody.querySelectorAll('.design-row');

        designRows.forEach(row => {
            let visible = true;

            // Apply all filters (AND logic)
            for (let filter of this.state.filters) {
                const cell = row.children[filter.column];
                if (!cell) continue;

                const cellValue = this.getCellValue(cell);
                const filterValue = filter.value;

                let matches = false;

                switch (filter.condition) {
                    case 'contains':
                        matches = String(cellValue).toLowerCase().includes(String(filterValue).toLowerCase());
                        break;
                    case 'equals':
                        matches = String(cellValue).toLowerCase() === String(filterValue).toLowerCase();
                        break;
                    case 'starts_with':
                        matches = String(cellValue).toLowerCase().startsWith(String(filterValue).toLowerCase());
                        break;
                    case 'ends_with':
                        matches = String(cellValue).toLowerCase().endsWith(String(filterValue).toLowerCase());
                        break;
                    case 'not_equals':
                        matches = String(cellValue).toLowerCase() !== String(filterValue).toLowerCase();
                        break;
                    case 'greater_than':
                        matches = parseFloat(cellValue) > parseFloat(filterValue);
                        break;
                    case 'less_than':
                        matches = parseFloat(cellValue) < parseFloat(filterValue);
                        break;
                    case 'is_empty':
                        matches = !cellValue || String(cellValue).trim() === '' || cellValue === '—';
                        break;
                    case 'is_not_empty':
                        matches = cellValue && String(cellValue).trim() !== '' && cellValue !== '—';
                        break;
                    default:
                        matches = true;
                }

                if (!matches) {
                    visible = false;
                    break;
                }
            }

            // Show/hide row and its level rows
            if (visible) {
                row.style.display = 'table-row';
                const designId = row.getAttribute('data-design-id');
                const levelRows = this.tbody.querySelectorAll(`.level-row-${designId}`);
                levelRows.forEach(levelRow => {
                    if (this.state.expandedDesigns.has(designId)) {
                        levelRow.style.display = 'table-row';
                    }
                });
            } else {
                row.style.display = 'none';
                const designId = row.getAttribute('data-design-id');
                const levelRows = this.tbody.querySelectorAll(`.level-row-${designId}`);
                levelRows.forEach(levelRow => {
                    levelRow.style.display = 'none';
                });
            }
        });
    }

    updateFilterChips() {
        const container = document.querySelector('.active-filters-container');
        if (!container) return;

        const chipsContainer = container.querySelector('.filter-chips');
        if (!chipsContainer) return;

        chipsContainer.innerHTML = '';

        if (this.state.filters.length === 0) {
            container.classList.remove('has-filters');
            return;
        }

        container.classList.add('has-filters');

        this.state.filters.forEach(filter => {
            const header = this.thead.querySelectorAll('th')[filter.column];
            const columnName = header ? header.textContent.replace('▲', '').replace('▼', '').trim() : `Column ${filter.column}`;

            const chip = document.createElement('span');
            chip.className = 'filter-chip';
            chip.innerHTML = `
                ${columnName}: ${filter.condition} "${filter.value}"
                <span class="filter-chip-remove" data-column="${filter.column}">×</span>
            `;

            const removeBtn = chip.querySelector('.filter-chip-remove');
            removeBtn.addEventListener('click', () => {
                this.clearFilter(filter.column);
            });

            chipsContainer.appendChild(chip);
        });
    }

    /* ============================================
       TOOLBAR & CONTROLS
       ============================================ */

    initToolbar() {
        // Create toolbar if it doesn't exist
        let toolbar = document.querySelector('.table-controls-toolbar');
        if (!toolbar) {
            toolbar = this.createToolbar();
            const cardBody = this.table.closest('.card-body');
            if (cardBody) {
                cardBody.insertBefore(toolbar, cardBody.firstChild);
            }
        }

        // Create active filters container
        let filtersContainer = document.querySelector('.active-filters-container');
        if (!filtersContainer) {
            filtersContainer = document.createElement('div');
            filtersContainer.className = 'active-filters-container';
            filtersContainer.innerHTML = `
                <div class="filter-chips"></div>
                <button class="clear-all-filters-btn">Clear All Filters</button>
            `;
            const cardBody = this.table.closest('.card-body');
            if (cardBody) {
                cardBody.insertBefore(filtersContainer, toolbar.nextSibling);
            }

            const clearAllBtn = filtersContainer.querySelector('.clear-all-filters-btn');
            clearAllBtn.addEventListener('click', () => this.clearAllFilters());
        }

        // Add event listeners to toolbar buttons
        this.attachToolbarListeners();
    }

    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'table-controls-toolbar';
        toolbar.innerHTML = `
            <div class="table-controls-left">
                <button class="toolbar-btn expand-all-btn">
                    <i class="bi bi-arrows-expand"></i> Expand All
                </button>
                <button class="toolbar-btn collapse-all-btn">
                    <i class="bi bi-arrows-collapse"></i> Collapse All
                </button>
            </div>
            <div class="table-controls-right">
                <button class="toolbar-btn export-csv-btn">
                    <i class="bi bi-file-earmark-spreadsheet"></i> CSV
                </button>
                <button class="toolbar-btn export-excel-btn">
                    <i class="bi bi-file-earmark-excel"></i> Excel
                </button>
                <button class="toolbar-btn export-pdf-btn">
                    <i class="bi bi-file-earmark-pdf"></i> PDF
                </button>
                <div class="column-visibility-dropdown">
                    <button class="toolbar-btn column-visibility-btn">
                        <i class="bi bi-eye"></i> Columns
                    </button>
                    <div class="column-visibility-menu">
                        <!-- Will be populated dynamically -->
                    </div>
                </div>
            </div>
        `;
        return toolbar;
    }

    attachToolbarListeners() {
        const expandAllBtn = document.querySelector('.expand-all-btn');
        const collapseAllBtn = document.querySelector('.collapse-all-btn');
        const exportCsvBtn = document.querySelector('.export-csv-btn');
        const exportExcelBtn = document.querySelector('.export-excel-btn');
        const exportPdfBtn = document.querySelector('.export-pdf-btn');
        const columnVisibilityBtn = document.querySelector('.column-visibility-btn');

        if (expandAllBtn) {
            expandAllBtn.addEventListener('click', () => this.expandAll());
        }

        if (collapseAllBtn) {
            collapseAllBtn.addEventListener('click', () => this.collapseAll());
        }

        if (exportCsvBtn) {
            exportCsvBtn.addEventListener('click', () => this.exportToCSV());
        }

        if (exportExcelBtn) {
            exportExcelBtn.addEventListener('click', () => this.exportToExcel());
        }

        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', () => this.exportToPDF());
        }

        if (columnVisibilityBtn) {
            columnVisibilityBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleColumnVisibilityMenu();
            });
        }

        // Close column visibility menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.column-visibility-dropdown')) {
                this.closeColumnVisibilityMenu();
            }
        });
    }

    /* ============================================
       COLUMN MANAGEMENT
       ============================================ */

    initColumnManagement() {
        this.populateColumnVisibilityMenu();
    }

    populateColumnVisibilityMenu() {
        const menu = document.querySelector('.column-visibility-menu');
        if (!menu) return;

        const headers = this.thead.querySelectorAll('th');
        menu.innerHTML = '';

        headers.forEach((header, index) => {
            // Skip first column (toggle icon) - always visible
            if (index === 0) return;

            const columnName = header.textContent.replace('▲', '').replace('▼', '').trim();

            const item = document.createElement('div');
            item.className = 'column-visibility-item';
            item.innerHTML = `
                <input type="checkbox" id="col-vis-${index}" ${!this.state.hiddenColumns.has(index) ? 'checked' : ''}>
                <label for="col-vis-${index}">${columnName}</label>
            `;

            const checkbox = item.querySelector('input');
            checkbox.addEventListener('change', () => {
                this.toggleColumnVisibility(index, checkbox.checked);
            });

            menu.appendChild(item);
        });
    }

    toggleColumnVisibilityMenu() {
        const menu = document.querySelector('.column-visibility-menu');
        if (menu) {
            menu.classList.toggle('show');
        }
    }

    closeColumnVisibilityMenu() {
        const menu = document.querySelector('.column-visibility-menu');
        if (menu) {
            menu.classList.remove('show');
        }
    }

    toggleColumnVisibility(columnIndex, visible) {
        if (visible) {
            this.state.hiddenColumns.delete(columnIndex);
        } else {
            this.state.hiddenColumns.add(columnIndex);
        }

        // Update column display
        const headers = this.thead.querySelectorAll('th');
        if (headers[columnIndex]) {
            headers[columnIndex].style.display = visible ? '' : 'none';
        }

        const rows = this.tbody.querySelectorAll('tr');
        rows.forEach(row => {
            if (row.children[columnIndex]) {
                row.children[columnIndex].style.display = visible ? '' : 'none';
            }
        });

        this.savePreferences();
    }

    /* ============================================
       DATA EXPORT
       ============================================ */

    exportToCSV() {
        const rows = this.getVisibleRows();
        const csvContent = this.convertToCSV(rows);

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `bit-design-hub-${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
    }

    exportToExcel() {
        alert('Excel export requires additional library (e.g., SheetJS). This is a placeholder.');
        // In production, use a library like SheetJS (xlsx) for proper Excel export
    }

    exportToPDF() {
        alert('PDF export requires additional library (e.g., jsPDF). This is a placeholder.');
        // In production, use a library like jsPDF for proper PDF export
    }

    getVisibleRows() {
        const visibleRows = [];
        const designRows = Array.from(this.tbody.querySelectorAll('.design-row'));

        designRows.forEach(row => {
            if (row.style.display !== 'none') {
                const rowData = [];
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, index) => {
                    if (!this.state.hiddenColumns.has(index)) {
                        rowData.push(cell.textContent.trim());
                    }
                });
                visibleRows.push(rowData);
            }
        });

        return visibleRows;
    }

    convertToCSV(rows) {
        // Get headers
        const headers = [];
        const headerCells = this.thead.querySelectorAll('th');
        headerCells.forEach((cell, index) => {
            if (!this.state.hiddenColumns.has(index)) {
                headers.push(cell.textContent.replace('▲', '').replace('▼', '').trim());
            }
        });

        // Build CSV
        let csv = headers.map(h => `"${h}"`).join(',') + '\n';

        rows.forEach(row => {
            csv += row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',') + '\n';
        });

        return csv;
    }

    /* ============================================
       KEYBOARD NAVIGATION
       ============================================ */

    initKeyboardNavigation() {
        const designRows = Array.from(this.tbody.querySelectorAll('.design-row'));
        let currentRowIndex = -1;

        this.table.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    currentRowIndex = Math.min(currentRowIndex + 1, designRows.length - 1);
                    this.focusRow(designRows[currentRowIndex]);
                    break;

                case 'ArrowUp':
                    e.preventDefault();
                    currentRowIndex = Math.max(currentRowIndex - 1, 0);
                    this.focusRow(designRows[currentRowIndex]);
                    break;

                case 'Enter':
                case ' ':
                    e.preventDefault();
                    if (currentRowIndex >= 0 && currentRowIndex < designRows.length) {
                        this.toggleDesignRow(designRows[currentRowIndex]);
                    }
                    break;

                case 'Escape':
                    this.closeAllFilterDropdowns();
                    this.closeColumnVisibilityMenu();
                    break;
            }
        });

        // Make rows focusable
        designRows.forEach((row, index) => {
            row.setAttribute('tabindex', '0');
            row.addEventListener('focus', () => {
                currentRowIndex = index;
            });
        });
    }

    focusRow(row) {
        if (row) {
            row.focus();
            row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    /* ============================================
       ACCESSIBILITY
       ============================================ */

    initAccessibility() {
        // Add ARIA labels to headers
        const headers = this.thead.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.setAttribute('role', 'columnheader');
            header.setAttribute('scope', 'col');
        });

        // Add ARIA labels to design rows
        const designRows = this.tbody.querySelectorAll('.design-row');
        designRows.forEach(row => {
            row.setAttribute('role', 'row');
            row.setAttribute('aria-label', 'Design row - click to expand/collapse');
        });

        // Add ARIA labels to toolbar buttons
        const expandAllBtn = document.querySelector('.expand-all-btn');
        const collapseAllBtn = document.querySelector('.collapse-all-btn');

        if (expandAllBtn) {
            expandAllBtn.setAttribute('aria-label', 'Expand all design rows');
        }

        if (collapseAllBtn) {
            collapseAllBtn.setAttribute('aria-label', 'Collapse all design rows');
        }
    }

    /* ============================================
       PREFERENCES & PERSISTENCE
       ============================================ */

    savePreferences() {
        const preferences = {
            expandedDesigns: Array.from(this.state.expandedDesigns),
            sortColumns: this.state.sortColumns,
            filters: this.state.filters,
            hiddenColumns: Array.from(this.state.hiddenColumns)
        };

        try {
            localStorage.setItem('bitdesign-hub-preferences', JSON.stringify(preferences));
        } catch (e) {
            console.warn('Failed to save preferences to localStorage:', e);
        }
    }

    loadPreferences() {
        try {
            const saved = localStorage.getItem('bitdesign-hub-preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                this.state.expandedDesigns = new Set(preferences.expandedDesigns || []);
                this.state.sortColumns = preferences.sortColumns || [];
                this.state.filters = preferences.filters || [];
                this.state.hiddenColumns = new Set(preferences.hiddenColumns || []);
            }
        } catch (e) {
            console.warn('Failed to load preferences from localStorage:', e);
        }
    }

    /* ============================================
       UTILITY METHODS
       ============================================ */

    refresh() {
        // Reapply all state after data refresh
        this.applySorting();
        this.applyFiltering();
        this.updateSortIndicators();
        this.updateFilterChips();
    }

    destroy() {
        // Clean up event listeners and state
        this.state = null;
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('bitdesign-hub-table');
    if (table) {
        window.hubTableController = new BitDesignHubTable('bitdesign-hub-table');
    }
});
