let currentItemId = null;
const stockModal = new bootstrap.Modal(document.getElementById('stockModal'));

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
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
  const itemId = Number(button.getAttribute('data-item-id'));
  const itemName = button.getAttribute('data-item-name');
  const currentStock = Number(button.getAttribute('data-current-stock') || 0);
  const lowThreshold = Number(button.getAttribute('data-low-threshold') || 0);
  const availability = button.getAttribute('data-availability') || 'available';
  const sku = button.getAttribute('data-item-sku') || '';
  const price = button.getAttribute('data-price') || '';
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

  const action = document.getElementById('stockAction').value;
  const quantity = parseInt(document.getElementById('stockQuantity').value);
  const lowThreshold = parseInt(document.getElementById('lowThreshold').value || 0);
  const availability = document.getElementById('availabilitySelect').value;

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

  const updateBtn = document.querySelector('#stockModal .btn-modal-confirm');
  if (updateBtn) {
    updateBtn.disabled = true;
    updateBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Updating...';
  }

  try {
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

    let data = null;
    try {
      data = await resp.json();
    } catch (e) {
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
          } else {
            availEl.classList.add('badge-info-custom');
            availEl.textContent = data.availability_display || data.availability;
          }
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
    if (updateBtn) {
      updateBtn.disabled = false;
      updateBtn.innerHTML = '<i class="bi bi-check-circle"></i> Update Stock';
    }
  }
}

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
      }
    }
  }
}
