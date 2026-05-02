/* ====================================================================
   main.js - top-level entry point.
   Other scripts (header_scroll, sidebar, content_expand) self-init
   on DOMContentLoaded, so this file is just a place for cross-cutting
   bootstrap logic.
   ==================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    // Mark the body as JS-enabled so CSS can hide no-JS fallbacks if needed.
    document.body.dataset.jsReady = 'true';

    // FUTURE: register service worker, kick off analytics, hydrate
    // theme preference from localStorage, etc.
  });
})();
