// localStorage persistence for Section 2 answers. Keys: bacai:m:<qid>, bacai:e:<qid>
// Delegated: one listener per event type on #sec2 (512MB-friendly).
(function () {
  var P = 'bacai:';
  var sec = document.getElementById('sec2');
  sec.querySelectorAll('input[type=radio]').forEach(function (r) {
    var k = P + 'm:' + r.name;
    try { if (localStorage.getItem(k) === r.value) r.checked = true; } catch (e) {}
  });
  sec.querySelectorAll('textarea').forEach(function (t) {
    var k = P + 'e:' + t.dataset.qid;
    try { var v = localStorage.getItem(k); if (v !== null) t.value = v; } catch (e) {}
  });
  sec.addEventListener('change', function (ev) {
    var r = ev.target;
    if (!r || r.type !== 'radio' || !r.name) return;
    try { localStorage.setItem(P + 'm:' + r.name, r.value); } catch (e) {}
    var card = r.closest('.card.q');
    if (card) card.querySelectorAll('.opt').forEach(function (o) { o.classList.remove('ok', 'bad'); });
  });
  sec.addEventListener('input', function (ev) {
    var t = ev.target;
    if (!t || t.tagName !== 'TEXTAREA' || !t.dataset.qid) return;
    try { localStorage.setItem(P + 'e:' + t.dataset.qid, t.value); } catch (e) {}
  });
})();
