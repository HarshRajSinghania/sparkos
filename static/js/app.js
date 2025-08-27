/**
 * SparkOS - Main Application JavaScript
 * Handles core functionality, UI interactions, and API communications
 */

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize modals
    initModals();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize date pickers
    initDatePickers();
    
    // Initialize charts if on dashboard
    if (document.querySelector('.dashboard-chart')) {
        initDashboardCharts();
    }
    
    // Initialize transaction filters if on transactions page
    if (document.getElementById('transactions-table')) {
        initTransactionFilters();
    }
    
    // Initialize savings goal progress bars
    initProgressBars();
    
    // Initialize mobile menu toggle
    initMobileMenu();
});

/**
 * Initialize all tooltips using Tippy.js
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        tippy(el, {
            content: el.getAttribute('data-tooltip'),
            placement: 'top',
            animation: 'shift-away',
            theme: 'light-border',
            delay: [100, 0],
            duration: [200, 150],
            arrow: true
        });
    });
}

/**
 * Initialize modals
 */
function initModals() {
    // Open modal handler
    document.querySelectorAll('[data-modal-toggle]').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-toggle');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
                document.body.classList.add('overflow-hidden');
                
                // Focus first input if exists
                const input = modal.querySelector('input, select, textarea');
                if (input) {
                    setTimeout(() => input.focus(), 100);
                }
            }
        });
    });

    // Close modal handlers
    document.querySelectorAll('[data-modal-hide]').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.add('hidden');
                document.body.classList.remove('overflow-hidden');
            }
        });
    });

    // Close modal when clicking outside content
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.add('hidden');
                document.body.classList.remove('overflow-hidden');
            }
        });
    });
}

/**
 * Initialize form validations
 */
function initFormValidations() {
    // Add custom validation for password strength
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            validatePasswordStrength(this);
        });
    });
    
    // Add custom validation for amount fields
    const amountInputs = document.querySelectorAll('input[data-type="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatCurrencyInput(this);
        });
    });
}

/**
 * Validate password strength and update UI
 */
function validatePasswordStrength(input) {
    const value = input.value;
    const strengthMeter = input.parentElement.querySelector('.password-strength');
    
    if (!strengthMeter) return;
    
    // Reset classes
    strengthMeter.className = 'password-strength mt-1 h-1 rounded-full';
    
    // Check password strength
    let strength = 0;
    let feedback = '';
    
    // Length check
    if (value.length >= 8) strength += 1;
    
    // Contains lowercase
    if (/[a-z]/.test(value)) strength += 1;
    
    // Contains uppercase
    if (/[A-Z]/.test(value)) strength += 1;
    
    // Contains number
    if (/[0-9]/.test(value)) strength += 1;
    
    // Contains special char
    if (/[^A-Za-z0-9]/.test(value)) strength += 1;
    
    // Update UI based on strength
    switch(strength) {
        case 0:
        case 1:
            strengthMeter.classList.add('bg-red-500');
            feedback = 'Very weak';
            break;
        case 2:
            strengthMeter.classList.add('bg-orange-500');
            feedback = 'Weak';
            break;
        case 3:
            strengthMeter.classList.add('bg-yellow-500');
            feedback = 'Moderate';
            break;
        case 4:
            strengthMeter.classList.add('bg-blue-500');
            feedback = 'Strong';
            break;
        case 5:
            strengthMeter.classList.add('bg-green-500');
            feedback = 'Very strong';
            break;
    }
    
    // Update feedback text if element exists
    const feedbackEl = input.parentElement.querySelector('.password-feedback');
    if (feedbackEl) {
        feedbackEl.textContent = feedback;
    }
}

/**
 * Format currency input
 */
