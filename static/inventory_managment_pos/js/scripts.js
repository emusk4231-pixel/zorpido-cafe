<<<<<<< HEAD
/**
 * INVENTORY MANAGEMENT JAVASCRIPT - FIXED VERSION
 * ================================================
 * Handles Add Stock and Update Stock functionality for menu items
 * 
 * Features:
 * - Add stock to menu items
 * - Decrease stock from menu items  
 * - Set stock to exact quantity
 * - Update low stock thresholds
 * - Update item availability status
 * - Real-time UI updates with color-coded badges
 * - Error handling and user feedback via toast notifications
 */

// ===== GLOBAL VARIABLES =====

// Store the current item ID being edited in the modal
let currentItemId = null;

// Initialize Bootstrap modal for stock updates
const stockModalElement = document.getElementById('stockModal');
const stockModal = stockModalElement ? new bootstrap.Modal(stockModalElement) : null;


// ===== UTILITY FUNCTIONS =====

/**
 * Retrieve CSRF token from browser cookies
 * Django requires CSRF tokens for POST requests to prevent cross-site attacks
 * 
 * @param {string} name - Cookie name to search for (default: 'csrftoken')
 * @returns {string|null} - CSRF token value or null if not found
 */
function getCookie(name) {
  let cookieValue = null;
  
  // Check if cookies exist
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    
    // Loop through all cookies
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      
      // Check if this cookie is the one we're looking for
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        // Extract and decode the cookie value
=======
let currentItemId = null;
const stockModal = new bootstrap.Modal(document.getElementById('stockModal'));

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
<<<<<<< HEAD
  
  return cookieValue;
}


// ===== MODAL FUNCTIONS =====

/**
 * Open stock update modal with item details
 * Internal function called by openStockModalFromButton()
 * 
 * @param {number} itemId - Menu item ID from database
 * @param {string} itemName - Display name of the item
 * @param {number} currentStock - Current stock quantity
 */
function openStockModal(itemId, itemName, currentStock) {
  // Store item ID for later use in updateStock() function
  currentItemId = itemId;
  
  // Populate modal header with item name
  document.getElementById('modalItemName').textContent = itemName;
  
  // Display current stock level in badge
  document.getElementById('modalCurrentStock').textContent = currentStock;
  
  // Reset quantity input field for new entry
  document.getElementById('stockQuantity').value = 0;
  
  // Reset stock action dropdown to 'add' (default action)
  document.getElementById('stockAction').value = 'add';
  
  // Show the modal dialog
  if (stockModal) {
    stockModal.show();
  } else {
    console.error('Stock modal not initialized. Cannot open dialog.');
  }
}

/**
 * Open stock update modal from button click
 * 
 * This function is called directly from HTML button onclick handlers:
 * onclick="openStockModalFromButton(this)"
 * 
 * It extracts all item data from button data attributes and populates
 * the modal form with these values.
 * 
 * @param {HTMLElement} button - The clicked button element containing data attributes
 */
function openStockModalFromButton(button) {
  // Extract all item data from button attributes
  // The template sets these attributes: data-item-id, data-item-name, data-current-stock, etc.
  
=======
  return cookieValue;
}

function openStockModal(itemId, itemName, currentStock) {
  currentItemId = itemId;
  document.getElementById('modalItemName').textContent = itemName;
  document.getElementById('modalCurrentStock').textContent = currentStock;
  document.getElementById('stockQuantity').value = 0;
  stockModal.show();
}

