(() => {
  'use strict';
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav');
  const closeMenu = () => {
    nav.dataset.open = 'false';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = 'Menu +';
  };
  toggle?.addEventListener('click', () => {
    const open = nav.dataset.open !== 'true';
    nav.dataset.open = String(open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? 'Close −' : 'Menu +';
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav?.dataset.open === 'true') {
      closeMenu();
      toggle.focus();
    }
  });
  document.addEventListener('click', event => {
    if (nav?.dataset.open === 'true' && !event.target.closest('.site-header')) closeMenu();
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const carousels = [...document.querySelectorAll('[data-carousel]')].map((carousel, index) => {
    const track = carousel.querySelector('[data-carousel-track]');
    const previous = carousel.querySelector('[data-carousel-prev]');
    const next = carousel.querySelector('[data-carousel-next]');
    const position = carousel.querySelector('[data-carousel-status]');
    if (!track || !previous || !next) return null;

    const slides = [...track.querySelectorAll('.recipe-card')];
    track.id ||= `recipe-carousel-track-${index + 1}`;
    track.setAttribute('role', 'group');
    previous.setAttribute('aria-controls', track.id);
    next.setAttribute('aria-controls', track.id);
    if (position) position.setAttribute('aria-atomic', 'true');

    const instructions = document.createElement('p');
    instructions.id = `${track.id}-instructions`;
    instructions.className = 'carousel-sr-only';
    instructions.textContent = 'Use the left and right arrow keys to browse recipes, Home for the first recipes, and End for the last. You can also swipe or scroll horizontally.';
    carousel.append(instructions);
    track.setAttribute('aria-describedby', [track.getAttribute('aria-describedby'), instructions.id].filter(Boolean).join(' '));

    let frame = 0;
    let announcePosition = false;
    let scrollTimer;
    const visibleSlides = () => slides.filter(slide => !slide.hidden);
    const maxScroll = () => Math.max(0, track.scrollWidth - track.clientWidth);

    const update = (announce = true) => {
      const available = visibleSlides();
      carousel.hidden = available.length === 0;
      previous.disabled = !available.length || track.scrollLeft <= 2;
      next.disabled = !available.length || track.scrollLeft >= maxScroll() - 2;
      if (!position || !announce || !available.length || !track.clientWidth) return;

      const viewport = track.getBoundingClientRect();
      const shown = available.reduce((indices, slide, slideIndex) => {
        const bounds = slide.getBoundingClientRect();
        const overlap = Math.min(bounds.right, viewport.right) - Math.max(bounds.left, viewport.left);
        if (overlap >= Math.min(bounds.width, viewport.width) / 2) indices.push(slideIndex);
        return indices;
      }, []);
      if (!shown.length) return;
      const first = shown[0] + 1;
      const last = shown[shown.length - 1] + 1;
      const range = first === last ? String(first) : `${first}\u2013${last}`;
      const label = `${range} of ${available.length} ${available.length === 1 ? 'recipe' : 'recipes'}`;
      if (position.textContent !== label) position.textContent = label;
    };

    const scheduleUpdate = (announce = false) => {
      announcePosition ||= announce;
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        update(announcePosition);
        announcePosition = false;
      });
    };

    const scrollTo = left => {
      track.scrollTo({
        left: Math.max(0, Math.min(left, maxScroll())),
        behavior: reducedMotion.matches ? 'auto' : 'smooth'
      });
      scheduleUpdate(true);
    };

    const move = direction => {
      const available = visibleSlides();
      if (!available.length) return;
      const viewport = track.getBoundingClientRect();
      const padding = parseFloat(getComputedStyle(track).paddingLeft) || 0;
      const offsets = available.map(slide => track.scrollLeft + slide.getBoundingClientRect().left - viewport.left - track.clientLeft - padding);
      const nearest = offsets.reduce((best, offset, slideIndex) => Math.abs(offset - track.scrollLeft) < Math.abs(offsets[best] - track.scrollLeft) ? slideIndex : best, 0);
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      const stride = available[0].getBoundingClientRect().width + gap;
      const perPage = Math.max(1, Math.floor((track.clientWidth + gap) / stride));
      const target = Math.max(0, Math.min(nearest + direction * perPage, available.length - 1));
      scrollTo(offsets[target]);
    };

    previous.addEventListener('click', () => move(-1));
    next.addEventListener('click', () => move(1));
    track.addEventListener('keydown', event => {
      if (event.target !== track || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      if (event.key === 'Home') scrollTo(0);
      else if (event.key === 'End') scrollTo(maxScroll());
      else move(event.key === 'ArrowRight' ? 1 : -1);
    });
    track.addEventListener('scroll', () => {
      scheduleUpdate();
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(() => scheduleUpdate(true), 150);
    }, { passive: true });
    track.addEventListener('scrollend', () => {
      clearTimeout(scrollTimer);
      scheduleUpdate(true);
    });
    if ('ResizeObserver' in window) new ResizeObserver(() => scheduleUpdate(true)).observe(track);
    else window.addEventListener('resize', () => scheduleUpdate(true));

    const refresh = (reset = false) => {
      carousel.hidden = visibleSlides().length === 0;
      if (reset) {
        clearTimeout(scrollTimer);
        track.scrollTo({ left: 0, behavior: 'auto' });
      }
      update();
      scheduleUpdate(true);
    };
    refresh();
    return { refresh };
  }).filter(Boolean);

  const search = document.querySelector('[data-search]');
  const cards = [...document.querySelectorAll('[data-filter-card]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  let category = 'all';
  const filterCards = () => {
    const query = (search?.value || '').trim().toLocaleLowerCase();
    let count = 0;
    for (const card of cards) {
      const matches = (category === 'all' || card.dataset.category === category) && (card.dataset.search || card.textContent).toLocaleLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) count++;
    }
    const status = document.querySelector('[data-filter-status]');
    if (status) status.textContent = `${count} ${count === 1 ? 'recipe' : 'recipes'} to explore`;
    const empty = document.querySelector('[data-empty]');
    if (empty) empty.hidden = count !== 0;
    carousels.forEach(carousel => carousel.refresh(true));
  };
  search?.addEventListener('input', filterCards);
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    filterCards();
  }));
  document.querySelector('[data-reset]')?.addEventListener('click', () => {
    category = 'all';
    if (search) search.value = '';
    filters.forEach(item => item.setAttribute('aria-pressed', String(item.dataset.filter === 'all')));
    filterCards();
    search?.focus();
  });
  document.querySelectorAll('[data-disclosures]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('.health-reading').forEach(section => { section.open = button.dataset.disclosures === 'open'; });
  }));
  document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
  window.addEventListener('hashchange', () => {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target?.tagName === 'DETAILS') target.open = true;
  });
})();
