/* ====================================================================
   content_expand.js - "expand" button for content blocks.

   Strategy:
     1. Read collapsed max-height from CSS variable.
     2. For each block, compare scrollHeight to that limit.
     3. If overflow exists, reveal the toggle button and wire it up.
     4. On expand, set inline max-height to the measured scrollHeight
        so the CSS transition has a concrete target. After the
        transition, drop the inline value so future content changes
        re-flow naturally.
   ==================================================================== */

(function () {
  'use strict';

  function readCollapsedHeight() {
    const raw = getComputedStyle(document.documentElement)
      .getPropertyValue('--content-collapsed-height');
    return parseInt(raw, 10) || 220;
  }

  function setupBlock(block, collapsedHeight) {
    const body = block.querySelector('[data-role="body"]');
    const text = block.querySelector('[data-role="text"]');
    const toggle = block.querySelector('[data-role="toggle"]');
    if (!body || !text || !toggle) return;

    // Decide whether the toggle is needed based on actual content size.
    // Use text.scrollHeight (the real content) rather than body.scrollHeight
    // so the fade overlay doesn't skew the measurement.
    const overflows = text.scrollHeight > collapsedHeight + 4;
    if (!overflows) {
      // No overflow: hide fade + button entirely so the block looks clean.
      const fade = block.querySelector('[data-role="fade"]');
      if (fade) fade.style.display = 'none';
      body.style.maxHeight = 'none';
      return;
    }

    // Overflow exists: surface the toggle.
    toggle.hidden = false;

    toggle.addEventListener('click', function () {
      const willExpand = block.dataset.expanded !== 'true';

      if (willExpand) {
        // Set explicit max-height for a smooth transition target.
        body.style.maxHeight = text.scrollHeight + 'px';
        block.dataset.expanded = 'true';

        // After transition completes, remove the inline value so the
        // block re-measures correctly if content changes later.
        body.addEventListener('transitionend', function onEnd() {
          body.removeEventListener('transitionend', onEnd);
          if (block.dataset.expanded === 'true') {
            body.style.maxHeight = 'none';
          }
        });
      } else {
        // First fix the inline value so the transition has a starting
        // point (otherwise going from 'none' won't animate).
        body.style.maxHeight = text.scrollHeight + 'px';
        // Force reflow.
        // eslint-disable-next-line no-unused-expressions
        body.offsetHeight;
        // Then collapse back to CSS-driven value.
        body.style.maxHeight = '';
        block.dataset.expanded = 'false';
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    const collapsedHeight = readCollapsedHeight();
    document.querySelectorAll('.content-block').forEach(function (block) {
      setupBlock(block, collapsedHeight);
    });

    // FUTURE: re-run setup on dynamically loaded blocks (infinite scroll).
    // Expose a hook on window for that case:
    window.CreepyDocs = window.CreepyDocs || {};
    window.CreepyDocs.setupContentBlock = function (block) {
      setupBlock(block, readCollapsedHeight());
    };
  });
})();
