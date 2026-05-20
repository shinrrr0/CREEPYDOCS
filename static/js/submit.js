/* ====================================================================
   submit.js - pasta submission form.
   On success: form resets, success banner appears with a link to the
   main feed where the new story is now at the top.
   ==================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    var form       = document.getElementById('submit-form');
    var submitBtn  = document.getElementById('submit-btn');
    var errorEl    = document.getElementById('submit-error');
    var successEl  = document.getElementById('submit-success');
    var charCount  = document.getElementById('submit-char-count');
    var fileInput  = document.getElementById('submit-image');
    var fileText   = document.getElementById('submit-file-text');
    var bodyInput  = form ? form.querySelector('textarea[name="body"]') : null;

    if (!form) return;

    /* ----------------------------------------------------------------
       Character counter
       ---------------------------------------------------------------- */
    if (bodyInput && charCount) {
      bodyInput.addEventListener('input', function () {
        var n = bodyInput.value.length;
        charCount.textContent = n.toLocaleString('ru') + ' символов';
      });
    }

    /* ----------------------------------------------------------------
       File label
       ---------------------------------------------------------------- */
    if (fileInput && fileText) {
      fileInput.addEventListener('change', function () {
        fileText.textContent = fileInput.files.length > 0
          ? fileInput.files[0].name
          : 'Выбрать изображение';
      });

      var fileLabel = form.querySelector('.submit-form__file-label');
      if (fileLabel) {
        fileLabel.addEventListener('dragover',  function (e) {
          e.preventDefault();
          fileLabel.classList.add('submit-form__file-label--drag');
        });
        fileLabel.addEventListener('dragleave', function () {
          fileLabel.classList.remove('submit-form__file-label--drag');
        });
        fileLabel.addEventListener('drop', function (e) {
          e.preventDefault();
          fileLabel.classList.remove('submit-form__file-label--drag');
          if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            fileText.textContent = fileInput.files[0].name;
          }
        });
      }
    }

    /* ----------------------------------------------------------------
       Submission
       ---------------------------------------------------------------- */
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var title  = (form.querySelector('[name="title"]').value  || '').trim();
      var body   = (form.querySelector('[name="body"]').value   || '').trim();
      var author = (form.querySelector('[name="author"]').value || '').trim();
      var file   = fileInput && fileInput.files.length > 0 ? fileInput.files[0] : null;

      if (!title) { showError('Заголовок не может быть пустым');     return; }
      if (!body)  { showError('Текст истории не может быть пустым'); return; }

      hideError();
      setLoading(true);

      var fd = new FormData();
      fd.append('title', title);
      fd.append('body',  body);
      if (author) fd.append('author', author);
      if (file)   fd.append('image',  file);

      fetch('/api/submit', { method: 'POST', body: fd })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            // Story saved with section_slug='stories' → appears at the top
            // of /section/stories ordered by created_at desc.
            window.location.href = '/section/stories';
          } else {
            showError(data.error || 'Ошибка при публикации');
          }
        })
        .catch(function (err) {
          showError('Сетевая ошибка: ' + err.message);
        })
        .finally(function () {
          setLoading(false);
        });
    });

    /* ----------------------------------------------------------------
       Helpers
       ---------------------------------------------------------------- */
    function setLoading(on) {
      submitBtn.disabled    = on;
      submitBtn.textContent = on ? 'Публикую...' : 'Опубликовать';
    }

    function showError(msg) {
      errorEl.textContent = msg;
      errorEl.hidden = false;
      errorEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideError() { errorEl.hidden = true; }
  });
})();
