<<<<<<< HEAD
function postJson(url, body){
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(body || {})
  }).then(r => r.json());
}

document.querySelectorAll('.complete-now').forEach(function(btn){
  btn.addEventListener('click', function(){
    const id = this.dataset.id;
    const originalHTML = this.innerHTML;
    this.innerHTML = '<span class="loading-spinner"></span> Processing...';
    this.disabled = true;
    
    setTimeout(() => {
      window.location.href = `/pos/order/${id}/payment/`;
    }, 300);
  });
});

document.querySelectorAll('.delete-order').forEach(function(btn){
  btn.addEventListener('click', function(){
    const id = this.dataset.id;
    if(!confirm('⚠️ Delete this order?\n\nThis action cannot be undone and will permanently remove all order data.')) return;
    
    const originalHTML = this.innerHTML;
    this.innerHTML = '<span class="loading-spinner"></span>';
    this.disabled = true;
    
    postJson(`/pos/order/${id}/delete/`, {}).then(data => {
      if(data.success) {
        location.reload();
      } else {
        alert('❌ Failed to delete order: ' + (data.error || 'Unknown error'));
        this.innerHTML = originalHTML;
        this.disabled = false;
      }
    }).catch(err => {
      alert('❌ Network error: ' + err.message);
      this.innerHTML = originalHTML;
      this.disabled = false;
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
=======
function postJson(url, body){
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(body || {})
  }).then(r => r.json());
}

document.querySelectorAll('.complete-now').forEach(function(btn){
  btn.addEventListener('click', function(){
    const id = this.dataset.id;
    const originalHTML = this.innerHTML;
    this.innerHTML = '<span class="loading-spinner"></span> Processing...';
    this.disabled = true;
    
    setTimeout(() => {
      window.location.href = `/pos/order/${id}/payment/`;
    }, 300);
  });
});

document.querySelectorAll('.delete-order').forEach(function(btn){
  btn.addEventListener('click', function(){
    const id = this.dataset.id;
    if(!confirm('⚠️ Delete this order?\n\nThis action cannot be undone and will permanently remove all order data.')) return;
    
    const originalHTML = this.innerHTML;
    this.innerHTML = '<span class="loading-spinner"></span>';
    this.disabled = true;
    
    postJson(`/pos/order/${id}/delete/`, {}).then(data => {
      if(data.success) {
        location.reload();
      } else {
        alert('❌ Failed to delete order: ' + (data.error || 'Unknown error'));
        this.innerHTML = originalHTML;
        this.disabled = false;
      }
    }).catch(err => {
      alert('❌ Network error: ' + err.message);
      this.innerHTML = originalHTML;
      this.disabled = false;
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
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
