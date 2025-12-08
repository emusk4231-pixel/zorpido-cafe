document.addEventListener('DOMContentLoaded', function() {
  // Modal functionality with enhanced animations
  const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
  
  modalTriggers.forEach(btn => {
    btn.addEventListener('click', function() {
      const imageSrc = this.dataset.image || '';
      const imageEl = document.getElementById('modalDishImage');
      
      // Smooth image loading
      imageEl.style.opacity = '0';
      imageEl.style.transform = 'scale(0.95)';
      
      if (imageSrc) {
        imageEl.src = imageSrc;
        imageEl.onload = function() {
          this.style.transition = 'all 0.5s ease';
          this.style.opacity = '1';
          this.style.transform = 'scale(1)';
        };
      }
      
      // Populate modal content
      document.getElementById('modalDishName').textContent = this.dataset.name;
      document.getElementById('modalDishCategory').textContent = this.dataset.category;
      document.getElementById('modalDishPrice').textContent = this.dataset.price;
      document.getElementById('modalDishDescription').textContent = this.dataset.description;
      document.getElementById('modalDishPrepTime').textContent = this.dataset.time + ' mins';

      // Toggle badges
      const vegBadge = document.getElementById('modalDishVegetarian');
      const spicyBadge = document.getElementById('modalDishSpicy');
      const availableBadge = document.getElementById('modalDishAvailable');
      
      vegBadge.classList.toggle('d-none', this.dataset.vegetarian !== 'True');
      spicyBadge.classList.toggle('d-none', this.dataset.spicy !== 'True');
      availableBadge.classList.toggle('d-none', this.dataset.instock !== 'False');
    });
  });
  
  // Enhanced smooth scroll for category navigation
  document.querySelectorAll('.category-pill').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        const offset = 90;
        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - offset;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
        
        // Flash highlight effect
        targetElement.style.transition = 'all 0.6s ease';
        targetElement.style.backgroundColor = 'rgba(220, 53, 69, 0.05)';
        targetElement.style.transform = 'scale(1.01)';
        
        setTimeout(() => {
          targetElement.style.backgroundColor = '';
          targetElement.style.transform = '';
        }, 1200);
      }
    });
  });
  
  // Parallax effect for hero section
  let lastScrollY = 0;
  let ticking = false;
  
  function updateParallax() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.menu-hero-section');
    
    if (hero && scrolled < 600) {
      const heroContent = hero.querySelector('.hero-content');
      if (heroContent) {
        heroContent.style.transform = `translateY(${scrolled * 0.4}px)`;
        heroContent.style.opacity = Math.max(0, 1 - (scrolled / 500));
      }
    }
    
    ticking = false;
  }
  
  window.addEventListener('scroll', function() {
    lastScrollY = window.pageYOffset;
    
    if (!ticking) {
      window.requestAnimationFrame(updateParallax);
      ticking = true;
    }
  });
  
  // Intersection Observer for staggered card animations
  const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, index * 50);
        cardObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -80px 0px'
  });
  
  document.querySelectorAll('.menu-card-enhanced').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(40px)';
    card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    cardObserver.observe(card);
  });
  
  // Category section observer
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        
        // Animate category line
        const line = entry.target.querySelector('.category-line');
        if (line) {
          line.style.animation = 'lineExpand 0.8s ease-out';
        }
      }
    });
  }, { threshold: 0.2 });
  
  document.querySelectorAll('.category-section').forEach(section => {
    sectionObserver.observe(section);
  });
  
  // Add ripple effect to buttons
  function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    const existingRipple = button.querySelector('.ripple');
    if (existingRipple) {
      existingRipple.remove();
    }
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  }
  
  document.querySelectorAll('.btn-brand-gradient, .view-details-btn, .quick-view-enhanced').forEach(button => {
    button.addEventListener('click', createRipple);
  });
  
  // Enhanced modal animations
  const dishModal = document.getElementById('dishModal');
  if (dishModal) {
    dishModal.addEventListener('show.bs.modal', function() {
      this.querySelector('.modal-content').style.transform = 'scale(0.9)';
      this.querySelector('.modal-content').style.opacity = '0';
    });
    
    dishModal.addEventListener('shown.bs.modal', function() {
      this.querySelector('.modal-content').style.transition = 'all 0.3s ease';
      this.querySelector('.modal-content').style.transform = 'scale(1)';
      this.querySelector('.modal-content').style.opacity = '1';
    });
    
    dishModal.addEventListener('hide.bs.modal', function() {
      this.querySelector('.modal-content').style.transform = 'scale(0.9)';
      this.querySelector('.modal-content').style.opacity = '0';
    });
  }
  
  // Counter animation for category badges
  function animateCounter(element, target) {
    let current = 0;
    const increment = target / 40;
    const duration = 1000;
    const stepTime = duration / 40;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        element.textContent = target;
        clearInterval(timer);
      } else {
        element.textContent = Math.floor(current);
      }
    }, stepTime);
  }
  
  const badgeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const badge = entry.target.querySelector('.badge-number');
        if (badge && !badge.classList.contains('animated')) {
          const target = parseInt(badge.textContent);
          badge.classList.add('animated');
          animateCounter(badge, target);
        }
        badgeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  
  document.querySelectorAll('.items-badge').forEach(badge => {
    badgeObserver.observe(badge.parentElement);
  });
});

// Add ripple and modal animation styles
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
  }
  
  @keyframes ripple-animation {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
  
  .modal.fade .modal-dialog {
    transition: transform 0.3s ease-out, opacity 0.3s ease-out;
  }
`;
document.head.appendChild(styleSheet);
