document.addEventListener('DOMContentLoaded', function() {
    // Form submission animation
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const btn = form.querySelector('button[type="submit"]');
            const originalContent = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span><span>Sending...</span>';
            btn.disabled = true;
            
            // Re-enable after 3 seconds (in case of client-side validation failure)
            setTimeout(function() {
                if (btn.disabled) {
                    btn.innerHTML = originalContent;
                    btn.disabled = false;
                }
            }, 3000);
        });
    }

    // Add focus animations to form fields
    const formControls = document.querySelectorAll('.zorpido-form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.01)';
            this.parentElement.style.transition = 'transform 0.3s ease';
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Character counter for message field (optional)
    const messageField = document.querySelector('textarea[name="message"]');
    if (messageField) {
        messageField.addEventListener('input', function() {
            const length = this.value.length;
            if (length > 0) {
                this.style.borderColor = 'var(--zorpido-red)';
            } else {
                this.style.borderColor = '#e9ecef';
            }
        });
    }

    // Add smooth scroll to form if coming from a link
    if (window.location.hash === '#contact-form') {
        document.getElementById('contactForm').scrollIntoView({ behavior: 'smooth' });
    }
});