function openStockModalFromButton(button) {
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
  const itemId = Number(button.getAttribute('data-item-id'));
  const itemName = button.getAttribute('data-item-name');
  const currentStock = Number(button.getAttribute('data-current-stock') || 0);
  const lowThreshold = Number(button.getAttribute('data-low-threshold') || 0);
  const availability = button.getAttribute('data-availability') || 'available';
  const sku = button.getAttribute('data-item-sku') || '';
  const price = button.getAttribute('data-price') || '';
<<<<<<< HEAD
  const purchasePrice = button.getAttribute('data-purchase-price') || '';
  
  // Validate that we have a valid item ID
  if (!itemId || itemId <= 0) {
    showInventoryNotification('❌ Invalid item ID. Cannot open editor.', 'error');
    console.error('Invalid item ID:', itemId);
    return;
  }
  
  // Open modal and populate initial values
  openStockModal(itemId, itemName, currentStock);
  
  // Set low threshold input field
  document.getElementById('lowThreshold').value = lowThreshold;
  
  // Set availability dropdown to current value
  document.getElementById('availabilitySelect').value = availability;
  
  // Populate SKU display in modal (read-only)
  const skuEl = document.getElementById('modalSKU');
  if (skuEl) {
    skuEl.textContent = sku ? `#${sku}` : '-';
  }
  
  // Populate price display in modal (read-only)
  const priceEl = document.getElementById('modalPrice');
  if (priceEl) {
    priceEl.textContent = price ? `NPR ${price}` : 'NPR 0.00';
  }

  // Populate new editable price fields if available
  const purchaseInput = document.getElementById('modalPurchasePrice');
  const sellingInput = document.getElementById('modalSellingPrice');
  if (purchaseInput) purchaseInput.value = purchasePrice || '';
  if (sellingInput) sellingInput.value = price || '';
  
  // Log for debugging
  console.log(`✓ Opened editor modal for item ID ${itemId}: ${itemName}`);
}


// ===== STOCK UPDATE LOGIC =====

/**
 * Update stock for a menu item via AJAX
 * 
 * This function:
 * 1. Validates all form inputs
 * 2. Sends AJAX POST request to backend
 * 3. Updates UI with new stock values
 * 4. Shows success/error notifications
 * 
 * Called from modal 'Update Stock' button onclick
 */
async function updateStock() {
  // ===== INPUT VALIDATION =====
  
  // Check if an item is selected
  if (!currentItemId || currentItemId <= 0) {
    showInventoryNotification('❌ No item selected. Please open an item first.', 'error');
    console.error('No valid item ID set for stock update');
    return;
  }

  // Get form values from modal inputs
=======
  openStockModal(itemId, itemName, currentStock);
  document.getElementById('lowThreshold').value = lowThreshold;
  document.getElementById('availabilitySelect').value = availability;
  // populate SKU and price displays in the modal
  const skuEl = document.getElementById('modalSKU');
  if (skuEl) skuEl.textContent = sku ? `#${sku}` : '-';
  const priceEl = document.getElementById('modalPrice');
  if (priceEl) priceEl.textContent = price ? `NPR ${price}` : 'NPR 0.00';
}

