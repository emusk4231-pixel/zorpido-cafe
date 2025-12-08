<<<<<<< HEAD
function openCreditModal(customerId, customerName, action) {
    document.getElementById('creditCustomerId').value = customerId;
    document.getElementById('creditAction').value = action;
    document.getElementById('creditAmount').value = '';
    
    const header = document.getElementById('creditModalHeader');
    const title = document.getElementById('creditModalTitle');
    const submitBtn = document.getElementById('creditSubmitBtn');
    
    if (action === 'add') {
        header.classList.remove('deduct');
        header.classList.add('add');
        title.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Add Credit to ' + customerName;
        submitBtn.className = 'btn btn-success';
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Add Credit';
    } else {
        header.classList.remove('add');
        header.classList.add('deduct');
        title.innerHTML = '<i class="bi bi-dash-circle me-2"></i>Deduct Credit from ' + customerName;
        submitBtn.className = 'btn btn-danger';
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Deduct Credit';
    }
    
    var modal = new bootstrap.Modal(document.getElementById('creditModal'));
    modal.show();
}

document.querySelectorAll('.credit-action-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        var customerId = this.dataset.customerId;
        var customerName = this.dataset.customerName;
        var action = this.dataset.action;
        openCreditModal(customerId, customerName, action);
    });
});

document.getElementById('creditForm').addEventListener('submit', function(e){
    e.preventDefault();
    var customerId = document.getElementById('creditCustomerId').value;
    var action = document.getElementById('creditAction').value;
    var amount = document.getElementById('creditAmount').value;

    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    const submitBtn = document.getElementById('creditSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

    fetch(`/pos/credit/${customerId}/update/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ action: action, amount: amount })
    }).then(r => r.json()).then(data => {
        if (data.success) {
            alert('Credit updated successfully!');
            location.reload();
        } else {
            alert(data.error || 'Failed to update credit');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Save';
        }
    }).catch(err => {
        console.error(err);
        alert('Failed to update credit');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Save';
    });
});

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

// View history
document.querySelectorAll('.view-history-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
        const customerId = this.dataset.customerId;
        const customerName = this.dataset.customerName;
        openHistoryModal(customerId, customerName);
    });
});

function openHistoryModal(customerId, customerName) {
    const from = document.getElementById('fromDate').value;
    const to = document.getElementById('toDate').value;
    fetch(`/pos/credit/${customerId}/history/?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                alert(data.error || 'Failed to load history');
                return;
            }
            let rows = '';
            data.transactions.forEach((t) => {
                rows += `<tr><td>${t.created_at}</td><td><span class="badge bg-${t.action === 'add' ? 'success' : 'danger'}">${t.action_display}</span></td><td>NPR ${t.amount}</td><td><strong>NPR ${t.balance_after}</strong></td><td>${t.note || '-'}</td></tr>`;
            });
            const html = `
                <div class="modal-header" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white;">
                    <h5 class="modal-title"><i class="bi bi-clock-history me-2"></i>Credit History for ${customerName}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" style="filter: brightness(0) invert(1);"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-modern">
                            <thead>
                                <tr><th>Date</th><th>Action</th><th>Amount</th><th>Balance After</th><th>Note</th></tr>
                            </thead>
                            <tbody>${rows || '<tr><td colspan="5" class="text-center text-muted">No transactions found</td></tr>'}</tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            `;
            const modalEl = document.getElementById('creditHistoryModalBody');
            modalEl.innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById('creditHistoryModal'));
            modal.show();
        }).catch(err => { 
            console.error(err); 
            alert('Failed to load history');
        });
}

