// Details modal population
document.querySelectorAll('.details-btn').forEach(function(btn){
    btn.addEventListener('click', function(){
        var name = this.dataset.name || '';
        var image = this.dataset.image || '';
        var description = this.dataset.description || '';

        document.getElementById('dishDetailsTitle').innerText = name;
        var imgEl = document.getElementById('dishDetailsImage');
        if(image) {
            imgEl.src = image;
            imgEl.style.display = 'block';
        } else {
            imgEl.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800';
        }
        document.getElementById('dishDetailsDescription').innerText = description;

        var modal = new bootstrap.Modal(document.getElementById('dishDetailsModal'));
        modal.show();
    });
});


function copyPhone() {
    const phone = "+9779845910341";
    navigator.clipboard.writeText(phone);

    const status = document.getElementById("copy-status");
    status.style.display = "inline";
    setTimeout(() => { status.style.display = "none"; }, 2000);
}

// testimoibials


/**
 * ZORPIDO TESTIMONIALS - JavaScript
 * Single Slide Auto-Animation with Smooth Transitions
 */

/**
 * ZORPIDO TESTIMONIALS - ENHANCED JAVASCRIPT
 * Advanced Auto-Animation with Smooth Transitions & Performance Optimization
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    autoPlayInterval: 6000,
    transitionDuration: 900,
    pauseOnHover: true,
    easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    progressUpdateInterval: 16 // ~60fps
  };

  let currentIndex = 0;
  let autoPlayTimer = null;
  let progressInterval = null;
  let isTransitioning = false;
  let isPaused = false;
  let progressStartTime = null;

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /**
   * Initialize the testimonial slider
   */
  function init() {
    const slider = document.querySelector('.testimonial-slider');
    if (!slider) return;

    const slides = document.querySelectorAll('.testimonial-slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const progressFill = document.querySelector('.progress-fill');

    if (slides.length === 0) return;

    // Setup event listeners
    setupControls(slides, dots, prevBtn, nextBtn);
    
    // Setup hover pause
    if (CONFIG.pauseOnHover) {
      setupHoverPause(slider);
    }

    // Add ripple effects to buttons
    addRippleEffects();

    // Optimize for performance
    optimizePerformance();

    // Start auto-play
    startAutoPlay(slides, dots, progressFill);

    // Add entrance animation
    animateEntrance();

    // Add intersection observer for visibility
    setupVisibilityObserver(slides, dots, progressFill);

    console.log('%c🎉 Zorpido Testimonials Enhanced - Activated!', 
      'color: #DC2626; font-size: 16px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);');
  }

  /**
   * Setup navigation controls
   */
  function setupControls(slides, dots, prevBtn, nextBtn) {
    // Previous button
    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        if (isTransitioning) return;
        createClickEffect(e, prevBtn);
        goToSlide(currentIndex - 1, slides, dots);
        resetAutoPlay(slides, dots);
      });
    }

    // Next button
    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        if (isTransitioning) return;
        createClickEffect(e, nextBtn);
        goToSlide(currentIndex + 1, slides, dots);
        resetAutoPlay(slides, dots);
      });
    }

    // Dot navigation
    dots.forEach((dot, index) => {
      dot.addEventListener('click', (e) => {
        if (isTransitioning || index === currentIndex) return;
        createClickEffect(e, dot);
        goToSlide(index, slides, dots);
        resetAutoPlay(slides, dots);
      });

      // Add hover effect
      dot.addEventListener('mouseenter', function() {
        if (index !== currentIndex) {
          this.style.transform = 'scale(1.3)';
        }
      });

      dot.addEventListener('mouseleave', function() {
        if (index !== currentIndex) {
          this.style.transform = 'scale(1)';
        }
      });
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        if (isTransitioning) return;
        goToSlide(currentIndex - 1, slides, dots);
        resetAutoPlay(slides, dots);
      } else if (e.key === 'ArrowRight') {
        if (isTransitioning) return;
        goToSlide(currentIndex + 1, slides, dots);
        resetAutoPlay(slides, dots);
      }
    });

    // Touch/Swipe support
    setupTouchControls(slides, dots);
  }

  /**
   * Create click ripple effect
   */
  function createClickEffect(e, element) {
    const ripple = element.querySelector('.btn-ripple') || element.querySelector('.dot-inner');
    if (ripple) {
      ripple.style.animation = 'none';
      void ripple.offsetWidth; // Force reflow
      ripple.style.animation = 'rippleEffect 0.6s ease';
    }
  }

  /**
   * Setup touch/swipe controls for mobile
   */
  function setupTouchControls(slides, dots) {
    const slider = document.querySelector('.testimonial-slider');
    if (!slider) return;

    let touchStartX = 0;
    let touchEndX = 0;
    let touchStartY = 0;
    let touchEndY = 0;

    slider.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    slider.addEventListener('touchmove', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      touchEndY = e.changedTouches[0].screenY;
    }, { passive: true });

    slider.addEventListener('touchend', (e) => {
      handleSwipe(slides, dots);
    }, { passive: true });

    function handleSwipe(slides, dots) {
      const swipeThreshold = 75;
      const diffX = touchStartX - touchEndX;
      const diffY = Math.abs(touchStartY - touchEndY);

      // Only trigger if horizontal swipe is dominant
      if (Math.abs(diffX) > swipeThreshold && Math.abs(diffX) > diffY * 2) {
        if (diffX > 0) {
          // Swiped left - next
          goToSlide(currentIndex + 1, slides, dots);
        } else {
          // Swiped right - previous
          goToSlide(currentIndex - 1, slides, dots);
        }
        resetAutoPlay(slides, dots);
      }
    }
  }

  /**
   * Go to specific slide with enhanced animation
   */
  function goToSlide(index, slides, dots) {
    if (isTransitioning) return;

    const newIndex = (index + slides.length) % slides.length;
    
    if (newIndex === currentIndex) return;

    isTransitioning = true;

    const currentSlide = slides[currentIndex];
    const nextSlide = slides[newIndex];
    const direction = newIndex > currentIndex ? 'next' : 'prev';

    // Animate transition
    animateSlideTransition(currentSlide, nextSlide, direction, () => {
      currentIndex = newIndex;
      updateDots(dots);
      isTransitioning = false;
      announceSlideChange(currentIndex + 1, slides.length);
    });
  }

  /**
   * Animate slide transition with enhanced effects
   */
  function animateSlideTransition(currentSlide, nextSlide, direction, callback) {
    // Prepare next slide
    nextSlide.style.transition = 'none';
    nextSlide.style.filter = 'blur(8px)';
    
    if (direction === 'next') {
      nextSlide.style.transform = 'translateX(150px) scale(0.9)';
    } else {
      nextSlide.style.transform = 'translateX(-150px) scale(0.9)';
    }
    
    nextSlide.style.opacity = '0';
    nextSlide.classList.remove('exit-left');
    nextSlide.classList.add('active');

    // Force reflow
    void nextSlide.offsetWidth;

    // Apply transition
    nextSlide.style.transition = `all ${CONFIG.transitionDuration}ms ${CONFIG.easing}`;

    // Animate in
    requestAnimationFrame(() => {
      nextSlide.style.transform = 'translateX(0) scale(1)';
      nextSlide.style.opacity = '1';
      nextSlide.style.filter = 'blur(0)';

      // Animate out current slide
      currentSlide.style.filter = 'blur(8px)';
      
      if (direction === 'next') {
        currentSlide.style.transform = 'translateX(-150px) scale(0.9)';
      } else {
        currentSlide.style.transform = 'translateX(150px) scale(0.9)';
      }
      
      currentSlide.style.opacity = '0';
    });

    // Clean up
    setTimeout(() => {
      currentSlide.classList.remove('active');
      currentSlide.classList.add('exit-left');
      currentSlide.style.transition = '';
      nextSlide.style.transition = '';
      
      if (callback) callback();
    }, CONFIG.transitionDuration);
  }

  /**
   * Update active dot with smooth animation
   */
  function updateDots(dots) {
    dots.forEach((dot, index) => {
      const inner = dot.querySelector('.dot-inner');
      
      if (index === currentIndex) {
        dot.classList.add('active');
        if (inner) {
          inner.style.transform = 'scale(1)';
        }
      } else {
        dot.classList.remove('active');
        if (inner) {
          inner.style.transform = 'scale(0)';
        }
      }
    });
  }

  /**
   * Start auto-play with smooth progress
   */
  function startAutoPlay(slides, dots, progressFill) {
    if (slides.length <= 1 || isPaused) return;

    progressStartTime = Date.now();
    startSmoothProgress(progressFill);

    autoPlayTimer = setTimeout(() => {
      if (!isPaused) {
        goToSlide(currentIndex + 1, slides, dots);
        startAutoPlay(slides, dots, progressFill);
      }
    }, CONFIG.autoPlayInterval);
  }

  /**
   * Smooth progress bar animation
   */
  function startSmoothProgress(progressFill) {
    if (!progressFill || isPaused) return;

    stopProgressAnimation();

    let startWidth = 0;
    progressFill.style.width = '0%';

    progressInterval = setInterval(() => {
      if (isPaused) return;

      const elapsed = Date.now() - progressStartTime;
      const progress = Math.min((elapsed / CONFIG.autoPlayInterval) * 100, 100);
      
      progressFill.style.width = `${progress}%`;

      if (progress >= 100) {
        stopProgressAnimation();
      }
    }, CONFIG.progressUpdateInterval);
  }

  /**
   * Stop progress animation
   */
  function stopProgressAnimation() {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
  }

  /**
   * Stop auto-play
   */
  function stopAutoPlay() {
    if (autoPlayTimer) {
      clearTimeout(autoPlayTimer);
      autoPlayTimer = null;
    }
    stopProgressAnimation();
  }

  /**
   * Reset auto-play
   */
  function resetAutoPlay(slides, dots) {
    stopAutoPlay();
    const progressFill = document.querySelector('.progress-fill');
    
    // Small delay before restarting
    setTimeout(() => {
      startAutoPlay(slides, dots, progressFill);
    }, 100);
  }

  /**
   * Setup hover pause with smooth transitions
   */
  function setupHoverPause(slider) {
    const progressFill = document.querySelector('.progress-fill');
    let pausedProgress = 0;

    slider.addEventListener('mouseenter', () => {
      isPaused = true;
      
      if (progressFill) {
        pausedProgress = parseFloat(progressFill.style.width) || 0;
      }
      
      stopAutoPlay();
    });

    slider.addEventListener('mouseleave', () => {
      isPaused = false;
      
      const slides = document.querySelectorAll('.testimonial-slide');
      const dots = document.querySelectorAll('.dot');
      
      // Adjust remaining time based on paused progress
      const remainingTime = CONFIG.autoPlayInterval * (1 - pausedProgress / 100);
      progressStartTime = Date.now() - (CONFIG.autoPlayInterval - remainingTime);
      
      startAutoPlay(slides, dots, progressFill);
    });
  }

  /**
   * Add ripple effects to interactive elements
   */
  function addRippleEffects() {
    const buttons = document.querySelectorAll('.control-btn');
    
    buttons.forEach(button => {
      button.addEventListener('mousedown', function(e) {
        const ripple = this.querySelector('.btn-ripple');
        if (ripple) {
          ripple.style.animation = 'none';
          void ripple.offsetWidth;
          ripple.style.animation = 'rippleEffect 0.6s ease';
        }
      });
    });
  }

  /**
   * Optimize performance
   */
  function optimizePerformance() {
    // Use will-change for better performance
    const slides = document.querySelectorAll('.testimonial-slide');
    slides.forEach(slide => {
      slide.style.willChange = 'transform, opacity';
    });

    // Cleanup will-change after transitions
    setTimeout(() => {
      slides.forEach(slide => {
        slide.style.willChange = 'auto';
      });
    }, 2000);
  }

  /**
   * Animate entrance of testimonial section
   */
  function animateEntrance() {
    const section = document.querySelector('.zorpido-testimonials');
    if (!section) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          section.style.opacity = '0';
          section.style.transform = 'translateY(50px)';
          
          requestAnimationFrame(() => {
            section.style.transition = 'all 1s cubic-bezier(0.34, 1.56, 0.64, 1)';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
          });

          // Animate floating quotes with stagger
          const quotes = document.querySelectorAll('.quote-float');
          quotes.forEach((quote, index) => {
            setTimeout(() => {
              quote.style.opacity = '0';
              quote.style.transform = 'scale(0.5) rotate(-30deg)';
              quote.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
              
              requestAnimationFrame(() => {
                quote.style.opacity = '0.12';
                quote.style.transform = 'scale(1) rotate(0deg)';
              });
            }, index * 150);
          });

          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px'
    });

    observer.observe(section);
  }

  /**
   * Setup visibility observer for pause on hidden
   */
  function setupVisibilityObserver(slides, dots, progressFill) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) {
          isPaused = true;
          stopAutoPlay();
        } else if (!isPaused) {
          startAutoPlay(slides, dots, progressFill);
        }
      });
    }, {
      threshold: 0.1
    });

    const section = document.querySelector('.zorpido-testimonials');
    if (section) {
      observer.observe(section);
    }
  }

  /**
   * Announce slide changes for accessibility
   */
  function announceSlideChange(slideNumber, totalSlides) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';
    announcement.textContent = `Showing testimonial ${slideNumber} of ${totalSlides}`;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      if (announcement.parentNode) {
        document.body.removeChild(announcement);
      }
    }, 1000);
  }

  /**
   * Handle visibility change
   */
  document.addEventListener('visibilitychange', () => {
    const slides = document.querySelectorAll('.testimonial-slide');
    const dots = document.querySelectorAll('.dot');
    const progressFill = document.querySelector('.progress-fill');

    if (document.hidden) {
      isPaused = true;
      stopAutoPlay();
    } else {
      isPaused = false;
      if (slides.length > 1) {
        startAutoPlay(slides, dots, progressFill);
      }
    }
  });

  /**
   * Smooth scroll to testimonials
   */
  window.scrollToTestimonials = function() {
    const section = document.querySelector('.zorpido-testimonials');
    if (section) {
      section.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
    }
  };

  /**
   * Public API with enhanced methods
   */
  window.ZorpidoTestimonials = {
    next: function() {
      const slides = document.querySelectorAll('.testimonial-slide');
      const dots = document.querySelectorAll('.dot');
      goToSlide(currentIndex + 1, slides, dots);
      resetAutoPlay(slides, dots);
    },
    prev: function() {
      const slides = document.querySelectorAll('.testimonial-slide');
      const dots = document.querySelectorAll('.dot');
      goToSlide(currentIndex - 1, slides, dots);
      resetAutoPlay(slides, dots);
    },
    goTo: function(index) {
      const slides = document.querySelectorAll('.testimonial-slide');
      const dots = document.querySelectorAll('.dot');
      if (index >= 0 && index < slides.length) {
        goToSlide(index, slides, dots);
        resetAutoPlay(slides, dots);
      }
    },
    pause: function() {
      isPaused = true;
      stopAutoPlay();
    },
    play: function() {
      isPaused = false;
      const slides = document.querySelectorAll('.testimonial-slide');
      const dots = document.querySelectorAll('.dot');
      const progressFill = document.querySelector('.progress-fill');
      startAutoPlay(slides, dots, progressFill);
    },
    getCurrentIndex: function() {
      return currentIndex;
    },
    getTotalSlides: function() {
      return document.querySelectorAll('.testimonial-slide').length;
    }
  };

})();



