/*
  toasts.js
  - Converts Django `messages` into slide-in toast popups on the right side.
  - Auto-hides after 3 seconds, can be dismissed manually.
  - Works by reading a small data blob rendered server-side into the DOM.
*/

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('zorpido-toast-container');
  if (!container) return;

  // Django messages are not rendered directly here (we moved rendering to JS to avoid
  // mixing with the main content). We'll look for a special JSON payload
  // placed by Django templates (if any). If there's none, the server-side template
  // can also render inline .zorpido-toast elements which this will handle.

  // 1) If there are pre-rendered toast elements inside container, collect them
  const preToasts = Array.from(container.querySelectorAll('.zorpido-toast'));

  // Helper to create a toast element
  function createToast(message, level) {
    const toast = document.createElement('div');
    toast.className = 'zorpido-toast ' + (level === 'error' || level === 'danger' ? 'toast-error' : 'toast-success');
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');

    // Optional icon
    const icon = document.createElement('div');
    icon.className = 'toast-icon';
    icon.innerHTML = (level === 'error' || level === 'danger') ? '<i class="bi bi-x-circle-fill"></i>' : '<i class="bi bi-check-circle-fill"></i>';

    const msg = document.createElement('div');
    msg.className = 'toast-message';
    msg.innerHTML = message;

    const btn = document.createElement('button');
    btn.className = 'toast-close';
    btn.type = 'button';
    btn.setAttribute('aria-label','Close');
    btn.innerHTML = '&times;';

    btn.addEventListener('click', () => hideToast(toast));

    toast.appendChild(icon);
    toast.appendChild(msg);
    toast.appendChild(btn);

    return toast;
  }

  function showToast(el, duration = 3000) {
    // append and trigger animation
    container.appendChild(el);
    // force reflow for transition
    void el.offsetWidth;
    el.classList.add('show');

    // Auto-hide
    const timeout = setTimeout(() => {
      hideToast(el);
    }, duration);

    // Allow manual hide to cancel auto-hide
    el.dataset._timeout = timeout;
  }

  function hideToast(el) {
    // clear auto-hide timeout if present
    const t = el.dataset && el.dataset._timeout;
    if (t) clearTimeout(t);

    el.classList.remove('show');
    el.classList.add('hiding');
    // remove from DOM after transition
    setTimeout(() => {
      try { if (el.parentNode) el.parentNode.removeChild(el); } catch(e){}
    }, 380);
  }

  // If template rendered messages as JSON blob in a script tag with id 'zorpido-django-messages', parse it
  const payloadScript = document.getElementById('zorpido-django-messages');
  if (payloadScript) {
    try {
      const payload = JSON.parse(payloadScript.textContent || '[]');
      payload.forEach(item => {
        const t = createToast(item.message, item.level || 'info');
        showToast(t, item.duration || 3000);
      });
    } catch (e) {
      console.error('Invalid zorpido-django-messages payload', e);
    }
  }

  // Also initialize any pre-rendered toasts inside the container
  if (preToasts.length) {
    preToasts.forEach(pt => {
      // determine level from class or data-tags
      const tags = (pt.dataset && pt.dataset.tags) ? pt.dataset.tags : pt.className;
      const level = /error|danger/.test(tags) ? 'error' : ( /success/.test(tags) ? 'success' : 'info');
      pt.classList.add(level === 'error' ? 'toast-error' : 'toast-success');
      // attach close handler
      const closeBtn = pt.querySelector('.toast-close');
      if (closeBtn) closeBtn.addEventListener('click', () => hideToast(pt));
      showToast(pt, parseInt(pt.dataset.duration || 3000, 10));
    });
  }

  // As a convenience: if there are legacy .alert elements in the DOM produced by other templates,
  // convert them into toasts and then remove legacy alerts.
  const legacyAlerts = Array.from(document.querySelectorAll('.alert')).filter(a => !a.closest('#zorpido-toast-container'));
  if (legacyAlerts.length) {
    legacyAlerts.forEach(a => {
      const tags = a.className;
      const level = /alert-danger|alert-error/.test(tags) ? 'error' : (/alert-success/.test(tags) ? 'success' : 'info');
      const msgHtml = a.innerHTML.replace(/<button[\s\S]*?>[\s\S]*?<\/button>/i,'');
      const t = createToast(msgHtml, level);
      showToast(t, 3000);
      // remove the legacy alert from DOM
      try { a.parentNode.removeChild(a); } catch(e){}
    });
  }

});