function formatCurrencyInput(input) {
    // Remove all non-digit and non-decimal point characters
    let value = input.value.replace(/[^\d.]/g, '');
    
    // Ensure only one decimal point
    const decimalSplit = value.split('.');
    if (decimalSplit.length > 2) {
        value = decimalSplit[0] + '.' + decimalSplit.slice(1).join('');
    }
    
    // Format as currency
    if (value) {
        // Format with 2 decimal places
        const num = parseFloat(value);
        if (!isNaN(num)) {
            input.value = num.toFixed(2);
        }
    }
}

/**
 * Initialize date pickers
 */
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set min/max dates if not already set
        if (!input.min) {
            input.min = '2000-01-01';
        }
        if (!input.max) {
            const today = new Date();
            const year = today.getFullYear() + 10;
            input.max = `${year}-12-31`;
        }
    });
}

/**
 * Initialize dashboard charts
 */
function initDashboardCharts() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Skipping chart initialization.');
        return;
    }
    
    // Sample chart data - this would be replaced with actual data from the API
    const ctx = document.getElementById('spending-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Food', 'Shopping', 'Bills', 'Entertainment', 'Other'],
            datasets: [{
                data: [300, 200, 150, 100, 50],
                backgroundColor: [
                    '#3B82F6',
                    '#10B981',
                    '#F59E0B',
                    '#8B5CF6',
                    '#6B7280'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            }
        }
    });
    
    // Add more chart initializations as needed
}

/**
 * Initialize transaction filters
 */
function initTransactionFilters() {
    const filterForm = document.getElementById('transaction-filters');
    if (!filterForm) return;
    
    // Reset filters
    const resetBtn = filterForm.querySelector('[type="reset"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // Submit the form to reset all filters
            filterForm.submit();
        });
    }
    
    // Submit form on filter change
    const filterInputs = filterForm.querySelectorAll('select, input:not([type="reset"])');
    filterInputs.forEach(input => {
        input.addEventListener('change', function() {
            filterForm.submit();
        });
    });
}

/**
 * Initialize progress bars animation
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const value = bar.getAttribute('data-value');
        const progress = bar.querySelector('.progress-bar-fill');
        if (progress) {
            // Animate progress bar
            setTimeout(() => {
                progress.style.width = `${value}%`;
            }, 100);
        }
    });
}

/**
 * Initialize mobile menu
 */
function initMobileMenu() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !isExpanded);
            mobileMenu.classList.toggle('hidden');
        });
    }
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (default: 5000)
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} flex items-center justify-between p-4 mb-2 rounded-lg shadow-lg`;
    
    const messageEl = document.createElement('div');
    messageEl.className = 'flex-1';
    messageEl.textContent = message;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'ml-4 text-xl';
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
    
    toast.appendChild(messageEl);
    toast.appendChild(closeBtn);
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

/**
 * Make an AJAX request
 * @param {string} url - The URL to make the request to
 * @param {string} method - The HTTP method (GET, POST, PUT, DELETE)
 * @param {Object} data - The data to send with the request
 * @param {Object} options - Additional options (headers, etc.)
 * @returns {Promise} A promise that resolves with the response
 */
function ajaxRequest(url, method = 'GET', data = null, options = {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        // Set up the request
        xhr.open(method, url, true);
        
        // Set headers
        xhr.setRequestHeader('Content-Type', 'application/json');
        if (options.headers) {
            Object.entries(options.headers).forEach(([key, value]) => {
                xhr.setRequestHeader(key, value);
            });
        }
        
        // Set up the response handler
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = xhr.responseText ? JSON.parse(xhr.responseText) : null;
                    resolve(response);
                } catch (e) {
                    reject(new Error('Invalid JSON response'));
                }
            } else {
                reject(new Error(`Request failed with status ${xhr.status}`));
            }
        };
        
        // Handle network errors
        xhr.onerror = function() {
            reject(new Error('Network error'));
        };
        
        // Send the request
        xhr.send(data ? JSON.stringify(data) : null);
    });
}

// Make functions available globally
window.SparkOS = {
    showToast,
    ajaxRequest,
    // Add other utility functions here
};