// featured gallery section
/**
 * ZORPIDO FEATURED SLIDER - JavaScript
 * Enhanced Image Gallery with Advanced Features
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    autoPlayInterval: 5000,
    transitionDuration: 800,
    pauseOnHover: true,
    enableKeyboard: true,
    enableTouch: true,
    enableFullscreen: true
  };

  let currentIndex = 0;
  let autoPlayTimer = null;
  let isTransitioning = false;
  let isAutoPlaying = true;

  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /**
   * Initialize the featured slider
   */
  function init() {
    const carousel = document.querySelector('.zorpido-carousel');
    if (!carousel) return;

    const slides = document.querySelectorAll('.carousel-slide');
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    const progressDots = document.querySelectorAll('.progress-dot');
    const prevBtn = document.querySelector('.arrow-prev');
    const nextBtn = document.querySelector('.arrow-next');
    const autoplayBtn = document.querySelector('.autoplay-toggle');
    const images = document.querySelectorAll('.image-container');

    if (slides.length === 0) return;

    // Setup controls
    setupNavigation(slides, thumbnails, progressDots, prevBtn, nextBtn);
    setupAutoplay(slides, thumbnails, progressDots, autoplayBtn);
    setupFullscreen(slides, images);
    
    if (CONFIG.enableKeyboard) setupKeyboard(slides, thumbnails, progressDots);
    if (CONFIG.enableTouch) setupTouch(carousel, slides, thumbnails, progressDots);
    if (CONFIG.pauseOnHover) setupHoverPause(carousel);

    // Update counter
    updateCounter(slides.length);

    // Start autoplay
    if (isAutoPlaying) {
      startAutoPlay(slides, thumbnails, progressDots);
    }

    console.log('%c🎨 Zorpido Featured Slider Activated!', 
      'color: #DC2626; font-size: 14px; font-weight: bold;');
  }

  /**
   * Setup navigation controls
   */
  function setupNavigation(slides, thumbnails, progressDots, prevBtn, nextBtn) {
    // Previous button
    prevBtn?.addEventListener('click', () => {
      if (isTransitioning) return;
      goToSlide(currentIndex - 1, slides, thumbnails, progressDots);
      resetAutoPlay(slides, thumbnails, progressDots);
    });

    // Next button
    nextBtn?.addEventListener('click', () => {
      if (isTransitioning) return;
      goToSlide(currentIndex + 1, slides, thumbnails, progressDots);
      resetAutoPlay(slides, thumbnails, progressDots);
    });

    // Thumbnail clicks
    thumbnails.forEach((thumb, index) => {
      thumb.addEventListener('click', () => {
        if (isTransitioning || index === currentIndex) return;
        goToSlide(index, slides, thumbnails, progressDots);
        resetAutoPlay(slides, thumbnails, progressDots);
      });
    });

    // Progress dot clicks
    progressDots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        if (isTransitioning || index === currentIndex) return;
        goToSlide(index, slides, thumbnails, progressDots);
        resetAutoPlay(slides, thumbnails, progressDots);
      });
    });
  }

  /**
   * Go to specific slide
   */
  function goToSlide(index, slides, thumbnails, progressDots) {
    if (isTransitioning) return;

    const newIndex = (index + slides.length) % slides.length;
    if (newIndex === currentIndex) return;

    isTransitioning = true;

    const currentSlide = slides[currentIndex];
    const nextSlide = slides[newIndex];

    // Animate transition
    currentSlide.classList.add('exit');
    nextSlide.classList.add('active');

    setTimeout(() => {
      currentSlide.classList.remove('active', 'exit');
      currentIndex = newIndex;
      updateUI(thumbnails, progressDots, slides.length);
      isTransitioning = false;
    }, CONFIG.transitionDuration);
  }

  /**
   * Update UI elements
   */
  function updateUI(thumbnails, progressDots, totalSlides) {
    // Update thumbnails
    thumbnails.forEach((thumb, index) => {
      thumb.classList.toggle('active', index === currentIndex);
    });

    // Update progress dots
    progressDots.forEach((dot, index) => {
      dot.classList.toggle('active', index === currentIndex);
    });

    // Update counter
    updateCounter(totalSlides);

    // Scroll active thumbnail into view (horizontal scroll only to avoid vertical jumps)
    const activeThumbnail = thumbnails[currentIndex];
    if (activeThumbnail) {
      try {
        const track = activeThumbnail.closest('.thumbnail-track');
        if (track) {
          // Calculate center offset and scroll the track horizontally
          const trackRect = track.getBoundingClientRect();
          const thumbRect = activeThumbnail.getBoundingClientRect();
          const trackCenter = trackRect.left + (trackRect.width / 2);
          const thumbCenter = thumbRect.left + (thumbRect.width / 2);
          const offset = thumbCenter - trackCenter;
          track.scrollBy({ left: offset, behavior: 'smooth' });
        } else {
          // Fallback: use scrollIntoView with nearest block to minimize vertical movement
          activeThumbnail.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
      } catch (e) {
        // If anything goes wrong, fallback gracefully
        activeThumbnail.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }

  /**
   * Update slide counter
   */
  function updateCounter(total) {
    const currentEl = document.querySelector('.current-slide');
    const totalEl = document.querySelector('.total-slides');
    
    if (currentEl) currentEl.textContent = currentIndex + 1;
    if (totalEl) totalEl.textContent = total;
  }

  /**
   * Setup autoplay
   */
  function setupAutoplay(slides, thumbnails, progressDots, autoplayBtn) {
    if (!autoplayBtn) return;

    autoplayBtn.addEventListener('click', () => {
      isAutoPlaying = !isAutoPlaying;
      autoplayBtn.classList.toggle('active', isAutoPlaying);

      if (isAutoPlaying) {
        startAutoPlay(slides, thumbnails, progressDots);
      } else {
        stopAutoPlay();
      }
    });
  }

  /**
   * Start autoplay
   */
  function startAutoPlay(slides, thumbnails, progressDots) {
    if (slides.length <= 1) return;

    stopAutoPlay();
    autoPlayTimer = setInterval(() => {
      goToSlide(currentIndex + 1, slides, thumbnails, progressDots);
    }, CONFIG.autoPlayInterval);
  }

  /**
   * Stop autoplay
   */
  function stopAutoPlay() {
    if (autoPlayTimer) {
      clearInterval(autoPlayTimer);
      autoPlayTimer = null;
    }
  }

  /**
   * Reset autoplay
   */
  function resetAutoPlay(slides, thumbnails, progressDots) {
    if (isAutoPlaying) {
      startAutoPlay(slides, thumbnails, progressDots);
    }
  }

  /**
   * Setup hover pause
   */
  function setupHoverPause(carousel) {
    carousel.addEventListener('mouseenter', () => {
      stopAutoPlay();
    });

    carousel.addEventListener('mouseleave', () => {
      if (isAutoPlaying) {
        const slides = document.querySelectorAll('.carousel-slide');
        const thumbnails = document.querySelectorAll('.thumbnail-item');
        const progressDots = document.querySelectorAll('.progress-dot');
        startAutoPlay(slides, thumbnails, progressDots);
      }
    });
  }

  /**
   * Setup keyboard navigation
   */
  function setupKeyboard(slides, thumbnails, progressDots) {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        goToSlide(currentIndex - 1, slides, thumbnails, progressDots);
        resetAutoPlay(slides, thumbnails, progressDots);
      } else if (e.key === 'ArrowRight') {
        goToSlide(currentIndex + 1, slides, thumbnails, progressDots);
        resetAutoPlay(slides, thumbnails, progressDots);
      } else if (e.key === 'Escape') {
        closeFullscreen();
      }
    });
  }

  /**
   * Setup touch/swipe controls
   */
  function setupTouch(carousel, slides, thumbnails, progressDots) {
    let touchStartX = 0;
    let touchEndX = 0;
    let touchStartY = 0;
    let touchEndY = 0;

    carousel.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    carousel.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      touchEndY = e.changedTouches[0].screenY;
      handleSwipe(slides, thumbnails, progressDots);
    }, { passive: true });

    function handleSwipe(slides, thumbnails, progressDots) {
      const swipeThreshold = 50;
      const diffX = touchStartX - touchEndX;
      const diffY = Math.abs(touchStartY - touchEndY);

      // Only register horizontal swipes
      if (diffY < swipeThreshold && Math.abs(diffX) > swipeThreshold) {
        if (diffX > 0) {
          // Swiped left - next
          goToSlide(currentIndex + 1, slides, thumbnails, progressDots);
        } else {
          // Swiped right - previous
          goToSlide(currentIndex - 1, slides, thumbnails, progressDots);
        }
        resetAutoPlay(slides, thumbnails, progressDots);
      }
    }
  }

  /**
   * Setup fullscreen functionality
   */
  function setupFullscreen(slides, images) {
    if (!CONFIG.enableFullscreen) return;

    const modal = document.getElementById('fullscreenModal');
    const modalImage = document.getElementById('fullscreenImage');
    const closeBtn = modal?.querySelector('.modal-close');
    const modalPrev = modal?.querySelector('.modal-prev');
    const modalNext = modal?.querySelector('.modal-next');

    if (!modal || !modalImage) return;

    // Click image to open fullscreen
    images.forEach((imageContainer, index) => {
      imageContainer.addEventListener('click', () => {
        const img = imageContainer.querySelector('.featured-image');
        if (img) {
          openFullscreen(img.src, img.alt);
        }
      });
    });

    // Close button
    closeBtn?.addEventListener('click', closeFullscreen);

    // Click outside to close
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeFullscreen();
      }
    });

    // Modal navigation
    modalPrev?.addEventListener('click', () => {
      navigateFullscreen(-1, slides);
    });

    modalNext?.addEventListener('click', () => {
      navigateFullscreen(1, slides);
    });

    function openFullscreen(src, alt) {
      modalImage.src = src;
      modalImage.alt = alt;
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }

    function navigateFullscreen(direction, slides) {
      const newIndex = (currentIndex + direction + slides.length) % slides.length;
      const newSlide = slides[newIndex];
      const newImage = newSlide.querySelector('.featured-image');
      
      if (newImage) {
        modalImage.style.opacity = '0';
        setTimeout(() => {
          modalImage.src = newImage.src;
          modalImage.alt = newImage.alt;
          modalImage.style.opacity = '1';
        }, 200);
      }
    }
  }

  /**
   * Close fullscreen modal
   */
  function closeFullscreen() {
    const modal = document.getElementById('fullscreenModal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  /**
   * Handle visibility change
   */
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stopAutoPlay();
    } else if (isAutoPlaying) {
      const slides = document.querySelectorAll('.carousel-slide');
      const thumbnails = document.querySelectorAll('.thumbnail-item');
      const progressDots = document.querySelectorAll('.progress-dot');
      startAutoPlay(slides, thumbnails, progressDots);
    }
  });

  /**
   * Lazy load images
   */
  function lazyLoadImages() {
    const images = document.querySelectorAll('.featured-image[data-src]');
    
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
          }
        });
      });

      images.forEach(img => imageObserver.observe(img));
    } else {
      // Fallback for older browsers
      images.forEach(img => {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      });
    }
  }

  /**
   * Add entrance animations
   */
  function addEntranceAnimation() {
    const slider = document.querySelector('.zorpido-featured-slider');
    if (!slider) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          slider.style.opacity = '0';
          slider.style.transform = 'translateY(40px)';
          
          requestAnimationFrame(() => {
            slider.style.transition = 'all 0.8s ease-out';
            slider.style.opacity = '1';
            slider.style.transform = 'translateY(0)';
          });

          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    observer.observe(slider);
  }

  // Initialize additional features
  lazyLoadImages();
  addEntranceAnimation();

  /**
   * Public API
   */
  window.ZorpidoFeaturedSlider = {
    next: function() {
      const slides = document.querySelectorAll('.carousel-slide');
      const thumbnails = document.querySelectorAll('.thumbnail-item');
      const progressDots = document.querySelectorAll('.progress-dot');
      goToSlide(currentIndex + 1, slides, thumbnails, progressDots);
      resetAutoPlay(slides, thumbnails, progressDots);
    },
    prev: function() {
      const slides = document.querySelectorAll('.carousel-slide');
      const thumbnails = document.querySelectorAll('.thumbnail-item');
      const progressDots = document.querySelectorAll('.progress-dot');
      goToSlide(currentIndex - 1, slides, thumbnails, progressDots);
      resetAutoPlay(slides, thumbnails, progressDots);
    },
    goTo: function(index) {
      const slides = document.querySelectorAll('.carousel-slide');
      const thumbnails = document.querySelectorAll('.thumbnail-item');
      const progressDots = document.querySelectorAll('.progress-dot');
      goToSlide(index, slides, thumbnails, progressDots);
      resetAutoPlay(slides, thumbnails, progressDots);
    },
    pause: function() {
      isAutoPlaying = false;
      stopAutoPlay();
      const btn = document.querySelector('.autoplay-toggle');
      if (btn) btn.classList.remove('active');
    },
    play: function() {
      isAutoPlaying = true;
      const slides = document.querySelectorAll('.carousel-slide');
      const thumbnails = document.querySelectorAll('.thumbnail-item');
      const progressDots = document.querySelectorAll('.progress-dot');
      startAutoPlay(slides, thumbnails, progressDots);
      const btn = document.querySelector('.autoplay-toggle');
      if (btn) btn.classList.add('active');
    },
    getCurrentIndex: function() {
      return currentIndex;
    }
  };

})();




