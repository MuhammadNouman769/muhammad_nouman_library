// Muhammad Nouman Library — global AJAX behaviour. No full page reloads.
(function () {
  const csrf = window.MNL.csrfToken;

  function toast(msg) {
    const area = document.getElementById('toast-area');
    if (!area) return;
    const el = document.createElement('div');
    el.className = 'mnl-toast';
    el.textContent = msg;
    area.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  function postForm(url, data) {
    const body = new URLSearchParams(data);
    return fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body,
    }).then((r) => r.json());
  }

  document.addEventListener('DOMContentLoaded', () => {
    /* ---------------- live search ---------------- */
    const searchInput = document.getElementById('navSearchInput');
    const searchResults = document.getElementById('navSearchResults');
    let searchTimer;
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        const q = searchInput.value.trim();
        if (q.length < 2) {
          searchResults.classList.add('d-none');
          searchResults.innerHTML = '';
          return;
        }
        searchTimer = setTimeout(() => {
          fetch(`${window.MNL.urls.liveSearch}?q=${encodeURIComponent(q)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
          })
            .then((r) => r.json())
            .then((data) => {
              if (!data.results.length) {
                searchResults.innerHTML = '<div class="p-3 text-muted small">No books found.</div>';
              } else {
                searchResults.innerHTML = data.results
                  .map(
                    (b) => `<a href="${b.url}">
                      <img src="${b.cover || 'https://placehold.co/60x84'}" alt="">
                      <div><div class="fw-semibold small">${b.title}</div>
                      <div class="text-muted small">${b.author} — ${b.is_free ? 'Free' : b.price}</div></div>
                    </a>`
                  )
                  .join('');
              }
              searchResults.classList.remove('d-none');
            });
        }, 300);
      });
      document.addEventListener('click', (e) => {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
          searchResults.classList.add('d-none');
        }
      });
    }

    /* ---------------- add to cart ---------------- */
    document.body.addEventListener('click', (e) => {
      const btn = e.target.closest('.js-add-to-cart');
      if (!btn) return;
      e.preventDefault();
      const bookId = btn.dataset.bookId;
      postForm(`/orders/cart/add/${bookId}/`, { quantity: 1 }).then((data) => {
        if (data.status === 'ok') {
          document.querySelectorAll('#cartCountBadge').forEach((b) => (b.textContent = data.cart_count));
          toast('Added to cart');
          const miniCart = document.getElementById('miniCartBody');
          if (miniCart && data.mini_cart_html) miniCart.innerHTML = data.mini_cart_html;
        }
      });
    });

    /* ---------------- cart page: update / remove ---------------- */
    document.body.addEventListener('click', (e) => {
      const rm = e.target.closest('.js-cart-remove');
      if (rm) {
        e.preventDefault();
        postForm(`/orders/cart/remove/${rm.dataset.bookId}/`, {}).then((data) => refreshCart(data));
      }
    });
    document.body.addEventListener('change', (e) => {
      const qty = e.target.closest('.js-cart-qty');
      if (qty) {
        postForm(`/orders/cart/update/${qty.dataset.bookId}/`, { quantity: qty.value }).then((data) => refreshCart(data));
      }
    });
    function refreshCart(data) {
      if (data.status !== 'ok') return;
      document.querySelectorAll('#cartCountBadge').forEach((b) => (b.textContent = data.cart_count));
      const tableWrap = document.getElementById('cartTableWrap');
      if (tableWrap && data.table_html !== undefined) tableWrap.innerHTML = data.table_html;
      const totalEl = document.getElementById('cartTotal');
      if (totalEl && data.cart_total !== undefined) totalEl.textContent = data.cart_total;
    }

    /* ---------------- coupon ---------------- */
    const couponForm = document.getElementById('couponForm');
    if (couponForm) {
      couponForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const code = document.getElementById('couponCode').value;
        postForm(window.location.pathname.includes('checkout') ? '/orders/cart/coupon/apply/' : '/orders/cart/coupon/apply/', { code }).then((data) => {
          const box = document.getElementById('couponMsg');
          if (data.status === 'ok') {
            box.className = 'text-success small mt-2';
            box.textContent = `Coupon applied: ${data.discount_percent}% off`;
          } else {
            box.className = 'text-danger small mt-2';
            box.textContent = data.message;
          }
        });
      });
    }

    /* ---------------- book filters (AJAX, no reload) ---------------- */
    const filterForm = document.getElementById('bookFilterForm');
    const grid = document.getElementById('bookGrid');
    if (filterForm && grid) {
      const runFilter = () => {
        const params = new URLSearchParams(new FormData(filterForm));
        fetch(`${filterForm.dataset.baseUrl}?${params.toString()}`, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
          .then((r) => r.json())
          .then((data) => {
            grid.innerHTML = data.html;
            const countEl = document.getElementById('resultCount');
            if (countEl) countEl.textContent = data.count;
          });
      };
      filterForm.addEventListener('change', runFilter);
      filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        runFilter();
      });
      let t;
      const q = filterForm.querySelector('[name="q"]');
      if (q) q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(runFilter, 350); });
    }

    /* ---------------- wishlist toggle ---------------- */
    document.body.addEventListener('click', (e) => {
      const wbtn = e.target.closest('.js-wishlist-toggle');
      if (!wbtn) return;
      e.preventDefault();
      postForm(wbtn.dataset.url, {}).then((data) => {
        wbtn.classList.toggle('active', data.in_wishlist);
        wbtn.innerHTML = data.in_wishlist ? '<i class="bi bi-heart-fill"></i>' : '<i class="bi bi-heart"></i>';
        toast(data.in_wishlist ? 'Added to wishlist' : 'Removed from wishlist');
      });
    });

    /* ---------------- review submit ---------------- */
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
      reviewForm.querySelectorAll('.js-star').forEach((star) => {
        star.addEventListener('click', () => {
          reviewForm.querySelector('[name="rating"]').value = star.dataset.value;
          reviewForm.querySelectorAll('.js-star').forEach((s) => s.classList.toggle('bi-star-fill', s.dataset.value <= star.dataset.value));
        });
      });
      reviewForm.addEventListener('submit', (e) => {
        e.preventDefault();
        postForm(reviewForm.action, new FormData(reviewForm)).then((data) => {
          if (data.status === 'ok') {
            document.getElementById('reviewsList').insertAdjacentHTML('afterbegin', data.html);
            document.getElementById('avgRating').textContent = data.average_rating;
            document.getElementById('reviewCount').textContent = data.review_count;
            toast('Review submitted');
          }
        });
      });
    }

    /* ---------------- contact form ---------------- */
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
      contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        postForm(window.MNL.urls.contactSubmit, new FormData(contactForm)).then((data) => {
          const box = document.getElementById('contactMsg');
          if (data.status === 'ok') {
            box.className = 'alert alert-success mt-3';
            box.textContent = data.message;
            contactForm.reset();
          } else {
            box.className = 'alert alert-danger mt-3';
            box.textContent = 'Please check the form and try again.';
          }
        });
      });
    }

    /* ---------------- audio player (listen without reload) ---------------- */
    document.body.addEventListener('click', (e) => {
      const playBtn = e.target.closest('.js-listen-audio');
      if (!playBtn) return;
      e.preventDefault();
      const url = playBtn.dataset.audioUrl;
      const title = playBtn.dataset.title;
      const box = document.getElementById('audioPlayerBox');
      if (!box) return;
      box.classList.remove('d-none');
      box.querySelector('.player-title').textContent = title;
      const audioEl = box.querySelector('audio');
      audioEl.src = url;
      audioEl.play().catch(() => {});
    });

    /* ---------------- dashboard: delete confirm via AJAX ---------------- */
    document.body.addEventListener('click', (e) => {
      const del = e.target.closest('.js-confirm-delete');
      if (!del) return;
      if (!confirm(del.dataset.confirm || 'Are you sure?')) e.preventDefault();
    });
  });
})();