async function updateStock() {
  if (!currentItemId) {
    alert('⚠️ No item selected');
    return;
  }

>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
  const action = document.getElementById('stockAction').value;
  const quantity = parseInt(document.getElementById('stockQuantity').value);
  const lowThreshold = parseInt(document.getElementById('lowThreshold').value || 0);
  const availability = document.getElementById('availabilitySelect').value;

<<<<<<< HEAD
  // Validate quantity is a valid number
  if (isNaN(quantity)) {
    showInventoryNotification('❌ Please enter a valid quantity number', 'error');
    return;
  }

  // Validate quantity is not negative
  if (quantity < 0) {
    showInventoryNotification('❌ Quantity cannot be negative', 'error');
    return;
  }

  // Get current stock from modal display
  const modalCurrent = Number(document.getElementById('modalCurrentStock').textContent || 0);

  // Action-specific validation
  if (action === 'add') {
    // Adding stock requires quantity > 0
    if (quantity <= 0) {
      showInventoryNotification('❌ Enter a quantity greater than 0 to add stock', 'error');
      return;
    }
  } else if (action === 'decrease') {
    // Decreasing stock requires quantity > 0
    if (quantity <= 0) {
      showInventoryNotification('❌ Enter a quantity greater than 0 to decrease stock', 'error');
      return;
    }
    // Cannot decrease more than current stock
    if (quantity > modalCurrent) {
      showInventoryNotification(`❌ Cannot decrease by ${quantity}. Current stock is only ${modalCurrent}`, 'error');
      return;
    }
  }
  // 'set' action allows any non-negative value

  // ===== DISABLE BUTTON AND SHOW LOADING STATE =====
  
=======
  if (isNaN(quantity)) {
    alert('⚠️ Please enter a valid quantity');
    return;
  }
  if (quantity < 0) {
    alert('⚠️ Quantity must be positive');
    return;
  }
  const modalCurrent = Number(document.getElementById('modalCurrentStock').textContent || 0);
  if (action === 'add' && quantity <= 0) {
    alert('⚠️ Please enter a quantity greater than zero to add');
    return;
  }
  if (action === 'decrease') {
    if (quantity <= 0) {
      alert('⚠️ Please enter a quantity greater than zero to decrease');
      return;
    }
    if (quantity > modalCurrent) {
      alert('⚠️ Cannot decrease more than current stock');
      return;
    }
  }

>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
  const updateBtn = document.querySelector('#stockModal .btn-modal-confirm');
  if (updateBtn) {
    updateBtn.disabled = true;
    updateBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Updating...';
  }

  try {
<<<<<<< HEAD
    // ===== SEND AJAX REQUEST TO BACKEND =====
    
    console.log(`Sending stock update request: item=${currentItemId}, action=${action}, quantity=${quantity}, threshold=${lowThreshold}, availability=${availability}`);
    
    // Fetch API call to update endpoint
    const resp = await fetch(`/pos/inventory/${currentItemId}/update/`, {
      method: 'POST',  // POST required by Django @require_POST decorator
      headers: {
        'Content-Type': 'application/json',  // Sending JSON data
        'X-CSRFToken': getCookie('csrftoken')  // Django CSRF protection
      },
      body: JSON.stringify({
        action: action,              // 'add', 'decrease', or 'set'
        quantity: quantity,          // Quantity to change/set
        low_threshold: lowThreshold, // Low stock threshold (optional)
        availability: availability   // Availability status (optional)
        ,
        // Include price updates if provided in modal
        purchase_price: (document.getElementById('modalPurchasePrice') ? document.getElementById('modalPurchasePrice').value : null),
        price: (document.getElementById('modalSellingPrice') ? document.getElementById('modalSellingPrice').value : null)
      })
    });

    // Try to parse JSON response
=======
    const resp = await fetch(`/pos/inventory/${currentItemId}/update/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        action: action,
        quantity: quantity,
        low_threshold: lowThreshold,
        availability: availability
      })
    });

>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
    let data = null;
    try {
      data = await resp.json();
    } catch (e) {
<<<<<<< HEAD
      // Server may have returned non-JSON response
      console.error('Failed to parse JSON response:', e);
    }

    // ===== HANDLE SERVER ERROR RESPONSES =====
    
    if (!resp.ok) {
      // Server returned error status code (4xx, 5xx)
      const errMsg = data && data.error 
        ? data.error 
        : `Server error: ${resp.status} ${resp.statusText}`;
      
      console.error('Server error response:', resp.status, errMsg);
      showInventoryNotification(`❌ Error: ${errMsg}`, 'error');
      return;
    }

    // ===== HANDLE SUCCESS RESPONSE =====
    
    if (data && data.success) {
      console.log('✓ Stock update successful:', data);
      
      // Get new stock value from server response
      const newStock = (typeof data.new_stock !== 'undefined') ? Number(data.new_stock) : null;
      const lowThresh = Number(document.getElementById('lowThreshold').value || 0);

      // ===== UPDATE STOCK BADGES ON PAGE =====
      
      if (newStock !== null) {
        // Find all stock badges for this item throughout the page
        const badges = document.querySelectorAll(`[data-stock-badge="${currentItemId}"]`);
        
        badges.forEach(badge => {
          // Update badge text with new stock quantity
          badge.textContent = newStock;
          
          // Remove all color classes
          badge.classList.remove('badge-success-custom', 'badge-warning-custom', 'badge-danger-custom');
          
          // Apply appropriate color based on new stock level
          if (newStock <= 0) {
            badge.classList.add('badge-danger-custom');  // Red for out of stock
          } else if (newStock <= lowThresh) {
            badge.classList.add('badge-warning-custom');  // Yellow for low stock
          } else {
            badge.classList.add('badge-success-custom');  // Green for healthy stock
          }
          
          console.log(`Updated badge for item ${currentItemId}: new stock = ${newStock}`);
        });

        // Update modal display to show new stock
        const modalCurrentEl = document.getElementById('modalCurrentStock');
        if (modalCurrentEl) {
          modalCurrentEl.textContent = newStock;
        }

          // Update price/purchase price displays on the page if provided
          if (data.price || data.purchase_price) {
            // Find elements that show price
            const priceEls = document.querySelectorAll(`[data-price]`);
            priceEls.forEach(el => {
              const pid = Number(el.getAttribute('data-item-id') || el.getAttribute('data-item-sku') || 0);
              if (pid === currentItemId && data.price) {
                // We assume there is a nearby element showing selling price; reload page as fallback
                // Simple approach: reload page to reflect price changes server-side
                location.reload();
              }
            });
          }
      }

      // ===== UPDATE AVAILABILITY BADGES =====
      
      if (data.availability) {
        const availEls = document.querySelectorAll(`[data-availability="${currentItemId}"]`);
        
        availEls.forEach(availEl => {
          // Remove all color classes
          availEl.classList.remove('badge-success-custom', 'badge-danger-custom', 'badge-info-custom');
          
          // Update badge with new availability status
          if (data.availability === 'available') {
            availEl.classList.add('badge-success-custom');
            availEl.textContent = '✅ Available';
          } else if (data.availability === 'out_of_stock') {
            availEl.classList.add('badge-danger-custom');
            availEl.textContent = '❌ Out of Stock';
=======
      // non-json response
    }

    if (!resp.ok) {
      const errMsg = data && data.error ? data.error : `Server responded with status ${resp.status}`;
      alert('❌ Error: ' + errMsg);
      return;
    }

    if (data && data.success) {
      // Update UI dynamically
      const newStock = (typeof data.new_stock !== 'undefined') ? Number(data.new_stock) : null;
      const lowThresh = Number(document.getElementById('lowThreshold').value || 0);

      if (newStock !== null) {
        // update all badges that reference this item
        const badges = document.querySelectorAll(`[data-stock-badge="${currentItemId}"]`);
        badges.forEach(badge => {
          badge.textContent = newStock;
          badge.classList.remove('badge-success-custom','badge-warning-custom','badge-danger-custom');
          if (newStock <= 0) {
            badge.classList.add('badge-danger-custom');
          } else if (newStock <= lowThresh) {
            badge.classList.add('badge-warning-custom');
          } else {
            badge.classList.add('badge-success-custom');
          }
        });

        // update modal display
        const modalCurrent = document.getElementById('modalCurrentStock');
        if (modalCurrent) modalCurrent.textContent = newStock;
      }

      // update availability badge if provided
      if (data.availability) {
        const availEls = document.querySelectorAll(`[data-availability="${currentItemId}"]`);
        availEls.forEach(availEl => {
          availEl.classList.remove('badge-success-custom','badge-danger-custom','badge-info-custom');
          if (data.availability === 'available') {
            availEl.classList.add('badge-success-custom');
            availEl.textContent = 'Available';
          } else if (data.availability === 'out_of_stock') {
            availEl.classList.add('badge-danger-custom');
            availEl.textContent = 'Out of Stock';
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
          } else {
            availEl.classList.add('badge-info-custom');
            availEl.textContent = data.availability_display || data.availability;
          }
<<<<<<< HEAD
          
          console.log(`Updated availability badge for item ${currentItemId}: ${data.availability}`);
        });
      }

      // Show success notification
      showInventoryNotification(`✅ ${data.message || 'Stock updated successfully'}`, 'success');
      
      // Close the modal
      if (stockModal) {
        stockModal.hide();
      }
    } else {
      // Success status but data.success is false (shouldn't happen with 200 response)
      const errMsg = data && data.error ? data.error : 'Unknown error occurred';
      console.error('Update marked as failed:', errMsg);
      showInventoryNotification(`❌ Error: ${errMsg}`, 'error');
    }
  } catch (error) {
    // Network error or other JavaScript exception
    console.error('Exception during stock update:', error);
    showInventoryNotification(`❌ Network error: ${error.message || error}`, 'error');
  } finally {
    // ===== RE-ENABLE BUTTON AND RESTORE NORMAL STATE =====
    
=======
        });
      }

      // show success toast and close modal
      showInventoryNotification('Stock updated successfully', 'success');
      stockModal.hide();
    } else {
      showInventoryNotification('Error: ' + (data && data.error ? data.error : 'Unknown error'), 'error');
    }
  } catch (error) {
    console.error('Error updating stock:', error);
    showInventoryNotification('Failed to update stock: ' + (error.message || error), 'error');
  } finally {
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
    if (updateBtn) {
      updateBtn.disabled = false;
      updateBtn.innerHTML = '<i class="bi bi-check-circle"></i> Update Stock';
    }
  }
}

<<<<<<< HEAD

// ===== NOTIFICATION AND UI HELPERS =====

/**
 * Show a temporary notification toast message
 * 
 * Used for success/error feedback after stock updates and other actions.
 * The notification appears in the top-right corner and automatically
 * disappears after 2.5 seconds.
 * 
 * @param {string} message - The message to display to the user
 * @param {string} type - Notification type: 'success' (green), 'error' (red), or 'info' (blue)
 */
function showInventoryNotification(message, type = 'info') {
  // Create notification element
  const el = document.createElement('div');
  el.className = `inventory-toast toast-${type}`;
  
  // Base styles for all notifications
  el.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 0.8rem 1rem;
    color: #fff;
    border-radius: 8px;
    z-index: 11000;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    font-weight: 600;
    max-width: 400px;
    word-wrap: break-word;
  `;
  
  // Apply color based on notification type
  if (type === 'error') {
    el.style.background = '#DC2626';  // Red for errors
  } else if (type === 'success') {
    el.style.background = '#10B981';  // Green for success
  } else {
    el.style.background = '#3B82F6';  // Blue for info
  }
  
  // Set notification text
  el.textContent = message;
  
  // Add to page
  document.body.appendChild(el);
  
  // Auto-remove after 2.5 seconds with fade animation
  setTimeout(() => {
    el.style.transition = 'opacity 0.3s ease';
    el.style.opacity = '0';
    
    // Remove element from DOM after fade completes
    setTimeout(() => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }, 300);
  }, 2500);
}

/**
 * Filter inventory table by item name
 * 
 * Searches for the input value in the first column (item name)
 * and hides/shows rows accordingly. Case-insensitive search.
 */
function filterTable() {
  // Get search input value
  const input = document.getElementById('searchInput');
  const filter = input.value.toUpperCase();
  
  // Get the inventory table
  const table = document.getElementById('inventoryTable');
  const tr = table.getElementsByTagName('tr');

  // Loop through all table rows
  for (let i = 1; i < tr.length; i++) {  // Start at 1 to skip header row
    const td = tr[i].getElementsByTagName('td')[0];  // Get first column (item name)
    
    if (td) {
      const txtValue = td.textContent || td.innerText;
      
      // Show/hide row based on whether item name matches search
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = '';  // Show row
      } else {
        tr[i].style.display = 'none';  // Hide row
=======
// small notification helper for inventory page
function showInventoryNotification(message, type='info') {
  const el = document.createElement('div');
  el.className = `inventory-toast toast-${type}`;
  el.style.cssText = 'position:fixed;top:20px;right:20px;padding:0.8rem 1rem;background:#10B981;color:#fff;border-radius:8px;z-index:11000;box-shadow:0 6px 18px rgba(0,0,0,0.15);font-weight:600;';
  if (type==='error') el.style.background = '#DC2626';
  if (type==='info') el.style.background = '#3B82F6';
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(()=>{
    el.style.transition='opacity 0.3s'; el.style.opacity='0';
    setTimeout(()=>el.remove(),300);
  },2500);
}

function filterTable() {
  const input = document.getElementById('searchInput');
  const filter = input.value.toUpperCase();
  const table = document.getElementById('inventoryTable');
  const tr = table.getElementsByTagName('tr');

  for (let i = 1; i < tr.length; i++) {
    const td = tr[i].getElementsByTagName('td')[0];
    if (td) {
      const txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = '';
      } else {
        tr[i].style.display = 'none';
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
      }
    }
  }
}
