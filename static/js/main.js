/* Isha's Return Gifts — Main JS v4 */
document.addEventListener('DOMContentLoaded', () => {

  /* Sticky header */
  const header = document.getElementById('siteHeader');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  /* Search expand/collapse */
  window.toggleSearch = function () {
    const wrap = document.getElementById('searchWrap');
    const field = document.getElementById('searchField');
    if (!wrap) return;
    wrap.classList.toggle('open');
    if (wrap.classList.contains('open')) setTimeout(() => field && field.focus(), 60);
  };
  document.addEventListener('click', (e) => {
    const wrap = document.getElementById('searchWrap');
    const btn = document.querySelector('.search-icon-btn');
    if (wrap && !wrap.contains(e.target) && e.target !== btn) wrap.classList.remove('open');
  });

  /* Mobile menu */
  window.toggleMobileMenu = function () {
    const menu = document.getElementById('mobileMenu');
    const btn = document.getElementById('mobileMenuBtn');
    if (!menu || !btn) return;
    menu.classList.toggle('open');
    btn.classList.toggle('active');
  };
  window.closeMobileMenu = function () {
    const menu = document.getElementById('mobileMenu');
    const btn = document.getElementById('mobileMenuBtn');
    if (menu) menu.classList.remove('open');
    if (btn) btn.classList.remove('active');
  };

  /* Auto-dismiss alerts */
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      try { bootstrap.Alert.getOrCreateInstance(el).close(); } catch (e) {}
    }, 4500);
  });

  /* Scroll animations */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 65);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll(
    '.product-card,.why-card,.testimonial-card,.category-card,.section-header,.trust-item'
  ).forEach(el => { el.classList.add('animate-on-scroll'); io.observe(el); });

  /* Cart qty auto-submit */
  document.querySelectorAll('.qty-input').forEach(input => {
    input.addEventListener('change', function () { this.closest('form')?.submit(); });
  });

  /* Smooth scroll anchors */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const href = a.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) { e.preventDefault(); closeMobileMenu(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });

  /* Active nav highlight */
  const path = window.location.pathname;
  document.querySelectorAll('.hn-link,.mobile-nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#' && path === href) {
      link.style.color = 'var(--rose)';
      link.style.background = 'var(--rose-pale)';
    }
  });

  /* Image error fallback */
  document.querySelectorAll('img.product-img').forEach(img => {
    img.addEventListener('error', function () { this.style.display = 'none'; });
  });

});