// why choose us section 
// (function() {
//   'use strict';
//   if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', init);
//   } else {
//     init();
//   }
//   function init() {
//     const section = document.querySelector('.zorpido-why-choose');
//     if (!section) return;

//     initScrollAnimations();
    
//     initCardInteractions();
    
//     initStatsCounter();
    
//     initParallaxEffect();
    
//     initCardTilt();
    
//     initEntranceAnimation();

//     console.log('%c🌟 Zorpido Why Choose Section Activated!', 
//       'color: #DC2626; font-size: 14px; font-weight: bold;');
//   }
//   function initScrollAnimations() {
//     if (typeof AOS !== 'undefined') {
//       AOS.init({
//         duration: 600,
//         easing: 'ease-out-cubic',
//         once: true,
//         offset: 100
//       });
//     } else {
//       const cards = document.querySelectorAll('.feature-card');
      
//       if ('IntersectionObserver' in window) {
//         const observer = new IntersectionObserver((entries) => {
//           entries.forEach(entry => {
//             if (entry.isIntersecting) {
//               entry.target.style.opacity = '1';
//               entry.target.style.transform = 'translateY(0)';
//             }
//           });
//         }, {
//           threshold: 0.1,
//           rootMargin: '0px 0px -50px 0px'
//         });

//         cards.forEach((card, index) => {
//           card.style.opacity = '0';
//           card.style.transform = 'translateY(50px)';
//           card.style.transition = `all 0.6s ease ${index * 0.1}s`;
//           observer.observe(card);
//         });
//       }
//     }
//   }
//   function initCardInteractions() {
//     const cards = document.querySelectorAll('.feature-card');
    
