/* ====================================================================
   blog.js - blog post creation, file upload, AJAX submission,
             and blog-number navigation.
   Each blog has its own form with blog_id in data attribute.
   ==================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    /* ----------------------------------------------------------------
       Blog number navigation
       ---------------------------------------------------------------- */
    var goInput = document.getElementById('blog-go-input');
    var goBtn   = document.getElementById('blog-go-btn');

    function navigateToBlog() {
      var val = parseInt(goInput.value, 10);
      var min = parseInt(goInput.min, 10) || 1;
      var max = parseInt(goInput.max, 10) || 100;
      if (!val || val < min || val > max) {
        goInput.classList.add('blog-header__go-input--invalid');
        setTimeout(function () {
          goInput.classList.remove('blog-header__go-input--invalid');
        }, 600);
        return;
      }
      window.location.href = '/blog/' + val;
    }

    if (goBtn) {
      goBtn.addEventListener('click', navigateToBlog);
    }

    if (goInput) {
      goInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') navigateToBlog();
      });
    }

    /* ----------------------------------------------------------------
       Post creation form
       ---------------------------------------------------------------- */
    var form = document.getElementById('post-form');
    if (!form) return;

    var blogId = form.dataset.blogId;
    if (!blogId) {
      console.error('Blog ID not found in form data');
      return;
    }

    var textarea  = form.querySelector('textarea[name="text"]');
    var fileInput = form.querySelector('input[name="image"]');
    var fileLabel = form.querySelector('.post-form__file-label');
    var fileName  = document.getElementById('file-name');
    var errorDiv  = document.getElementById('post-error');
    var submitBtn = form.querySelector('.post-form__submit');

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

      var text = textarea.value.trim();
      var file = fileInput.files.length > 0 ? fileInput.files[0] : null;

      // Client-side validation
      if (!text && !file) {
        showError('Напиши текст или прикрепи изображение');
        return;
      }

      // Build FormData
      var formData = new FormData();
      if (text) formData.append('text', text);
      if (file) formData.append('image', file);

      // Disable submit button
      submitBtn.disabled = true;
      submitBtn.textContent = 'Отправляю...';

      // POST to API
      var apiUrl = '/api/blog/' + blogId + '/post';
      fetch(apiUrl, {
        method: 'POST',
        body: formData,
      })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          if (data.success) {
            // Clear form
            textarea.value = '';
            fileInput.value = '';
            fileName.textContent = '';
            errorDiv.style.display = 'none';

            location.reload();
          } else {
            showError(data.error || 'Ошибка при создании поста');
          }
        })
        .catch(function (err) {
          showError('Сетевая ошибка: ' + err.message);
          console.error(err);
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Отправить';
        });
    });

    function showError(message) {
      errorDiv.textContent = message;
      errorDiv.style.display = 'block';
      setTimeout(function () {
        errorDiv.style.display = 'none';
      }, 5000);
    }
  });
})();
