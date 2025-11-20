// Order state
let orderItems = [];

function addToOrderFromElement(el) {
    const itemId = Number(el.getAttribute('data-item-id'));
    const itemName = el.getAttribute('data-item-name');
    const itemPrice = Number(el.getAttribute('data-item-price')) || 0;
    addToOrder(itemId, itemName, itemPrice);
    
    // Visual feedback
    el.classList.add('selected');
    setTimeout(() => {
        if (!orderItems.find(item => item.item_id === itemId)) {
            el.classList.remove('selected');
        }
    }, 300);
}

function addToOrder(itemId, itemName, itemPrice) {
    const existingItem = orderItems.find(item => item.item_id === itemId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        orderItems.push({
            item_id: itemId,
            name: itemName,
            price: itemPrice,
            quantity: 1
        });
    }
    
    updateOrderDisplay();
}

function removeFromOrder(itemId) {
    orderItems = orderItems.filter(item => item.item_id !== itemId);
    
    // Remove visual selection from menu item
    const menuCard = document.querySelector(`[data-item-id="${itemId}"]`);
    if (menuCard) {
        menuCard.classList.remove('selected');
    }
    
    updateOrderDisplay();
}

function updateQuantity(itemId, delta) {
    const item = orderItems.find(item => item.item_id === itemId);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            removeFromOrder(itemId);
        } else {
            updateOrderDisplay();
        }
    }
}

function updateOrderDisplay() {
    const container = document.getElementById('orderItems');
    const createBtn = document.getElementById('createOrderBtn');
    
    if (orderItems.length === 0) {
        container.innerHTML = `
            <div class="empty-cart-state">
                <i class="bi bi-cart-x"></i>
                <p>No items in cart</p>
            </div>
        `;
        createBtn.disabled = true;
        
        // Remove all selected states
        document.querySelectorAll('.menu-item-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
    } else {
        container.innerHTML = orderItems.map(item => `
            <div class="order-item">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <div class="order-item-name">${item.name}</div>
                        <small class="order-item-price">NPR ${item.price}</small>
                    </div>
                    <div class="quantity-control">
                        <button class="quantity-btn" onclick="updateQuantity(${item.item_id}, -1)" aria-label="Decrease quantity">
                            <i class="bi bi-dash"></i>
                        </button>
                        <span class="quantity-display">${item.quantity}</span>
                        <button class="quantity-btn" onclick="updateQuantity(${item.item_id}, 1)" aria-label="Increase quantity">
                            <i class="bi bi-plus"></i>
                        </button>
                        <button class="remove-item-btn" onclick="removeFromOrder(${item.item_id})" aria-label="Remove item">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="order-item-total">
                    <strong>NPR ${(item.price * item.quantity).toFixed(2)}</strong>
                </div>
            </div>
        `).join('');
        createBtn.disabled = false;
        
        // Update selected states
        orderItems.forEach(item => {
            const menuCard = document.querySelector(`[data-item-id="${item.item_id}"]`);
            if (menuCard) {
                menuCard.classList.add('selected');
            }
        });
    }
    
    // Calculate totals
    const subtotal = orderItems.reduce((sum, item) => sum + (Number(item.price) * item.quantity), 0);
    const total = subtotal;
    
    const formatCurrency = (amount) => `NPR ${Number(amount).toFixed(2)}`;
    
    document.getElementById('subtotal').textContent = formatCurrency(subtotal);
    document.getElementById('total').textContent = formatCurrency(total);
}

function clearOrder() {
    if (confirm('Clear all items from cart?')) {
        orderItems = [];
        updateOrderDisplay();
    }
}

function saveExpense() {
    const amount = document.getElementById('expenseAmount').value;
    const description = document.getElementById('expenseDescription').value;

    if (!amount || !description) {
        alert('Please fill in all fields');
        return;
    }

    fetch('{% url "pos:add_expense" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({
            amount: amount,
            description: description
            ,
            seller_id: document.getElementById('expenseSeller').value || null,
            seller_name: document.getElementById('expenseSellerName').value || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Expense added successfully!');
            document.getElementById('expenseForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('expenseModal')).hide();
            window.location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add expense');
    });
}

function createOrder() {
    const customerId = document.getElementById('customerSelect').value;
    const orderType = document.querySelector('input[name="orderType"]:checked').value;
    
    if (orderItems.length === 0) {
        alert('Please add items to the order');
        return;
    }
    
    const orderData = {
        customer_id: customerId || null,
        order_type: orderType,
        items: orderItems
    };
    
    const createBtn = document.getElementById('createOrderBtn');
    createBtn.disabled = true;
    createBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';
    
    fetch('{% url "pos:create_order" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Order ${data.order_number} created successfully!`);
            window.location.href = `/pos/order/${data.order_id}/payment/`;
        } else {
            alert('Error: ' + data.error);
            createBtn.disabled = false;
            createBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Create Order';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to create order');
        createBtn.disabled = false;
        createBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Create Order';
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Category tab functionality is handled by Bootstrap
    
    // Add visual feedback for order type selection
    document.querySelectorAll('input[name="orderType"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // Bootstrap handles the visual state automatically
            console.log('Order type selected:', this.value);
        });
    });
});