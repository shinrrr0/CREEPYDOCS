/* ====================================================================
   header_scroll.js - hide title on scroll-down, keep nav visible.
   Sets data-state="visible" / "compact" on #site-header. CSS handles
   the actual transform (title hides, padding adjusts).
   ==================================================================== */

(function () {
  'use strict';

  const HIDE_AFTER_PX = 80;   // don't collapse until user has scrolled this far
  const DELTA_THRESHOLD = 6;  // px of movement required before reacting

  document.addEventListener('DOMContentLoaded', function () {
    const header = document.getElementById('site-header');
    if (!header) return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    function update() {
      const currentY = window.scrollY;
      const delta = currentY - lastScrollY;

      // Always show full header near the top of the page.
      if (currentY < HIDE_AFTER_PX) {
        header.dataset.state = 'visible';
      } else if (Math.abs(delta) > DELTA_THRESHOLD) {
        // Scroll down: compact (nav stays, title hides)
        // Scroll up: show full header
        header.dataset.state = delta > 0 ? 'compact' : 'visible';
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
