// SPA views: sidebar switching, hamburger, hash deep-link, mobile drawer.
// Sidebar collapses via body.sb-collapsed (slide animation); state in bacai:sb.
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('#sidebar button[data-view]'));
  var views = { 'الشرح': 'sec1', 'الأسئلة': 'sec2', 'الإجابات': 'sec3' };
  var burger = document.getElementById('burger');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('overlay');
  function isMobile() { return window.innerWidth <= 640; }
  function isCollapsed() { return document.body.classList.contains('sb-collapsed'); }
  function setCollapsed(collapsed, persist) {
    document.body.classList.toggle('sb-collapsed', collapsed);
    if (isMobile()) {
      if (collapsed) overlay.setAttribute('hidden', '');
      else overlay.removeAttribute('hidden');
    } else {
      overlay.setAttribute('hidden', '');
    }
    if (persist !== false) { try { localStorage.setItem('bacai:sb', collapsed ? 'closed' : 'open'); } catch (e) {} }
  }
  function openSb() { setCollapsed(false); }
  function closeSb() { setCollapsed(true); }
  try {
    if (localStorage.getItem('bacai:sb') === 'closed') setCollapsed(true, false);
  } catch (e) {}
  burger.addEventListener('click', function () {
    setCollapsed(!isCollapsed());
  });
  overlay.addEventListener('click', closeSb);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSb(); });
  function show(name, push) {
    links.forEach(function (b) { b.classList.toggle('on', b.dataset.view === name); });
    Object.keys(views).forEach(function (k) {
      var el = document.getElementById(views[k]);
      var on = (k === name);
      el.classList.toggle('on', on);
      if (on) el.removeAttribute('hidden'); else el.setAttribute('hidden', '');
    });
    if (push !== false) { try { location.hash = name; } catch (e) {} }
    overlay.setAttribute('hidden', '');
  }
  links.forEach(function (b) { b.addEventListener('click', function () { show(b.dataset.view); if (isMobile()) closeSb(); }); });
  window.addEventListener('hashchange', function () {
    var h = (location.hash || '').replace('#', '');
    if (views[decodeURIComponent(h)]) show(decodeURIComponent(h), false);
  });
  var init = decodeURIComponent((location.hash || '').replace('#', ''));
  show(views[init] ? init : 'الشرح', false);
  window.__showView = show;
})();
