// Per-group localized grading (MCQ only). ANSWERS consulted only here, on click.
(function () {
  document.querySelectorAll('.gradeBtn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var gid = btn.dataset.hgroup;
      var scope = btn.closest('.view');
      var cards = scope.querySelectorAll('.card.q[data-hgroup="' + gid + '"]');
      var total = 0, right = 0;
      cards.forEach(function (card) {
        var qid = (card.querySelector('.opts') || {}).dataset
          ? card.querySelector('.opts').dataset.qid : null;
        if (!qid || !(qid in ANSWERS)) return;
        var checked = card.querySelector('input[type=radio]:checked');
        total++;
        var ok = checked && parseInt(checked.value, 10) === ANSWERS[qid];
        if (ok) right++;
        card.querySelectorAll('.opt').forEach(function (o) { o.classList.remove('ok', 'bad'); });
        var labels = card.querySelectorAll('.opt');
        if (labels[ANSWERS[qid]]) labels[ANSWERS[qid]].classList.add('ok');
        if (checked && !ok) checked.closest('.opt').classList.add('bad');
      });
      var sc = scope.querySelector('.score[data-score="' + gid + '"]');
      if (sc) {
        var man = parseInt(sc.dataset.manual || '0', 10);
        var txt = total ? ('النتيجة: ' + right + ' / ' + total) : 'لا أسئلة اختيار قابلة للتصحيح في هذه المجموعة.';
        if (man) txt += ' (+' + man + ' تحتاج مراجعة يدوية — افتح عرض الإجابة تحت كل سؤال)';
        sc.textContent = txt;
      }
    });
  });
  // Scoped reset: clears only this data-hgroup (bacai:m:/bacai:e:), theme key untouched
  document.querySelectorAll('.resetBtn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (!window.confirm('هل أنت متأكد من مسح إجابات هذا القسم؟')) return;
      var gid = btn.dataset.hgroup;
      var scope = btn.closest('.view');
      scope.querySelectorAll('.card.q[data-hgroup="' + gid + '"]').forEach(function (card) {
        var opts = card.querySelector('.opts');
        if (opts && opts.dataset.qid) {
          try { localStorage.removeItem('bacai:m:' + opts.dataset.qid); } catch (e) {}
        }
        var ta = card.querySelector('textarea');
        if (ta && ta.dataset.qid) {
          try { localStorage.removeItem('bacai:e:' + ta.dataset.qid); } catch (e) {}
          ta.value = '';
        }
        card.querySelectorAll('input[type=radio]').forEach(function (r) { r.checked = false; });
        card.querySelectorAll('.opt').forEach(function (o) { o.classList.remove('ok', 'bad'); });
      });
      var sc = scope.querySelector('.score[data-score="' + gid + '"]');
      if (sc) sc.textContent = '';
    });
  });
})();
