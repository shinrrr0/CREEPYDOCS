/* ====================================================================
   blog.js - blog post creation, file upload, AJAX submission.
   Each blog has its own form with blog_id in data attribute.
   ==================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('post-form');
    if (!form) return;

    const blogId = form.dataset.blogId;
    if (!blogId) {
      console.error('Blog ID not found in form data');
      return;
    }

    const textarea = form.querySelector('textarea[name="text"]');
    const fileInput = form.querySelector('input[name="image"]');
    const fileLabel = form.querySelector('.post-form__file-label');
    const fileName = document.getElementById('file-name');
    const errorDiv = document.getElementById('post-error');
    const submitBtn = form.querySelector('.post-form__submit');

    // ---- File selection display ----
    fileInput.addEventListener('change', function () {
      if (this.files.length > 0) {
        fileName.textContent = this.files[0].name;
      } else {
        fileName.textContent = '';
      }
    });

    // Drag-and-drop for file input
    fileLabel.addEventListener('dragover', function (e) {
      e.preventDefault();
      this.style.borderColor = 'var(--color-accent-bright)';
      this.style.background = 'rgba(60, 60, 60, 1)';
    });

    fileLabel.addEventListener('dragleave', function () {
      this.style.borderColor = '';
      this.style.background = '';
    });

    fileLabel.addEventListener('drop', function (e) {
      e.preventDefault();
      this.style.borderColor = '';
      this.style.background = '';

      if (e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        if (fileInput.files[0]) {
          fileName.textContent = fileInput.files[0].name;
        }
      }
    });

    // ---- Form submission ----
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const text = textarea.value.trim();
      const file = fileInput.files.length > 0 ? fileInput.files[0] : null;

      // Client-side validation
      if (!text && !file) {
        showError('Напиши текст или прикрепи изображение');
        return;
      }

      // Build FormData
      const formData = new FormData();
      if (text) formData.append('text', text);
      if (file) formData.append('image', file);

      // Disable submit button
      submitBtn.disabled = true;
      submitBtn.textContent = 'Отправляю...';

      // POST to API - use blog_id in URL
      const apiUrl = `/api/blog/${blogId}/post`;
      fetch(apiUrl, {
        method: 'POST',
        body: formData,
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Clear form
            textarea.value = '';
            fileInput.value = '';
            fileName.textContent = '';
            errorDiv.style.display = 'none';

            // Reload posts (simple: reload page)
            // TODO: add AJAX reload of posts instead of full page reload
            location.reload();
          } else {
            showError(data.error || 'Ошибка при создании поста');
          }
        })
        .catch(err => {
          showError('Сетевая ошибка: ' + err.message);
          console.error(err);
        })
        .finally(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Отправить';
        });
    });

    function showError(message) {
      errorDiv.textContent = message;
      errorDiv.style.display = 'block';
      setTimeout(() => {
        errorDiv.style.display = 'none';
      }, 5000);
    }
  });
})();
