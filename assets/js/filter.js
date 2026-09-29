// Unit filter (#uf) + search (#s), scoped to the active view only
(function () {
  var uf = document.getElementById('uf'), sf = document.getElementById('s');
  function activeView() { return document.querySelector('.view.on') || document.getElementById('sec1'); }
  function filt() {
    var u = uf.value, q = sf.value.trim();
    var v = activeView();
    document.querySelectorAll('.view .card').forEach(function (c) {
      var inV = (c.closest('.view') === v);
      var okU = (u === 'all' || c.dataset.unit === u || c.dataset.unit === '?');
      var okQ = (!q || (c.dataset.search || '').includes(q));
      c.style.display = (inV && okU && okQ) ? '' : 'none';
    });
    document.querySelectorAll('.view h3.grp').forEach(function (h) {
      var inV = (h.closest('.view') === v);
      var n = h.nextElementSibling, vis = false;
      while (n && !n.classList.contains('grp') && n.tagName !== 'H3') {
        if (n.classList && n.classList.contains('card') && n.style.display !== 'none') vis = true;
        n = n.nextElementSibling;
      }
      h.style.display = (inV && vis) ? '' : 'none';
    });
  }
  uf.addEventListener('change', filt);
  sf.addEventListener('input', filt);
  window.__refilter = filt;
})();
