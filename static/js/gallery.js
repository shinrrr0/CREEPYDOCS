/* ====================================================================
   gallery.js - image gallery interactions.

   Responsibilities:
     1. ImageViewer – class that manages the lightbox overlay.
        Open / close / keyboard / scroll-lock.
        Designed for easy extension – see FUTURE comments inside the class.
     2. GalleryGrid  – class that binds click/keyboard on the masonry grid
        and delegates to ImageViewer.

   Both classes self-initialise on DOMContentLoaded and bail silently
   if their root elements are absent (non-gallery pages are unaffected).
   ==================================================================== */

(function () {
  'use strict';

  // ====================================================================
  // ImageViewer
  // Manages the fullscreen lightbox overlay (#image-viewer).
  // ====================================================================
  class ImageViewer {
    /**
     * @param {object} [opts]
     * @param {string} [opts.viewerSelector]   - Root overlay element selector.
     * @param {string} [opts.backdropSelector] - Backdrop click-to-close element.
     * @param {string} [opts.closeSelector]    - Close button selector.
     * @param {string} [opts.imgSelector]      - <img> inside the panel.
     * @param {string} [opts.titleSelector]    - Title <span> inside the panel.
     * @param {string} [opts.wrapperSelector]  - .gallery-wrapper for dim effect.
     */
    constructor(opts = {}) {
      this._sel = {
        viewer:   opts.viewerSelector   || '#image-viewer',
        backdrop: opts.backdropSelector || '#viewer-backdrop',
        close:    opts.closeSelector    || '#viewer-close',
        img:      opts.imgSelector      || '#viewer-img',
        title:    opts.titleSelector    || '#viewer-title',
        wrapper:  opts.wrapperSelector  || '.gallery-wrapper',
      };

      this._viewer   = document.querySelector(this._sel.viewer);
      this._wrapper  = document.querySelector(this._sel.wrapper);

      if (!this._viewer) return;   // not on a gallery page – do nothing

      this._imgEl    = this._viewer.querySelector(this._sel.img);
      this._titleEl  = this._viewer.querySelector(this._sel.title);
      this._backdrop = this._viewer.querySelector(this._sel.backdrop);
      this._closeBtn = this._viewer.querySelector(this._sel.close);

      this._isOpen    = false;
      this._currentId = null;  // FUTURE: used by prev/next navigation

      this._bindEvents();
    }

    // ------------------------------------------------------------------
    // Public API
    // ------------------------------------------------------------------

    /** Open the viewer and display `src` with `title`. */
    open(src, title, imageId = null) {
      if (!this._viewer) return;

      this._imgEl.src   = src;
      this._imgEl.alt   = title;
      this._titleEl.textContent = title;
      this._currentId   = imageId;

      this._viewer.dataset.state = 'open';
      this._isOpen = true;

      // Dim the grid and lock scroll.
      if (this._wrapper) this._wrapper.dataset.dimmed = 'true';
      document.body.dataset.viewerOpen = 'true';

      // FUTURE: populate #viewer-meta with tags / author / date
      // FUTURE: update browser history with ?view=<imageId>
      // FUTURE: preload prev/next images for navigation

      this._closeBtn.focus();
    }

    /** Close the viewer and restore the grid. */
    close() {
      if (!this._viewer || !this._isOpen) return;

      this._viewer.dataset.state = 'closed';
      this._isOpen = false;
      this._currentId = null;

      if (this._wrapper) this._wrapper.dataset.dimmed = 'false';
      document.body.dataset.viewerOpen = 'false';

      // Clear src after transition so the old image doesn't flash on re-open.
      const dur = parseFloat(
        getComputedStyle(document.documentElement)
          .getPropertyValue('--dur-base')
      ) * 1000 || 320;
      setTimeout(() => {
        if (!this._isOpen) this._imgEl.src = '';
      }, dur);

      // FUTURE: restore history state when using pushState navigation
    }

    /** True while the viewer is visible. */
    get isOpen() { return this._isOpen; }

    // ------------------------------------------------------------------
    // Private helpers
    // ------------------------------------------------------------------

    _bindEvents() {
      // Close button
      this._closeBtn?.addEventListener('click', () => this.close());

      // Backdrop click (outside the panel)
      this._backdrop?.addEventListener('click', () => this.close());

      // Keyboard: Esc closes; arrow keys FUTURE navigation
      document.addEventListener('keydown', (e) => {
        if (!this._isOpen) return;
        if (e.key === 'Escape') { e.preventDefault(); this.close(); }
        // FUTURE: ArrowRight → this.next(); ArrowLeft → this.prev();
      });
    }

    // ------------------------------------------------------------------
    // FUTURE extension points
    // ------------------------------------------------------------------
    // next()  { /* advance to next card's data-image-src */ }
    // prev()  { /* go back to previous card's data-image-src */ }
    // _populateMeta(imageId) { /* fetch /api/gallery/<id> and fill #viewer-meta */ }
  }


  // ====================================================================
  // GalleryGrid
  // Binds click and keyboard events on the masonry grid;
  // delegates image data to the ImageViewer.
  // ====================================================================
  class GalleryGrid {
    /**
     * @param {ImageViewer} viewer - Viewer instance to delegate opens to.
     * @param {string} [gridSelector] - The masonry grid container selector.
     * @param {string} [cardSelector] - Individual card selector (within grid).
     */
    constructor(viewer, gridSelector = '#gallery-grid', cardSelector = '.image-card') {
      this._viewer       = viewer;
      this._grid         = document.querySelector(gridSelector);
      this._cardSelector = cardSelector;

      if (!this._grid) return;   // not on gallery page
      this._bindEvents();
    }

    _bindEvents() {
      // Event delegation: one listener handles all current and future cards.
      this._grid.addEventListener('click', (e) => {
        const card = e.target.closest(this._cardSelector);
        if (card) this._openCard(card);
      });

      // Keyboard: Enter / Space activates the focused card.
      this._grid.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        const card = e.target.closest(this._cardSelector);
        if (card) { e.preventDefault(); this._openCard(card); }
      });
    }

    _openCard(card) {
      const src   = card.dataset.imageSrc;
      const title = card.dataset.imageTitle;
      const id    = card.dataset.imageId ? parseInt(card.dataset.imageId, 10) : null;

      if (src) this._viewer.open(src, title, id);
    }
  }


  // ====================================================================
  // Bootstrap – runs only on pages that have the gallery markup.
  // ====================================================================
  document.addEventListener('DOMContentLoaded', function () {
    const viewer = new ImageViewer();
    new GalleryGrid(viewer);

    // Expose globally for debugging / future inter-module communication.
    // FUTURE: replace with a proper module system or event bus.
    window._creepyGallery = { viewer };
  });

})();
