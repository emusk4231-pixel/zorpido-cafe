/*
  gallery-modal.js
  - Lightweight JS to open a minimal gallery modal that shows only the image.
  - Adds keyboard navigation, fade-in/out, and ensures correct image sizing.
  - Comments explain behavior.
*/

document.addEventListener('DOMContentLoaded', function () {
  // Query the gallery section and modal elements
  const gallerySection = document.querySelector('.zorpido-gallery-section');
  if (!gallerySection) return; // nothing to do on pages without gallery

  // Create references for the modal element provided by template
  const modalEl = document.getElementById('galleryModal');
  const modalImage = document.getElementById('galleryModalImage');
  const modalClose = modalEl ? modalEl.querySelector('.modal-close-btn') : null;
  const navPrev = modalEl ? modalEl.querySelector('.nav-prev') : null;
  const navNext = modalEl ? modalEl.querySelector('.nav-next') : null;

  // Build an array of all gallery images in order for keyboard nav
  const imageContainers = Array.from(gallerySection.querySelectorAll('.image-container'));
  const gallerySrcs = imageContainers.map(ic => ({
    src: ic.dataset.image || (ic.querySelector('img') ? ic.querySelector('img').src : ''),
    title: ic.dataset.title || '',
    id: ic.dataset.id || null
  }));

  let currentIndex = 0;
  let bsModal = null;

  // Initialize Bootstrap modal instance lazily
  if (modalEl) bsModal = bootstrap.Modal.getOrCreateInstance(modalEl, {keyboard:false});

  // Helper: show image by index
  function showImage(index, {withAnimation=true} = {}){
    if (!gallerySrcs.length) return;
    currentIndex = (index + gallerySrcs.length) % gallerySrcs.length;
    const src = gallerySrcs[currentIndex].src;

    // small loading UX: hide until loaded
    if (!modalImage) return;
    modalImage.style.opacity = '0';
    modalImage.src = src;
    modalImage.alt = gallerySrcs[currentIndex].title || 'Gallery image';

    // once loaded, fade in smoothly
    modalImage.onload = () => {
      modalImage.style.transition = 'opacity .28s ease';
      modalImage.style.opacity = '1';
    };
  }

  // Open modal and show clicked image
  function openAtIndex(index){
    if (!bsModal) return;
    showImage(index);
    // show bootstrap modal; CSS handles dialog animation
    bsModal.show();
  }

  // Attach click handlers to each image container
  imageContainers.forEach((container, idx) => {
    container.style.cursor = 'zoom-in';
    container.addEventListener('click', (e) => {
      e.preventDefault();
      openAtIndex(idx);
    });
  });

  // Close handlers
  if (modalClose){
    modalClose.addEventListener('click', () => bsModal.hide());
  }

  // Navigation handlers
  if (navPrev){
    navPrev.addEventListener('click', (e)=>{
      e.stopPropagation();
      showImage(currentIndex - 1);
    });
  }
  if (navNext){
    navNext.addEventListener('click', (e)=>{
      e.stopPropagation();
      showImage(currentIndex + 1);
    });
  }

  // Keyboard navigation: left/right arrows and Escape
  document.addEventListener('keydown', (e)=>{
    if (!modalEl || !modalEl.classList.contains('show')) return; // only when modal is open
    if (e.key === 'ArrowLeft'){
      showImage(currentIndex - 1);
    } else if (e.key === 'ArrowRight'){
      showImage(currentIndex + 1);
    } else if (e.key === 'Escape'){
      bsModal.hide();
    }
  });

  // Prevent scroll behind modal on open & restore on close (reinforce Bootstrap behavior)
  if (modalEl){
    modalEl.addEventListener('show.bs.modal', () => {
      document.documentElement.style.overflow = 'hidden';
    });
    modalEl.addEventListener('hidden.bs.modal', () => {
      document.documentElement.style.overflow = '';
      // clear image to free memory
      modalImage.src = '';
    });
  }

});
