/* ====================================================================
   header_scroll.js - hide header on scroll-down, show on scroll-up.
   Sets data-state="visible" / "hidden" on #site-header. CSS handles
   the actual transform.
   ==================================================================== */

(function () {
  'use strict';

  const HIDE_AFTER_PX = 80;   // don't hide until user has scrolled this far
  const DELTA_THRESHOLD = 6;  // px of movement required before reacting

  document.addEventListener('DOMContentLoaded', function () {
    const header = document.getElementById('site-header');
    if (!header) return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    function update() {
      const currentY = window.scrollY;
      const delta = currentY - lastScrollY;

      // Always show near the top of the page.
      if (currentY < HIDE_AFTER_PX) {
        header.dataset.state = 'visible';
      } else if (Math.abs(delta) > DELTA_THRESHOLD) {
        header.dataset.state = delta > 0 ? 'hidden' : 'visible';
      }

      lastScrollY = currentY;
      ticking = false;
    }

    // rAF-throttled scroll listener.
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
  });
})();
