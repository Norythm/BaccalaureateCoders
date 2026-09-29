// Wiring: theme toggle + print (active view only via CSS)
(function () {
  var root = document.documentElement;
  try {
    var t = localStorage.getItem('bacai:theme');
    if (t === 'dark' || t === 'light') root.setAttribute('data-theme', t);
  } catch (e) {}
  document.getElementById('themeBtn').addEventListener('click', function () {
    var cur = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', cur);
    try { localStorage.setItem('bacai:theme', cur); } catch (e) {}
  });
  document.getElementById('printBtn').addEventListener('click', function () { window.print(); });
})();
