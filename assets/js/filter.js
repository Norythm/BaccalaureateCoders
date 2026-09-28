// Unit filter (#uf) + search (#s) for all cards
(function () {
  var uf = document.getElementById('uf'), sf = document.getElementById('s');
  function filt() {
    var u = uf.value, q = sf.value.trim();
    document.querySelectorAll('main .card').forEach(function (c) {
      var okU = (u === 'all' || c.dataset.unit === u || c.dataset.unit === '?');
      var okQ = (!q || (c.dataset.search || '').includes(q));
      c.style.display = (okU && okQ) ? '' : 'none';
    });
    document.querySelectorAll('h3.grp').forEach(function (h) {
      var n = h.nextElementSibling, vis = false;
      while (n && !n.classList.contains('grp') && n.tagName !== 'H3') {
        if (n.classList && n.classList.contains('card') && n.style.display !== 'none') vis = true;
        n = n.nextElementSibling;
      }
      h.style.display = vis ? '' : 'none';
    });
  }
  uf.addEventListener('change', filt);
  sf.addEventListener('input', filt);
})();
