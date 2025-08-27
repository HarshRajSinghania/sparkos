/**
 * Wallet Module - Handles all wallet-related functionality
 */

class Wallet {
    constructor() {
        this.initializeEventListeners();
        this.initializeCharts();
    }

    /**
     * Initialize event listeners for wallet interactions
     */
    initializeEventListeners() {
        // Transaction form submission
        const transactionForm = document.getElementById('transaction-form');
        if (transactionForm) {
            transactionForm.addEventListener('submit', this.handleTransactionSubmit.bind(this));
        }

        // Transaction type toggle
        const transactionTypeToggles = document.querySelectorAll('.transaction-type-toggle');
        transactionTypeToggles.forEach(toggle => {
            toggle.addEventListener('click', this.handleTransactionTypeToggle.bind(this));
        });

        // Date pickers
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            if (!input.value) {
                const today = new Date().toISOString().split('T')[0];
                input.value = today;
            }
        });

        // Amount formatting
        const amountInputs = document.querySelectorAll('input[data-type="amount"]');
        amountInputs.forEach(input => {
            input.addEventListener('blur', this.formatCurrencyInput.bind(this));
        });

        // Category selection
        const categorySelects = document.querySelectorAll('select[name="category"]');
        categorySelects.forEach(select => {
            select.addEventListener('change', this.handleCategoryChange.bind(this));
        });
    }

    /**
     * Handle transaction form submission
     */
    async handleTransactionSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        
        try {
            // Disable submit button
            submitButton.disabled = true;
            submitButton.innerHTML = 'Processing...';
            
            // Convert form data to JSON
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            // Determine the API endpoint
            const isEdit = form.dataset.edit === 'true';
            const url = isEdit 
                ? `/api/transactions/${form.dataset.transactionId}` 
                : '/api/transactions';
            const method = isEdit ? 'PUT' : 'POST';
            
            // Make the API request
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error('Failed to save transaction');
            }
            
            const result = await response.json();
            
            // Show success message
            window.SparkOS.showToast(
                isEdit ? 'Transaction updated successfully' : 'Transaction added successfully',
                'success'
            );
            
            // Redirect or reset form
            if (isEdit) {
                // If editing, redirect back to transactions list
                setTimeout(() => {
                    window.location.href = '/wallet/transactions';
                }, 1000);
            } else {
                // If adding new, reset form
                form.reset();
                // Update any dynamic UI elements
                this.updateTransactionList(result);
            }
            
        } catch (error) {
            console.error('Error saving transaction:', error);
            window.SparkOS.showToast(
                error.message || 'An error occurred while saving the transaction',
                'error'
            );
        } finally {
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    }

    /**
     * Handle transaction type toggle
     */
    handleTransactionTypeToggle(e) {
        const type = e.currentTarget.dataset.type;
        const form = e.currentTarget.closest('form');
        const amountInput = form.querySelector('input[name="amount"]');
        const categorySelect = form.querySelector('select[name="category"]');
        
        // Update active state of toggle buttons
        document.querySelectorAll('.transaction-type-toggle').forEach(btn => {
            btn.classList.remove('bg-indigo-600', 'text-white');
            btn.classList.add('bg-gray-200', 'text-gray-700');
        });
        
        e.currentTarget.classList.remove('bg-gray-200', 'text-gray-700');
        e.currentTarget.classList.add('bg-indigo-600', 'text-white');
        
        // Update hidden input value
        const typeInput = form.querySelector('input[name="transaction_type"]');
        if (typeInput) {
            typeInput.value = type;
        }
        
        // Update categories based on transaction type
        this.updateCategories(categorySelect, type);
    }

    /**
     * Update category options based on transaction type
     */
    updateCategories(selectElement, type) {
        if (!selectElement) return;
        
        const incomeCategories = [
            { value: 'salary', label: 'Salary' },
            { value: 'freelance', label: 'Freelance' },
            { value: 'investment', label: 'Investment' },
            { value: 'gift', label: 'Gift' },
            { value: 'other_income', label: 'Other Income' }
        ];
        
        const expenseCategories = [
            { value: 'food', label: 'Food & Dining' },
            { value: 'shopping', label: 'Shopping' },
            { value: 'transportation', label: 'Transportation' },
            { value: 'bills', label: 'Bills & Utilities' },
            { value: 'entertainment', label: 'Entertainment' },
            { value: 'health', label: 'Health & Medical' },
            { value: 'education', label: 'Education' },
            { value: 'gifts', label: 'Gifts & Donations' },
            { value: 'personal', label: 'Personal Care' },
            { value: 'travel', label: 'Travel' },
            { value: 'groceries', label: 'Groceries' },
            { value: 'subscriptions', label: 'Subscriptions' },
            { value: 'other', label: 'Other' }
        ];
        
        const categories = type === 'income' ? incomeCategories : expenseCategories;
        const currentValue = selectElement.value;
        
        // Clear existing options
        selectElement.innerHTML = '';
        
        // Add new options
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.value;
            option.textContent = category.label;
            selectElement.appendChild(option);
        });
        
        // Try to maintain the current selection if it exists in the new categories
        if (currentValue && categories.some(cat => cat.value === currentValue)) {
            selectElement.value = currentValue;
        }
    }

    /**
     * Format currency input
     */
    formatCurrencyInput(e) {
        const input = e.target || e;
        let value = input.value.replace(/[^\d.]/g, '');
        
        // Ensure only two decimal places
        const decimalSplit = value.split('.');
        if (decimalSplit.length > 1) {
            decimalSplit[1] = decimalSplit[1].substring(0, 2);
            value = decimalSplit.join('.');
        }
        
        // Format as currency
        if (value) {
            const num = parseFloat(value);
            if (!isNaN(num)) {
                input.value = num.toFixed(2);
            }
        }
    }

    /**
     * Handle category change
     */
    handleCategoryChange(e) {
        // Add any category-specific logic here
        const select = e.target;
        const selectedOption = select.options[select.selectedIndex];
        
        // Example: Show/hide additional fields based on category
        if (selectedOption.value === 'other') {
            // Show custom category input
            const customCategoryContainer = document.getElementById('custom-category-container');
            if (customCategoryContainer) {
                customCategoryContainer.classList.remove('hidden');
            }
        } else {
            // Hide custom category input
            const customCategoryContainer = document.getElementById('custom-category-container');
            if (customCategoryContainer) {
                customCategoryContainer.classList.add('hidden');
            }
        }
    }

    /**
     * Initialize charts for the wallet dashboard
     */
    initializeCharts() {
        // Check if we're on the dashboard and Chart.js is available
        if (typeof Chart === 'undefined' || !document.getElementById('spending-chart')) {
            return;
        }
        
        // Get chart data from data attributes
        const chartElement = document.getElementById('spending-chart');
        const chartData = JSON.parse(chartElement.dataset.chartData || '{}');
        
        // Create the chart
        const ctx = chartElement.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels || [],
                datasets: [{
                    data: chartData.data || [],
                    backgroundColor: [
                        '#3B82F6',
                        '#10B981',
                        '#F59E0B',
                        '#8B5CF6',
                        '#6B7280',
                        '#EC4899',
                        '#14B8A6',
                        '#F97316',
                        '#8B5CF6',
                        '#EC4899',
                        '#10B981',
                        '#3B82F6',
                        '#F59E0B'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                family: 'Inter',
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1F2937',
                        titleFont: {
                            family: 'Inter',
                            size: 12,
                            weight: '600'
                        },
                        bodyFont: {
                            family: 'Inter',
                            size: 12
                        },
                        padding: 12,
                        cornerRadius: 6,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${percentage}% (${value.toFixed(2)})`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Update transaction list after adding a new transaction
     */
    updateTransactionList(transaction) {
        const transactionList = document.getElementById('transactions-list');
        if (!transactionList) return;
        
        // Create a new transaction element
        const transactionElement = document.createElement('div');
        transactionElement.className = 'transaction-item';
        transactionElement.innerHTML = `
            <div class="flex items-center">
                <div class="p-2 rounded-full ${transaction.type === 'income' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}">
                    <i class="fas ${transaction.type === 'income' ? 'fa-arrow-down' : 'fa-arrow-up'}"></i>
                </div>
                <div class="ml-3">
                    <div class="font-medium">${transaction.description}</div>
                    <div class="text-sm text-gray-500">${transaction.category}</div>
                </div>
            </div>
            <div class="text-right">
                <div class="font-medium ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                    ${transaction.type === 'income' ? '+' : '-'}${parseFloat(transaction.amount).toFixed(2)}
                </div>
                <div class="text-sm text-gray-500">${new Date(transaction.date).toLocaleDateString()}</div>
            </div>
        `;
        
        // Add click event to view transaction details
        transactionElement.addEventListener('click', () => {
            window.location.href = `/wallet/transactions/${transaction.id}`;
        });
        
        // Add the new transaction to the top of the list
        if (transactionList.firstChild) {
            transactionList.insertBefore(transactionElement, transactionList.firstChild);
        } else {
            transactionList.appendChild(transactionElement);
        }
        
        // Update the summary
        this.updateSummary(transaction);
    }

    /**
     * Update the summary section with new transaction data
     */
    updateSummary(transaction) {
        // Update balance
        const balanceElement = document.getElementById('balance-amount');
        if (balanceElement) {
            const currentBalance = parseFloat(balanceElement.textContent.replace(/[^\d.-]/g, '')) || 0;
            const transactionAmount = parseFloat(transaction.amount) || 0;
            const newBalance = transaction.type === 'income' 
                ? currentBalance + transactionAmount 
                : currentBalance - transactionAmount;
            
            balanceElement.textContent = newBalance.toFixed(2);
            
            // Add animation class
            balanceElement.classList.add('text-green-500', 'scale-110');
            setTimeout(() => {
                balanceElement.classList.remove('text-green-500', 'scale-110');
            }, 1000);
        }
        
        // Update income/expense totals
        if (transaction.type === 'income') {
            const incomeElement = document.getElementById('income-amount');
            if (incomeElement) {
                const currentIncome = parseFloat(incomeElement.textContent.replace(/[^\d.-]/g, '')) || 0;
                incomeElement.textContent = (currentIncome + (parseFloat(transaction.amount) || 0)).toFixed(2);
            }
        } else {
            const expenseElement = document.getElementById('expense-amount');
            if (expenseElement) {
                const currentExpense = parseFloat(expenseElement.textContent.replace(/[^\d.-]/g, '')) || 0;
                expenseElement.textContent = (currentExpense + (parseFloat(transaction.amount) || 0)).toFixed(2);
            }
        }
    }

    /**
     * Get CSRF token from cookies
     */
    getCSRFToken() {
        const name = 'csrftoken=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(';');
        
        for (let i = 0; i < cookieArray.length; i++) {
            let cookie = cookieArray[i];
            while (cookie.charAt(0) === ' ') {
                cookie = cookie.substring(1);
            }
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length, cookie.length);
            }
        }
        return '';
    }
}

// Initialize the wallet when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on a wallet page
    if (document.querySelector('[data-wallet-module]')) {
        window.wallet = new Wallet();
    }
});