//     cards.forEach(card => {
//       card.addEventListener('click', function(e) {
//         createRipple(e, this);
//       });

//       card.addEventListener('mouseenter', function() {
//         this.style.zIndex = '10';
//       });

//       card.addEventListener('mouseleave', function() {
//         this.style.zIndex = '1';
//       });
//     });
//   }
//   function createRipple(event, element) {
//     const card = element.querySelector('.card-inner');
//     const ripple = document.createElement('span');
//     const rect = card.getBoundingClientRect();
//     const size = Math.max(rect.width, rect.height);
//     const x = event.clientX - rect.left - size / 2;
//     const y = event.clientY - rect.top - size / 2;

//     ripple.style.width = ripple.style.height = size + 'px';
//     ripple.style.left = x + 'px';
//     ripple.style.top = y + 'px';
//     ripple.style.position = 'absolute';
//     ripple.style.borderRadius = '50%';
//     ripple.style.background = 'rgba(220, 38, 38, 0.3)';
//     ripple.style.transform = 'scale(0)';
//     ripple.style.animation = 'ripple-effect 0.6s ease-out';
//     ripple.style.pointerEvents = 'none';

//     const style = document.createElement('style');
//     style.textContent = `
//       @keyframes ripple-effect {
//         to {
//           transform: scale(2);
//           opacity: 0;
//         }
//       }
//     `;
//     if (!document.querySelector('style[data-ripple]')) {
//       style.setAttribute('data-ripple', 'true');
//       document.head.appendChild(style);
//     }

