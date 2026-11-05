/* Shared navigation controller. Labels are prepended from saved translations. */
(() => {
  const scriptRoot = new URL('.', document.currentScript.src);
  const css = document.createElement('link');
  css.rel = 'stylesheet'; css.href = new URL('service-package-overviews.css', scriptRoot);
  document.head.append(css);
  document.documentElement.dataset.navigationReady = 'true';
  const init = () => {
    const nav = document.querySelector('.pt-header .pt-nav');
    if (!nav || nav.dataset.organizedNavigation) return;
    const locale = document.documentElement.dataset.staticLocale || 'en';
    const labels = window.PAPER_TRAIL_SERVICE_MENU[locale] || window.PAPER_TRAIL_SERVICE_MENU.en;
    const root = new URL('../', scriptRoot);
    const path = name => new URL((locale === 'en' ? '' : locale + '/') + name, root).href;
    const kinds = ['weekly-bookkeeping', 'monthly-bookkeeping', 'bookkeeping-repair', 'accounts-billing', 'financial-analysis', 'payroll'];
    const names = ['Weekly Bookkeeping', 'Monthly Bookkeeping', 'Bookkeeping Repair', 'Accounts & Billing', 'Financial Analysis', 'Payroll'];
    const services = ['weekly-bookkeeping.html', 'paper-trail-monthly-bookkeeping.html', 'paper-trail-services.html', 'accounts-billing.html', 'financial-analysis.html', 'payroll.html'];
    function link(name, route) {
      const a = document.createElement('a'); a.href = path(route); a.textContent = labels[name];
      if (new URL(a.href).pathname === location.pathname) a.setAttribute('aria-current', 'page');
      return a;
    }
    nav.replaceChildren(); nav.dataset.organizedNavigation = 'true';
    const groups = [];
    function family(name, overview, routes) {
      const group = document.createElement('div'); group.className = 'nav-family';
      const a = link(name, overview), panel = document.createElement('div');
      panel.className = 'nav-panel'; panel.id = 'navigation-' + name.toLowerCase(); panel.hidden = true;
      a.setAttribute('aria-haspopup', 'true'); a.setAttribute('aria-controls', panel.id); a.setAttribute('aria-expanded', 'false');
      panel.append(link('All ' + name, overview), ...routes.map((r, i) => link(names[i], r)));
      group.append(a, panel); nav.append(group); groups.push({group, a, panel});
    }
    nav.append(link('Home', 'index.html'), link('About', 'about.html'));
    family('Services', 'all-services.html', services);
    family('Packages', 'packages.html', kinds.map(k => k + '-packages.html'));
    nav.append(link('Bundle & Save', 'all-bundles.html'), link('Notes', 'notes.html'), link('Blog', 'blog.html'), link('Contact Us', 'areas-we-serve.html'));
    let timer, touch = false;
    const close = () => { clearTimeout(timer); groups.forEach(({a, panel}) => { panel.hidden = true; a.setAttribute('aria-expanded', 'false'); }); };
    const open = current => { close(); current.panel.hidden = false; current.a.setAttribute('aria-expanded', 'true'); };
    groups.forEach(current => {
      const {group, a, panel} = current;
      group.addEventListener('pointerenter', e => { clearTimeout(timer); if (e.pointerType === 'mouse') open(current); });
      group.addEventListener('pointerleave', e => { if (e.pointerType === 'mouse') timer = setTimeout(close, 180); });
      a.addEventListener('pointerdown', e => { touch = e.pointerType === 'touch' || e.pointerType === 'pen'; });
      a.addEventListener('click', e => {
        if (touch || matchMedia('(hover:none)').matches) { e.preventDefault(); panel.hidden ? open(current) : close(); }
        touch = false;
      });
      a.addEventListener('keydown', e => { if (e.key === 'ArrowDown' || e.key === ' ') { e.preventDefault(); open(current); panel.querySelector('a').focus(); } });
      group.addEventListener('focusout', e => { if (!group.contains(e.relatedTarget)) close(); });
    });
    nav.querySelectorAll(':scope > a').forEach(a => a.addEventListener('pointerenter', close));
    document.addEventListener('pointerdown', e => { if (!nav.contains(e.target)) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { const current = groups.find(g => !g.panel.hidden); if (current) { current.a.focus(); close(); } } });
    addEventListener('resize', close);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
