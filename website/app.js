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

  const search = document.querySelector('[data-search]');
  const cards = [...document.querySelectorAll('[data-filter-card]')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  let category = 'all';
  const filterCards = () => {
    const query = (search?.value || '').trim().toLocaleLowerCase();
    let count = 0;
    for (const card of cards) {
      const matches = (category === 'all' || card.dataset.category === category) && card.dataset.search.toLocaleLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) count++;
    }
    const status = document.querySelector('[data-filter-status]');
    if (status) status.textContent = `${count} ${count === 1 ? 'recipe' : 'recipes'} to explore`;
    const empty = document.querySelector('[data-empty]');
    if (empty) empty.hidden = count !== 0;
  };
  search?.addEventListener('input', filterCards);
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    filterCards();
  }));
  document.querySelector('[data-reset]')?.addEventListener('click', () => {
    category = 'all';
    search.value = '';
    filters.forEach(item => item.setAttribute('aria-pressed', String(item.dataset.filter === 'all')));
    filterCards();
    search.focus();
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
