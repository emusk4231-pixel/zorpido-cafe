// Social sharing functionality
document.addEventListener('DOMContentLoaded', function() {
    const shareButtons = document.querySelectorAll('.share-btn');
    const pageUrl = encodeURIComponent(window.location.href);
    const pageTitle = encodeURIComponent(document.title);
    
    shareButtons.forEach(btn => {
        if (btn.classList.contains('facebook')) {
            btn.href = `https://www.facebook.com/sharer/sharer.php?u=${pageUrl}`;
        } else if (btn.classList.contains('twitter')) {
            btn.href = `https://twitter.com/intent/tweet?url=${pageUrl}&text=${pageTitle}`;
        } else if (btn.classList.contains('linkedin')) {
            btn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${pageUrl}`;
        }
        
        if (!btn.classList.contains('email')) {
            btn.target = '_blank';
            btn.rel = 'noopener noreferrer';
        }
    });
});
