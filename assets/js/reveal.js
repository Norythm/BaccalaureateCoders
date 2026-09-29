// Per-question reveal: clones the Section 3 answer block inline (read on click only).
// Essay: side-by-side model answer + keyword-overlap hint (approximate, not a grade).
(function () {
  function toks(s) {
    var t = (s || '').normalize('NFKC');
    var words = t.match(/[\w\u0600-\u06FF]+/g) || [];
    var out = [];
    words.forEach(function (w) {
      if (AR_STOP.indexOf(w) !== -1 || w.length < 3) return;
      if (out.indexOf(w) === -1) out.push(w);
    });
    return out;
  }
  document.getElementById('sec2').addEventListener('click', function (ev) {
    var btn = ev.target.closest ? ev.target.closest('.revealBtn') : null;
    if (!btn || !btn.dataset.qid) return;
    var qid = btn.dataset.qid;
    var card = btn.closest('.card.q');
    var panel = card.querySelector('.reveal');
    if (!panel.classList.contains('open')) {
      var src = document.querySelector('#sec3 .card.a[data-qid="' + qid + '"] .ans');
      var body = '<div><b>نموذج الإجابة:</b> ' + (src ? src.innerHTML : '—') + '</div>';
      var ta = card.querySelector('textarea');
      if (ta) {
        var model = src ? src.textContent : '';
        var uw = toks(ta.value), mw = toks(model);
        var hit = 0;
        uw.forEach(function (w) { if (mw.indexOf(w) !== -1) hit++; });
        var pct = uw.length ? Math.round(100 * hit / uw.length) : 0;
        body += '<div class="hint">كلمات مشتركة مع النموذج: ' + pct + '% — مؤشر تقريبي للمذاكرة وليس درجة.</div>';
      }
      panel.innerHTML = '<div><div class="revealBody">' + body + '</div></div>';
      panel.removeAttribute('hidden');
      requestAnimationFrame(function () { panel.classList.add('open'); });
      btn.textContent = 'إخفاء الإجابة';
    } else {
      panel.classList.remove('open');
      panel.setAttribute('hidden', '');
      panel.innerHTML = '';
      btn.textContent = 'عرض الإجابة';
    }
  });
})();