//     card.style.position = 'relative';
//     card.style.overflow = 'hidden';
//     card.appendChild(ripple);

//     setTimeout(() => {
//       ripple.remove();
//     }, 600);
//   }

//   function initStatsCounter() {
//     const stats = document.querySelectorAll('.stat-number');
    
//     const observer = new IntersectionObserver((entries) => {
//       entries.forEach(entry => {
//         if (entry.isIntersecting) {
//           const target = entry.target;
//           const text = target.textContent;
//           const hasPlus = text.includes('+');
//           const hasStar = text.includes('★');
//           const number = parseFloat(text.replace(/[^\d.]/g, ''));
          
//           animateCounter(target, 0, number, 2000, hasPlus, hasStar);
//           observer.unobserve(target);
//         }
//       });
//     }, { threshold: 0.5 });

//     stats.forEach(stat => observer.observe(stat));
//   }
//   function animateCounter(element, start, end, duration, hasPlus, hasStar) {
//     const startTime = performance.now();
    
//     function update(currentTime) {
//       const elapsed = currentTime - startTime;
//       const progress = Math.min(elapsed / duration, 1);
    
//       const easeOutQuad = progress * (2 - progress);
//       const current = start + (end - start) * easeOutQuad;
      
//       let displayValue = Math.floor(current);
      
//       if (end >= 1000) {
//         displayValue = (current / 1000).toFixed(1) + 'K';
//       } else if (hasStar) {
//         displayValue = current.toFixed(1);
//       }
      
