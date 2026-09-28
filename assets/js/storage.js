// localStorage persistence for Section 2 answers. Keys: bacai:m:<qid>, bacai:e:<qid>
(function () {
  var P = 'bacai:';
  document.querySelectorAll('#sec2 input[type=radio]').forEach(function (r) {
    var k = P + 'm:' + r.name;
    try { if (localStorage.getItem(k) === r.value) r.checked = true; } catch (e) {}
    r.addEventListener('change', function () { try { localStorage.setItem(k, r.value); } catch (e) {} });
  });
  document.querySelectorAll('#sec2 textarea').forEach(function (t) {
    var k = P + 'e:' + t.dataset.qid;
    try { var v = localStorage.getItem(k); if (v !== null) t.value = v; } catch (e) {}
    t.addEventListener('input', function () { try { localStorage.setItem(k, t.value); } catch (e) {} });
  });
})();