document.getElementById('filterBtn').addEventListener('click', function(){
    const from = document.getElementById('fromDate').value;
    const to = document.getElementById('toDate').value;
    
    if (!from || !to) {
        alert('Please select both from and to dates');
        return;
    }
    
    alert('Date range selected. Click "History" for any customer to view filtered transactions.');
});
=======
function openCreditModal(customerId, customerName, action) {
    document.getElementById('creditCustomerId').value = customerId;
    document.getElementById('creditAction').value = action;
    document.getElementById('creditAmount').value = '';
    
    const header = document.getElementById('creditModalHeader');
    const title = document.getElementById('creditModalTitle');
    const submitBtn = document.getElementById('creditSubmitBtn');
    
    if (action === 'add') {
        header.classList.remove('deduct');
        header.classList.add('add');
        title.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Add Credit to ' + customerName;
        submitBtn.className = 'btn btn-success';
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Add Credit';
    } else {
        header.classList.remove('add');
        header.classList.add('deduct');
        title.innerHTML = '<i class="bi bi-dash-circle me-2"></i>Deduct Credit from ' + customerName;
        submitBtn.className = 'btn btn-danger';
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Deduct Credit';
    }
    
    var modal = new bootstrap.Modal(document.getElementById('creditModal'));
    modal.show();
}

document.querySelectorAll('.credit-action-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
        var customerId = this.dataset.customerId;
        var customerName = this.dataset.customerName;
        var action = this.dataset.action;
        openCreditModal(customerId, customerName, action);
    });
});

document.getElementById('creditForm').addEventListener('submit', function(e){
    e.preventDefault();
    var customerId = document.getElementById('creditCustomerId').value;
    var action = document.getElementById('creditAction').value;
    var amount = document.getElementById('creditAmount').value;

    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }

    const submitBtn = document.getElementById('creditSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

    fetch(`/pos/credit/${customerId}/update/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ action: action, amount: amount })
    }).then(r => r.json()).then(data => {
        if (data.success) {
            alert('Credit updated successfully!');
            location.reload();
        } else {
            alert(data.error || 'Failed to update credit');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Save';
        }
    }).catch(err => {
        console.error(err);
        alert('Failed to update credit');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Save';
    });
});

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

// View history
document.querySelectorAll('.view-history-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
        const customerId = this.dataset.customerId;
        const customerName = this.dataset.customerName;
        openHistoryModal(customerId, customerName);
    });
});

function openHistoryModal(customerId, customerName) {
    const from = document.getElementById('fromDate').value;
    const to = document.getElementById('toDate').value;
    fetch(`/pos/credit/${customerId}/history/?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`)
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                alert(data.error || 'Failed to load history');
                return;
            }
            let rows = '';
            data.transactions.forEach((t) => {
                rows += `<tr><td>${t.created_at}</td><td><span class="badge bg-${t.action === 'add' ? 'success' : 'danger'}">${t.action_display}</span></td><td>NPR ${t.amount}</td><td><strong>NPR ${t.balance_after}</strong></td><td>${t.note || '-'}</td></tr>`;
            });
            const html = `
                <div class="modal-header" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white;">
                    <h5 class="modal-title"><i class="bi bi-clock-history me-2"></i>Credit History for ${customerName}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" style="filter: brightness(0) invert(1);"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-modern">
                            <thead>
                                <tr><th>Date</th><th>Action</th><th>Amount</th><th>Balance After</th><th>Note</th></tr>
                            </thead>
                            <tbody>${rows || '<tr><td colspan="5" class="text-center text-muted">No transactions found</td></tr>'}</tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer border-0">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            `;
            const modalEl = document.getElementById('creditHistoryModalBody');
            modalEl.innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById('creditHistoryModal'));
            modal.show();
        }).catch(err => { 
            console.error(err); 
            alert('Failed to load history');
        });
}

document.getElementById('filterBtn').addEventListener('click', function(){
    const from = document.getElementById('fromDate').value;
    const to = document.getElementById('toDate').value;
    
    if (!from || !to) {
        alert('Please select both from and to dates');
        return;
    }
    
    alert('Date range selected. Click "History" for any customer to view filtered transactions.');
});
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