//       element.textContent = displayValue + (hasPlus ? '+' : '') + (hasStar ? '★' : '');
      
//       if (progress < 1) {
//         requestAnimationFrame(update);
//       }
//     }
    
//     requestAnimationFrame(update);
//   }

//   function initParallaxEffect() {
//     const floatingElements = document.querySelectorAll('.float-element');
    
//     if (floatingElements.length === 0) return;

//     window.addEventListener('scroll', () => {
//       const scrolled = window.pageYOffset;
//       const section = document.querySelector('.zorpido-why-choose');
      
//       if (!section) return;
      
//       const sectionTop = section.offsetTop;
//       const sectionHeight = section.offsetHeight;
      
//       if (scrolled > sectionTop - window.innerHeight && 
//           scrolled < sectionTop + sectionHeight) {
        
//         floatingElements.forEach((element, index) => {
//           const speed = 0.5 + (index * 0.1);
//           const yPos = (scrolled - sectionTop) * speed;
//           element.style.transform = `translateY(${yPos}px)`;
//         });
//       }
//     }, { passive: true });
//   }
//   function initCardTilt() {
//     const cards = document.querySelectorAll('.feature-card');
    
//     cards.forEach(card => {
//       card.addEventListener('mousemove', function(e) {
//         const rect = this.getBoundingClientRect();
//         const x = e.clientX - rect.left;
//         const y = e.clientY - rect.top;
        
//         const centerX = rect.width / 2;
//         const centerY = rect.height / 2;
        
//         const rotateX = (y - centerY) / 15;
//         const rotateY = (centerX - x) / 15;
        
//         const cardInner = this.querySelector('.card-inner');
//         cardInner.style.transform = `
//           perspective(1000px) 
//           rotateX(${rotateX}deg) 
//           rotateY(${rotateY}deg) 
//           translateY(-10px)
//         `;
//       });
      
//       card.addEventListener('mouseleave', function() {
//         const cardInner = this.querySelector('.card-inner');
//         cardInner.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
//       });
//     });
//   }
//   function initEntranceAnimation() {
//     const section = document.querySelector('.zorpido-why-choose');
//     if (!section) return;

//     const observer = new IntersectionObserver((entries) => {
//       entries.forEach(entry => {
//         if (entry.isIntersecting) {
//           const headerBadge = section.querySelector('.header-badge');
//           const sectionTitle = section.querySelector('.section-title');
//           const sectionSubtitle = section.querySelector('.section-subtitle');
          
//           if (headerBadge) {
//             headerBadge.style.opacity = '0';
//             headerBadge.style.transform = 'scale(0) rotate(-180deg)';
            
//             setTimeout(() => {
//               headerBadge.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
//               headerBadge.style.opacity = '1';
//               headerBadge.style.transform = 'scale(1) rotate(0deg)';
//             }, 100);
//           }
          
//           if (sectionTitle) {
//             sectionTitle.style.opacity = '0';
//             sectionTitle.style.transform = 'translateY(30px)';
            
//             setTimeout(() => {
//               sectionTitle.style.transition = 'all 0.8s ease-out';
//               sectionTitle.style.opacity = '1';
//               sectionTitle.style.transform = 'translateY(0)';
//             }, 300);
//           }
          
//           if (sectionSubtitle) {
//             sectionSubtitle.style.opacity = '0';
//             sectionSubtitle.style.transform = 'translateY(30px)';
            
//             setTimeout(() => {
//               sectionSubtitle.style.transition = 'all 0.8s ease-out';
//               sectionSubtitle.style.opacity = '1';
//               sectionSubtitle.style.transform = 'translateY(0)';
//             }, 500);
//           }
          
//           observer.unobserve(entry.target);
//         }
//       });
//     }, { threshold: 0.2 });

//     observer.observe(section);
//   }
//   function initSmoothScroll() {
//     const ctaButtons = document.querySelectorAll('.btn-primary-cta, .btn-secondary-cta');
    
//     ctaButtons.forEach(button => {
//       button.addEventListener('click', function(e) {
//         const href = this.getAttribute('href');
        
//         if (href && href.startsWith('#')) {
//           e.preventDefault();
//           const target = document.querySelector(href);
          
//           if (target) {
//             target.scrollIntoView({
//               behavior: 'smooth',
//               block: 'start'
//             });
//           }
//         }
//       });
//     });
//   }
//   function initKeyboardNavigation() {
//     const cards = document.querySelectorAll('.feature-card');
//     let currentFocus = -1;

//     document.addEventListener('keydown', (e) => {
//       if (e.key === 'Tab') {
//         currentFocus = (currentFocus + 1) % cards.length;
//         cards[currentFocus]?.focus();
//       }
//     });

//     cards.forEach((card, index) => {
//       card.setAttribute('tabindex', '0');
      
//       card.addEventListener('keydown', (e) => {
//         if (e.key === 'Enter' || e.key === ' ') {
//           e.preventDefault();
//           card.click();
//         }
//       });
//     });
//   }
//   function monitorPerformance() {
//     if ('PerformanceObserver' in window) {
//       const observer = new PerformanceObserver((list) => {
//         for (const entry of list.getEntries()) {
//           if (entry.duration > 50) {
//             console.warn('Slow animation detected:', entry);
//           }
//         }
//       });
      
//       observer.observe({ entryTypes: ['measure'] });
//     }
//   }

//   initSmoothScroll();
//   initKeyboardNavigation();
//   monitorPerformance();

//   window.ZorpidoWhyChoose = {
//     animateCards: function() {
//       initScrollAnimations();
//     },
//     resetAnimations: function() {
//       const cards = document.querySelectorAll('.feature-card');
//       cards.forEach(card => {
//         card.style.opacity = '0';
//         card.style.transform = 'translateY(50px)';
//       });
//       initScrollAnimations();
//     },
//     highlightCard: function(index) {
//       const cards = document.querySelectorAll('.feature-card');
//       if (cards[index]) {
//         cards[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
//         cards[index].style.animation = 'pulse 1s ease-in-out';
//       }
//     }
//   };

//   let resizeTimer;
//   window.addEventListener('resize', () => {
//     clearTimeout(resizeTimer);
//     resizeTimer = setTimeout(() => {
//       console.log('Window resized - recalculating positions');
//     }, 250);
//   });

// })();






/**
 * ZORPIDO GALLERY SECTION - JavaScript
 * Enhanced Gallery with Modal Navigation
 */

