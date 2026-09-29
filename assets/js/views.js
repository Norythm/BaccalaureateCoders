// SPA views: sidebar switching, hamburger, hash deep-link, mobile drawer
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('#sidebar button[data-view]'));
  var views = { 'الشرح': 'sec1', 'الأسئلة': 'sec2', 'الإجابات': 'sec3' };
  var burger = document.getElementById('burger');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('overlay');
  function openSb() { sidebar.removeAttribute('hidden'); overlay.removeAttribute('hidden'); }
  function closeSb() { if (window.innerWidth <= 640) { sidebar.setAttribute('hidden', ''); overlay.setAttribute('hidden', ''); } }
  burger.addEventListener('click', function () {
    if (sidebar.hasAttribute('hidden')) openSb(); else closeSb();
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
    if (window.innerWidth > 640) { sidebar.removeAttribute('hidden'); overlay.setAttribute('hidden', ''); }
  }
  links.forEach(function (b) { b.addEventListener('click', function () { show(b.dataset.view); closeSb(); }); });
  window.addEventListener('hashchange', function () {
    var h = (location.hash || '').replace('#', '');
    if (views[decodeURIComponent(h)]) show(decodeURIComponent(h), false);
  });
  var init = decodeURIComponent((location.hash || '').replace('#', ''));
  show(views[init] ? init : 'الشرح', false);
  window.__showView = show;
})();
