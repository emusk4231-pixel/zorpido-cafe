<<<<<<< HEAD
        // Intersection Observer for scroll animations
    const sections = document.querySelectorAll('.about-us-section');
        
        const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
        }, {
        threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
        });

        sections.forEach(section => {
        observer.observe(section);
        });

    // Add hover effect to feature cards
    const featureCards = document.querySelectorAll('.about-us-feature-card');
        featureCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.background = 'linear-gradient(135deg, #fffbf0 0%, #fff9e6 100%)';
        });
    card.addEventListener('mouseleave', function() {
        this.style.background = 'linear-gradient(135deg, #fff 0%, #fffbf0 100%)';
            });
        });

        // Smooth scroll behavior
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
        });
=======
document.addEventListener('DOMContentLoaded', function() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe story features
    document.querySelectorAll('.story-feature').forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(-30px)';
        el.style.transition = 'all 0.6s ease';
        el.style.transitionDelay = `${index * 0.2}s`;
        observer.observe(el);
    });

    // Observe value cards
    document.querySelectorAll('.value-card').forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        el.style.transitionDelay = `${index * 0.15}s`;
        observer.observe(el);
    });

    // Observe team cards
    document.querySelectorAll('.team-member-card').forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        el.style.transitionDelay = `${index * 0.2}s`;
        observer.observe(el);
    });

    // Observe mission cards
    document.querySelectorAll('.mission-card').forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'scale(0.9)';
        el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        el.style.transitionDelay = `${index * 0.2}s`;
        observer.observe(el);
    });

    // Add ripple effect to CTA button
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 193, 7, 0.5);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    }

    // Parallax effect for hero section
    const heroSection = document.querySelector('.about-hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            if (scrolled < 600) {
                heroSection.style.transform = `translateY(${scrolled * 0.5}px)`;
            }
        });
    }

    // Add hover sound effect simulation (visual feedback)
    document.querySelectorAll('.story-feature, .value-card, .team-member-card, .mission-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });

    // Counter animation for stats (if you want to add stats later)
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = Math.floor(target);
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    }

    // Smooth scroll for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation completion
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });

    // Team image rotation pause on hover
    document.querySelectorAll('.team-member-card').forEach(card => {
        const imageWrapper = card.querySelector('.team-image-wrapper::before');
        card.addEventListener('mouseenter', function() {
            if (imageWrapper) {
                imageWrapper.style.animationPlayState = 'paused';
            }
        });
        card.addEventListener('mouseleave', function() {
            if (imageWrapper) {
                imageWrapper.style.animationPlayState = 'running';
            }
        });
    });

    // Add dynamic gradient movement based on scroll
    const missionSection = document.querySelector('.mission-section');
    if (missionSection) {
        window.addEventListener('scroll', function() {
            const rect = missionSection.getBoundingClientRect();
            const scrollPercent = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / window.innerHeight));
            missionSection.style.backgroundPosition = `${scrollPercent * 100}% 50%`;
        });
    }

    // Add stagger animation to story content on load
    const storyElements = document.querySelectorAll('.story-badge, .story-title, .lead');
    storyElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.6s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 200);
    });
});

// Add ripple animation CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    /* Loading state */
    body:not(.loaded) * {
        animation-play-state: paused !important;
    }
    
    /* Smooth transitions */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #dc3545 0%, #ffc107 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #c62828 0%, #ffa000 100%);
    }
`;
document.head.appendChild(style);
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
