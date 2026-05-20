/* ====================================================================
   comments.js - comment thread loader and submission for story cards.

   Each story card has a .content-block__comments[data-story-id="N"]
   section. This script initialises ALL of them on the page so the
   feed works without any per-page wiring.

   Flow:
     1. User clicks the toggle → panel slides open + comments are
        fetched from GET /api/stories/<id>/comments (once per session).
     2. User fills the form and clicks "Отправить" → POST to same URL.
     3. New comment is appended to the list; counter is updated.
   ==================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.content-block__comments[data-story-id]')
      .forEach(initCommentSection);
  });

  /* Also expose for dynamically inserted cards (submit.js) */
  window.__initCommentSection = initCommentSection;

  /* ------------------------------------------------------------------ */
  /* Init                                                                 */
  /* ------------------------------------------------------------------ */
  function initCommentSection(section) {
    var storyId = section.dataset.storyId;
    if (!storyId) return;

    var toggle   = section.querySelector('[data-role="comments-toggle"]');
    var panel    = section.querySelector('[data-role="comments-panel"]');
    var list     = section.querySelector('[data-role="comments-list"]');
    var form     = section.querySelector('[data-role="comments-form"]');
    var countEl  = section.querySelector('[data-role="comments-count"]');
    var errorEl  = section.querySelector('[data-role="comments-error"]');
    var submitBtn = form ? form.querySelector('button[type="submit"]') : null;

    if (!toggle || !panel || !list || !form || !countEl || !errorEl) return;

    var loaded = false;
    var open   = false;

    /* ---- Toggle ---- */
    toggle.addEventListener('click', function () {
      open = !open;
      panel.hidden = !open;
      toggle.dataset.open = open ? 'true' : 'false';

      if (open && !loaded) {
        loadComments(storyId, list, function () { loaded = true; });
      }
    });

    /* ---- Form submit ---- */
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var bodyInput   = form.querySelector('[name="body"]');
      var authorInput = form.querySelector('[name="author"]');
      var body   = bodyInput ? bodyInput.value.trim() : '';
      var author = authorInput ? authorInput.value.trim() : '';

      if (!body) {
        showError(errorEl, 'Текст комментария не может быть пустым');
        return;
      }

      hideError(errorEl);
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Отправляю...';
      }

      fetch('/api/stories/' + storyId + '/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({ body: body, author: author || undefined }),
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            if (bodyInput)   bodyInput.value   = '';
            if (authorInput) authorInput.value = '';

            /* Remove "empty" placeholder if present */
            var empty = list.querySelector('.comments__empty');
            if (empty) empty.remove();

            appendComment(list, data.comment);

            /* Update count badge */
            var current = parseInt(countEl.textContent, 10) || 0;
            countEl.textContent = current + 1;
          } else {
            showError(errorEl, data.error || 'Ошибка при отправке');
          }
        })
        .catch(function (err) {
          showError(errorEl, 'Сетевая ошибка: ' + err.message);
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Отправить';
          }
        });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Load comments via GET                                                */
  /* ------------------------------------------------------------------ */
  function loadComments(storyId, list, onDone) {
    list.innerHTML = '<p class="comments__loading">Загрузка...</p>';

    fetch('/api/stories/' + storyId + '/comments')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        list.innerHTML = '';
        if (data.success && data.comments.length > 0) {
          data.comments.forEach(function (c) { appendComment(list, c); });
        } else if (data.success) {
          list.innerHTML =
            '<p class="comments__empty">Комментариев пока нет. Будь первым!</p>';
        } else {
          list.innerHTML =
            '<p class="comments__msg comments__msg--error">Не удалось загрузить комментарии.</p>';
        }
      })
      .catch(function () {
        list.innerHTML =
          '<p class="comments__msg comments__msg--error">Сетевая ошибка при загрузке.</p>';
      })
      .finally(onDone);
  }

  /* ------------------------------------------------------------------ */
  /* Render one comment                                                   */
  /* ------------------------------------------------------------------ */
  function appendComment(list, comment) {
    var date = new Date(comment.created_at);
    var dateStr = date.toLocaleString('ru-RU', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit',
    });

    var el = document.createElement('div');
    el.className = 'comment';
    el.innerHTML =
      '<div class="comment__meta">' +
        '<span class="comment__author">' + esc(comment.author || 'anon') + '</span>' +
        '<span class="comment__date">' + dateStr + '</span>' +
      '</div>' +
      '<div class="comment__body">' +
        esc(comment.body).replace(/\n/g, '<br>') +
      '</div>';

    list.appendChild(el);
  }

  /* ------------------------------------------------------------------ */
  /* Helpers                                                              */
  /* ------------------------------------------------------------------ */
  function esc(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function showError(el, msg) {
    el.textContent = msg;
    el.hidden = false;
  }

  function hideError(el) {
    el.hidden = true;
  }
})();
