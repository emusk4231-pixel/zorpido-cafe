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