(function() {
  'use strict';

  let currentImageIndex = 0;
  let totalImages = 0;
  let galleryImages = [];

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /**
   * Initialize gallery features
   */
  function init() {
    const gallerySection = document.querySelector('.zorpido-gallery-section');
    if (!gallerySection) return;

    // Initialize scroll animations
    initScrollAnimations();
    
    // Setup modal functionality
    setupModal();
    
    // Add hover effects
    addHoverEffects();
    
    // Setup keyboard navigation
    setupKeyboardNav();
    
    // Initialize lightbox features
    initLightbox();

    console.log('%c🖼️ Zorpido Gallery Activated!', 
      'color: #DC2626; font-size: 14px; font-weight: bold;');
  }

  /**
   * Initialize scroll animations
   */
  function initScrollAnimations() {
    // Check if AOS library is available
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 600,
        easing: 'ease-out-cubic',
        once: true,
        offset: 100
      });
    } else {
      // Fallback: Simple intersection observer
      const cards = document.querySelectorAll('.gallery-card');
      
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.style.opacity = '1';
              entry.target.style.transform = 'translateY(0)';
            }
          });
        }, {
          threshold: 0.1,
          rootMargin: '0px 0px -50px 0px'
        });

        cards.forEach((card, index) => {
          card.style.opacity = '0';
          card.style.transform = 'translateY(30px)';
          card.style.transition = `all 0.6s ease ${index * 0.05}s`;
          observer.observe(card);
        });
      }
    }
  }

  /**
   * Setup modal functionality
   */
  function setupModal() {
    const modal = document.getElementById('galleryModal');
    if (!modal) return;

  // Scope queries to the gallery section/modal to avoid picking up
  // similarly-named elements from other sliders (e.g. featured slider).
  const imageContainers = gallerySection.querySelectorAll('.image-container');
  const modalImage = document.getElementById('galleryModalImage');
  const modalTitle = document.getElementById('galleryModalTitle');
  const currentImageEl = document.getElementById('currentImage');
  const totalImagesEl = document.getElementById('totalImages');
  const prevBtn = document.getElementById('modalPrev');
  const nextBtn = document.getElementById('modalNext');
  // Thumbnails inside the modal's thumbnail nav (scope to modal)
  const thumbnails = modal.querySelectorAll('.thumbnail-item');

    // Collect all image data (include server id when available)
    galleryImages = Array.from(imageContainers).map(container => ({
      url: container.dataset.image,
      title: container.dataset.title || 'Untitled',
      id: container.dataset.id ? parseInt(container.dataset.id) : null,
      index: parseInt(container.dataset.index)
    }));

    totalImages = galleryImages.length;
    if (totalImagesEl) totalImagesEl.textContent = totalImages;

    // Open modal on image click
    imageContainers.forEach((container) => {
      container.addEventListener('click', function() {
        currentImageIndex = parseInt(this.dataset.index);
        updateModalImage();
      });
    });

    // Navigation buttons
    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateImage(-1);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateImage(1);
      });
    }

    // Thumbnail navigation
    thumbnails.forEach((thumb) => {
      thumb.addEventListener('click', function() {
        currentImageIndex = parseInt(this.dataset.index);
        updateModalImage();
      });
    });

    // Action buttons
    setupActionButtons();

    // Swipe support for mobile
    setupTouchNavigation(modal);
  }

  /**
   * Update modal image
   */
  function updateModalImage() {
    const modalImage = document.getElementById('galleryModalImage');
    const modalTitle = document.getElementById('galleryModalTitle');
    const currentImageEl = document.getElementById('currentImage');
    const loader = document.querySelector('.image-loader');
    const thumbnails = document.querySelectorAll('.thumbnail-item');

    if (!galleryImages[currentImageIndex]) return;

    const imageData = galleryImages[currentImageIndex];

    // Show loader and hide current image
    if (loader) loader.style.display = 'block';
    if (modalImage) {
      modalImage.style.opacity = '0';
      modalImage.style.display = 'none';
    }

    // Preload new image
    const img = new Image();
    img.onload = function() {
      if (modalImage) {
        modalImage.src = imageData.url;
        modalImage.alt = imageData.title;
        modalImage.style.display = 'block';
        
        // Force reflow
        void modalImage.offsetWidth;
        
        // Fade in
        setTimeout(() => {
          modalImage.style.opacity = '1';
        }, 50);
      }
      if (loader) loader.style.display = 'none';
    };
    
    img.onerror = function() {
      if (loader) loader.style.display = 'none';
      showNotification('Failed to load image', 'error');
    };
    
    img.src = imageData.url;

    // Update title and counter
    if (modalTitle) modalTitle.textContent = imageData.title;
    if (currentImageEl) currentImageEl.textContent = currentImageIndex + 1;

    // Update active thumbnail
    thumbnails.forEach((thumb, index) => {
      thumb.classList.toggle('active', index === currentImageIndex);
    });

    // Scroll thumbnail into view
    if (thumbnails[currentImageIndex]) {
      thumbnails[currentImageIndex].scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center'
      });
    }
  }

  /**
   * Navigate to next/previous image
   */
  function navigateImage(direction) {
    currentImageIndex = (currentImageIndex + direction + totalImages) % totalImages;
    updateModalImage();
  }

  /**
   * Setup action buttons
   */
  function setupActionButtons() {
    const downloadBtn = document.getElementById('downloadBtn');
    const shareBtn = document.getElementById('shareBtn');
    const shareMenu = document.getElementById('shareMenu');
    const closeShareMenu = document.getElementById('closeShareMenu');
    const shareOptions = document.querySelectorAll('.share-option');

    // Download button - Direct download to device
    if (downloadBtn) {
      downloadBtn.addEventListener('click', async () => {
        const imageData = galleryImages[currentImageIndex];
        if (!imageData) return;

        // If we have a server-side id for the image, use the download endpoint (simpler and preserves original file)
        if (imageData.id) {
          // use absolute path to trigger file download
          window.location.href = `/gallery/download/${imageData.id}/`;
          return;
        }

        // Fallback: fetch blob and download client-side
        try {
          // Show loading state
          downloadBtn.disabled = true;
          downloadBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Downloading...';

          // Fetch the image as blob
          const response = await fetch(imageData.url);
          const blob = await response.blob();
          
          // Create download link
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          
          // Generate filename
          const filename = `zorpido-${imageData.title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}-${Date.now()}.jpg`;
          a.download = filename;
          
          // Trigger download
          document.body.appendChild(a);
          a.click();
          
          // Cleanup
          setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
          }, 100);

          // Reset button
          downloadBtn.disabled = false;
          downloadBtn.innerHTML = '<i class="bi bi-download"></i> Download';
          
          showNotification('Image downloaded successfully! Check your downloads folder.', 'success');
        } catch (error) {
          console.error('Download failed:', error);
          downloadBtn.disabled = false;
          downloadBtn.innerHTML = '<i class="bi bi-download"></i> Download';
          showNotification('Failed to download image. Please try again.', 'error');
        }
      });
    }

    // Share button - Show share menu
    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        if (shareMenu) {
          shareMenu.classList.add('active');
        }
      });
    }

    // Close share menu
    if (closeShareMenu) {
      closeShareMenu.addEventListener('click', () => {
        if (shareMenu) {
          shareMenu.classList.remove('active');
        }
      });
    }

    // Share options
    shareOptions.forEach(option => {
      option.addEventListener('click', async () => {
        const platform = option.dataset.platform;
        const imageData = galleryImages[currentImageIndex];
        if (!imageData) return;

        const imageUrl = imageData.url;
        const shareText = `Check out this photo from Zorpido: ${imageData.title}`;

        try {
          // Use Web Share API on supported devices (mobile) for a native share sheet
          if (navigator.share) {
            try {
              await navigator.share({
                title: imageData.title,
                text: shareText,
                url: imageUrl
              });
              showNotification('Shared successfully', 'success');
            } catch (err) {
              // User may have cancelled; silently ignore
            }

            // close menu
            if (shareMenu) shareMenu.classList.remove('active');
            return;
          }

          // Desktop / fallback: open social share links using the image URL
          switch(platform) {
            case 'whatsapp':
              // WhatsApp sharing
              const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(shareText + ' ' + imageUrl)}`;
              window.open(whatsappUrl, '_blank');
              showNotification('Opening WhatsApp...', 'success');
              break;

            case 'facebook':
              // Facebook sharing (shares a URL; sharing an image URL is acceptable)
              const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(imageUrl)}&quote=${encodeURIComponent(shareText)}`;
              window.open(facebookUrl, '_blank', 'width=600,height=400');
              showNotification('Opening Facebook...', 'success');
              break;

            case 'messenger':
              // Messenger fallback - open Facebook share dialog for link sharing
              const messengerUrl = `https://www.facebook.com/dialog/send?link=${encodeURIComponent(imageUrl)}&app_id=145634995501895&redirect_uri=${encodeURIComponent(window.location.href)}`;
              window.open(messengerUrl, '_blank', 'width=600,height=600');
              showNotification('Opening Messenger...', 'success');
              break;

            case 'instagram':
              // Instagram - cannot share via URL; copy link and prompt
              await navigator.clipboard.writeText(imageUrl);
              showNotification('Image link copied! Open Instagram and paste in your story or post.', 'info');
              setTimeout(() => {
                window.open('https://www.instagram.com/', '_blank');
              }, 1200);
              break;

            case 'twitter':
              // Twitter sharing
              const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(imageUrl)}`;
              window.open(twitterUrl, '_blank', 'width=600,height=400');
              showNotification('Opening Twitter...', 'success');
              break;

            case 'copy':
              // Copy link to clipboard
              await navigator.clipboard.writeText(imageUrl);
              showNotification('Link copied to clipboard!', 'success');
              break;

            default:
              showNotification('Share option not available', 'error');
          }

          // Close share menu after selection
          if (shareMenu) {
            setTimeout(() => {
              shareMenu.classList.remove('active');
            }, 500);
          }
        } catch (error) {
          console.error('Share failed:', error);
          showNotification('Failed to share. Please try again.', 'error');
        }
      });
    });

    // Close share menu when clicking outside
    document.addEventListener('click', (e) => {
      if (shareMenu && shareMenu.classList.contains('active')) {
        if (!shareMenu.contains(e.target) && !shareBtn.contains(e.target)) {
          shareMenu.classList.remove('active');
        }
      }
    });
  }

  /**
   * Setup keyboard navigation
   */
  function setupKeyboardNav() {
    const modal = document.getElementById('galleryModal');
    if (!modal) return;

    document.addEventListener('keydown', (e) => {
      // Only handle keys when modal is open
      if (!modal.classList.contains('show')) return;

      switch(e.key) {
        case 'ArrowLeft':
          navigateImage(-1);
          break;
        case 'ArrowRight':
          navigateImage(1);
          break;
        case 'Escape':
          // Bootstrap will handle closing
          break;
      }
    });
  }

  /**
   * Setup touch navigation for swipe
   */
  function setupTouchNavigation(modal) {
    let touchStartX = 0;
    let touchEndX = 0;
    let touchStartY = 0;
    let touchEndY = 0;

    const imageViewer = modal.querySelector('.image-viewer');
    if (!imageViewer) return;

    imageViewer.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    imageViewer.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      touchEndY = e.changedTouches[0].screenY;
      handleSwipe();
    }, { passive: true });

    function handleSwipe() {
      const swipeThreshold = 50;
      const diffX = touchStartX - touchEndX;
      const diffY = Math.abs(touchStartY - touchEndY);

      // Only horizontal swipes
      if (diffY < swipeThreshold && Math.abs(diffX) > swipeThreshold) {
        if (diffX > 0) {
          // Swipe left - next
          navigateImage(1);
        } else {
          // Swipe right - previous
          navigateImage(-1);
        }
      }
    }
  }

  /**
   * Add hover effects to cards
   */
  function addHoverEffects() {
    const cards = document.querySelectorAll('.gallery-card');

    cards.forEach(card => {
      const imageContainer = card.querySelector('.image-container');
      
      imageContainer.addEventListener('mousemove', (e) => {
        const rect = imageContainer.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        imageContainer.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
      });
      
      imageContainer.addEventListener('mouseleave', () => {
        imageContainer.style.transform = '';
      });
    });
  }

  /**
   * Initialize lightbox features
   */
  function initLightbox() {
    const modal = document.getElementById('galleryModal');
    if (!modal) return;

    // Zoom on image click
    const modalImage = document.getElementById('galleryModalImage');
    if (modalImage) {
      let isZoomed = false;
      
      modalImage.addEventListener('click', () => {
        isZoomed = !isZoomed;
        modalImage.style.transform = isZoomed ? 'scale(1.5)' : 'scale(1)';
        modalImage.style.cursor = isZoomed ? 'zoom-out' : 'zoom-in';
        modalImage.style.transition = 'transform 0.3s ease';
      });
    }
  }

  /**
   * Show notification
   */
  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `gallery-notification notification-${type}`;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      background: ${type === 'success' ? '#10B981' : type === 'error' ? '#DC2626' : '#3B82F6'};
      color: white;
      border-radius: 10px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      animation: slideIn 0.3s ease;
      font-weight: 600;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => notification.remove(), 300);
    }, 3000);

    // Add animations if not exist
    if (!document.querySelector('style[data-notification-anim]')) {
      const style = document.createElement('style');
      style.setAttribute('data-notification-anim', 'true');
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(400px);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  /**
   * Public API
   */
  window.ZorpidoGallery = {
    openImage: function(index) {
      currentImageIndex = index;
      const modal = new bootstrap.Modal(document.getElementById('galleryModal'));
      modal.show();
      updateModalImage();
    },
    nextImage: function() {
      navigateImage(1);
    },
    prevImage: function() {
      navigateImage(-1);
    },
    getCurrentIndex: function() {
      return currentImageIndex;
    }
  };

})();