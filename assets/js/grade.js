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
      if (sc) sc.textContent = total ? ('النتيجة: ' + right + ' / ' + total) : 'لا أسئلة اختيار قابلة للتصحيح في هذه المجموعة.';
    });
  });
})();
