/* ====================================================================
   sidebar.js - open/close drawer.
   State lives on body[data-sidebar-open]. CSS reads it and animates.
   Closes on: trigger-click (toggle), overlay-click, Esc key.
   ==================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const trigger = document.getElementById('sidebar-trigger');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (!trigger || !sidebar || !overlay) return;

    function setOpen(open) {
      document.body.dataset.sidebarOpen = open ? 'true' : 'false';
      trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
      sidebar.setAttribute('aria-hidden', open ? 'false' : 'true');
      overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
    }

    function isOpen() {
      return document.body.dataset.sidebarOpen === 'true';
    }

    // Initial closed state.
    setOpen(false);

    trigger.addEventListener('click', function () {
      setOpen(!isOpen());
    });

    overlay.addEventListener('click', function () {
      setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) {
        setOpen(false);
      }
    });

    // Close after navigating via a sidebar link (mobile pattern).
    sidebar.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setOpen(false);
      });
    });
  });
})();
