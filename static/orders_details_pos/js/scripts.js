// Add item handler
document.querySelectorAll('.add-item-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
        const itemId = this.dataset.itemId;
        
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        
        fetch('{% url "pos:add_item" order.id %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ item_id: itemId, quantity: 1 })
        }).then(r => r.json()).then(data => {
            if(data.success){
                location.reload();
            } else {
                alert(data.error || 'Failed to add item');
                this.disabled = false;
                this.innerHTML = '<i class="bi bi-plus-lg"></i> Add';
            }
        }).catch(err => {
            console.error(err);
            alert('Failed to add item');
            this.disabled = false;
            this.innerHTML = '<i class="bi bi-plus-lg"></i> Add';
        });
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

// Complete order button handler
document.addEventListener('DOMContentLoaded', function(){
    var completeBtn = document.getElementById('completeOrderBtn');
    if(completeBtn){
        completeBtn.addEventListener('click', function(){
            // Redirect to payment page
            window.location.href = `/pos/order/{{ order.id }}/payment/`;
        });
    }
});
