# -*- coding: utf-8 -*-
"""Build split-file study page: index.html + assets/css + assets/js."""
import sys, re, html, json
sys.path.insert(0, '/media/Games/Programming/site')
from data_lessons_u1 import LESSONS_U1
from data_book_u1 import BOOK_U1, KHAWARIZMI_U1
from data_lessons_u2 import LESSONS_U2, BOOK_U2, KHAWARIZMI_U2
from data_lessons_u34 import LESSONS_U34, BOOK_U34, KHAWARIZMI_U34
from data_review import REVIEW_ESSAY, REVIEW_MCQ
from justify_review import JUST_REVIEW
from justify_kh12 import JUST_KH12
from justify_kh34 import JUST_KH34
from justify_khfree import JUST_KHFREE
from justify_book12 import JUST_BOOK12
from justify_book34 import JUST_BOOK34

LETTERS = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح"]
JUST_ALL = {}
JUST_ALL.update(JUST_REVIEW)
JUST_ALL.update(JUST_KH12)
JUST_ALL.update(JUST_KH34)
JUST_ALL.update(JUST_KHFREE)
JUST_ALL.update(JUST_BOOK12)
JUST_ALL.update(JUST_BOOK34)

def esc(s):
    return html.escape(str(s), quote=True)

def strip_label(opt):
    t = re.sub(r'^\s*[أبجدهـوزح]\s*[\)\.\-:：]?\s*', '', str(opt).strip())
    return t if t else str(opt).strip()

def norm_q(q, sec):
    qid = q["qid"]
    lesson = q.get("lesson", "")
    kind = q.get("kind", "mcq" if "opts" in q and q["opts"] else "essay")
    if sec == "REV-MCQ":
        kind = "mcq"
    elif sec == "REV-ESS":
        kind = "essay"
    text = q["text"]
    raw_opts = list(q.get("opts") or [])
    opts = [strip_label(o) for o in raw_opts]
    ans = (q["answer"] or "").strip()
    # resolve correct option index for single-answer MCQ
    cidx = None
    if kind == "mcq":
        if sec == "REV-MCQ" and ans in LETTERS and opts:
            cidx = LETTERS.index(ans)
        elif ans in LETTERS and opts:
            cidx = LETTERS.index(ans) if LETTERS.index(ans) < len(opts) else None
        else:
            # free-form: answer starts with letter, or matches an option
            m = re.match(r'^([أبجدهـ])\s', ans)
            if m and m.group(1) in LETTERS and LETTERS.index(m.group(1)) < len(opts):
                cidx = LETTERS.index(m.group(1))
            else:
                for i, o in enumerate(opts):
                    if o and (o == ans or ans.startswith(o[:24]) or o.startswith(ans[:24])):
                        cidx = i
                        break
    return dict(qid=qid, lesson=lesson, kind=kind, text=text, opts=opts,
                answer=ans, cidx=cidx,
                evidence=q.get("evidence", ""), src=q.get("src", ""), sec=sec)

LESSONS = LESSONS_U1 + LESSONS_U2 + LESSONS_U34
assert len(LESSONS) == 14, len(LESSONS)
LESSON_TITLE = {L["code"]: L["title"] for L in LESSONS}

RAW = (
    [norm_q(q, "REV-MCQ") for q in REVIEW_MCQ] +
    [norm_q(q, "REV-ESS") for q in REVIEW_ESSAY] +
    [norm_q(q, "B1") for q in BOOK_U1] +
    [norm_q(q, "K1") for q in KHAWARIZMI_U1] +
    [norm_q(q, "B2") for q in BOOK_U2] +
    [norm_q(q, "K2") for q in KHAWARIZMI_U2] +
    [norm_q(q, "B34") for q in BOOK_U34] +
    [norm_q(q, "K34") for q in KHAWARIZMI_U34]
)
assert len(RAW) == 357, len(RAW)
assert len({q["qid"] for q in RAW}) == 357

UNIT_OF = {L["code"]: L["unit"] for L in LESSONS}
def unit_of(q):
    return UNIT_OF.get(q["lesson"], "?")

# ---------- hierarchical regroup ----------
# 14 lesson groups (lesson field) + 1 unit group (Unit 1 review banks) .
# Scan found zero cross-unit and zero unit-comprehensive questions
# (5 keyword hits were false positives), so Units 2-4 unit groups and the
# general group are intentionally empty and omitted.
ORDER = ["1-1", "1-2", "1-3", "1-4", "2-1", "2-2", "2-3",
         "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4"]
by_lesson = {c: [] for c in ORDER}
unit1_review = []
ambiguous = []
for q in RAW:
    if q["sec"] in ("REV-MCQ", "REV-ESS"):
        unit1_review.append(q)
    elif q["lesson"] in by_lesson:
        by_lesson[q["lesson"]].append(q)
    else:
        ambiguous.append(q["qid"])
assert not ambiguous, ambiguous

HGROUPS = []
for c in ORDER:
    qs = by_lesson[c]
    HGROUPS.append((f"أسئلة الدرس {c}", "lesson", c, qs))
HGROUPS.append(("أسئلة الوحدة الأولى (مراجعة شاملة)", "unit", "1", unit1_review))

n_h = sum(len(qs) for _, _, _, qs in HGROUPS)
assert n_h == 357, n_h
ALLQ = [q for _, _, _, qs in HGROUPS for q in qs]

# gradeable = mcq with resolved single correct index AND justification entry
gradeable = {q["qid"] for q in ALLQ if q["kind"] == "mcq" and q["cidx"] is not None and q["qid"] in JUST_ALL}
n_grad_mcq = sum(1 for q in ALLQ if q["kind"] == "mcq" and q["qid"] in gradeable)
print("gradeable MCQ: %d / %d" % (n_grad_mcq, sum(1 for q in ALLQ if q["kind"] == "mcq")))

KIND_AR = {"mcq": "اختيار من متعدد", "essay": "مقالي"}

# ---------- Section 1 (unchanged) ----------
s1 = []
for L in LESSONS:
    goals = "".join(f"<li>{esc(g)}</li>" for g in L["goals"])
    cons = "".join(f"<li><b>{esc(t)}</b> — {esc(d)}</li>" for t, d in L["concepts"])
    pts = "".join(f"<li>{esc(p)}</li>" for p in L["points"])
    terms = "".join(f"<span class='term'>{esc(t)}</span>" for t in L["terms"])
    s1.append(f"""<details class="card lesson" data-unit="{esc(L['unit'])}" data-search="{esc(L['title']+' '+' '.join(L['terms']))}">
<summary><span class="badge">الوحدة {esc(L['unit'])}</span> <span class="badge code">الدرس {esc(L['code'])}</span> <b>{esc(L['title'])}</b></summary>
<div class="body">
<h4>أهداف التعلم</h4><ul>{goals}</ul>
<h4>المفاهيم الأساسية</h4><ul>{cons}</ul>
<h4>الفكرة الرئيسية</h4><p class="idea">{esc(L['idea'])}</p>
<h4>الشرح</h4><ul class="points">{pts}</ul>
<h4>المصطلحات المفتاحية</h4><div class="terms">{terms}</div>
<div class="src">المصدر: {esc(L['src'])}</div>
</div></details>""")
SEC1 = "\n".join(s1)

# ---------- Section 2 (hierarchical, data-qid only, per-group grade buttons) ----------
def gid_of(gkind, gkey):
    return f"g-{gkind}-{gkey}".replace(" ", "_")

s2 = []
for gtitle, gkind, gkey, qs in HGROUPS:
    gid = gid_of(gkind, gkey)
    nmcq = sum(1 for q in qs if q["kind"] == "mcq" and q["qid"] in gradeable)
    ness = sum(1 for q in qs if q["kind"] == "essay")
    cards = []
    for q in qs:
        if q["kind"] == "mcq":
            opts = "".join(
                f"""<label class="opt"><input type="radio" name="{esc(q['qid'])}" value="{i}"><span class="ol">{LETTERS[i]}</span><span>{esc(o)}</span></label>"""
                for i, o in enumerate(q["opts"]))
            inner = f"<div class='opts' data-qid='{esc(q['qid'])}'>{opts}</div>"
        else:
            inner = f"<textarea data-qid='{esc(q['qid'])}' rows='4' placeholder='اكتب إجابتك هنا'></textarea>"
        cards.append(f"""<div class="card q" data-unit="{esc(unit_of(q))}" data-hgroup="{esc(gid)}" data-search="{esc(q['text'])}">
<div class="qhead"><span class="qid">{esc(q['qid'])}</span><span class="ktag">{KIND_AR[q['kind']]}</span><span class="ltag">الدرس {esc(q['lesson'])}</span></div>
<p class="qtext">{esc(q['text'])}</p>{inner}
</div>""")
    grade_btn = ""
    if nmcq:
        grade_btn = (f"<button class='gradeBtn' data-hgroup='{esc(gid)}' type='button'>عرض الحل الصحيح لإجاباتي</button>"
                     f"<button class='resetBtn' data-hgroup='{esc(gid)}' type='button'>مسح إجاباتي وإعادة المحاولة</button>"
                     f"<span class='score' data-score='{esc(gid)}'></span>"
                     f"<div class='enote'>التصحيح الآلي للاختيار من متعدد فقط ({nmcq} سؤالا) — المقالية ({ness}) للمذاكرة الذاتية.</div>")
    s2.append(f"<h3 class='grp' data-hgroup-head='{esc(gid)}'>{esc(gtitle)} <span class='cnt'>({len(qs)})</span><br>{grade_btn}</h3>\n" + "\n".join(cards))
SEC2 = "\n".join(s2)

# ---------- Section 3 (mirrors Section 2, MCQ justifications) ----------
NOTE = "تنبيه: لا توجد إجابات نموذجية داخل المستندات الأربعة (نسخ المراجعة نسخ طالب بإجابات فارغة) — جميع الإجابات أدناه مستنتجة من شرح الدروس ومقرونة بالدليل."
s3 = [f"<div class='note'>{esc(NOTE)}</div>"]
for gtitle, gkind, gkey, qs in HGROUPS:
    gid = gid_of(gkind, gkey)
    cards = []
    for q in qs:
        if q["kind"] == "mcq" and q["qid"] in JUST_ALL:
            j = JUST_ALL[q["qid"]]
            why = j.get("why", "")
            wrongs = list(j.get("wrong", []))
            # align wrong clauses to distractor indices:
            # non-amb: wrong list excludes correct index -> splice it back in order
            # amb: list may be generic per-option or shorter -> pad
            n = len(q["opts"])
            per = [""] * n
            if q["cidx"] is not None and not j.get("amb", False) and len(wrongs) == n - 1:
                wi = 0
                for i in range(n):
                    if i == q["cidx"]:
                        continue
                    per[i] = wrongs[wi]
                    wi += 1
            else:
                for i in range(min(n, len(wrongs))):
                    per[i] = wrongs[i]
            witems = "".join(
                f"<li><b>{LETTERS[i]}:</b> {esc(per[i] or '—')}</li>"
                for i in range(n) if i != q["cidx"])
            ctext = q["opts"][q["cidx"]] if q["cidx"] is not None and q["cidx"] < n else q["answer"]
            clet = LETTERS[q["cidx"]] if q["cidx"] is not None and q["cidx"] < len(LETTERS) else ""
            ans_show = (f"الإجابة: {esc(clet)} — {esc(ctext)}"
                        f"<div class='why'><b>لماذا هي صحيحة؟</b> {esc(why)}</div>"
                        f"<div class='why'><b>لماذا الباقي خطأ؟</b><ul>{witems}</ul></div>")
        elif q["kind"] == "mcq":
            ans_show = esc(q["answer"])
        else:
            ans_show = esc(q["answer"])
        cards.append(f"""<div class="card a" data-unit="{esc(unit_of(q))}" data-hgroup="{esc(gid)}" data-search="{esc(q['qid']+' '+q['text'])}">
<div class="qhead"><span class="qid">{esc(q['qid'])}</span><span class="ltag">الدرس {esc(q['lesson'])}</span><span class="der">لا توجد إجابة نموذجية في المستندات — الإجابة مستنتجة من شرح الدرس {esc(q['lesson'])}</span></div>
<p class="qtext">{esc(q['text'])}</p>
<div class="ans"><b>نموذج الإجابة:</b> {ans_show}</div>
<div class="ev"><b>الدليل:</b> {esc(q['evidence'])}</div>
<div class="src">المصدر: {esc(q['src'])}</div></div>""")
    s3.append(f"<h3 class='grp' data-hgroup-head='{esc(gid)}'>{esc(gtitle)} <span class='cnt'>({len(qs)})</span></h3>\n" + "\n".join(cards))
SEC3 = "\n".join(s3)

# ---------- answers.js (correctness data, read only on grade click) ----------
ANS = {}
for q in ALLQ:
    if q["kind"] == "mcq" and q["qid"] in gradeable:
        ANS[q["qid"]] = q["cidx"]
ANS_JS = "var ANSWERS = " + json.dumps(ANS, ensure_ascii=False) + ";"

CSS = """:root{
  --paper:#eef3f9;
  --card:#f7fafd;
  --ink:#1e2a3a;
  --muted:#5b6b82;
  --line:#c9d6e6;
  --accent:#2563a8;
  --accent-ink:#ffffff;
  --accent-soft:#e2ecf7;
  --warn-bg:#fdf6e3;
  --warn-line:#c9a227;
  --ans-bg:#eaf3fb;
  --ans-line:#2563a8;
  --ok-bg:#e9f4ec;
  --ok-line:#2e7d32;
  --bad-bg:#fbecec;
  --bad-line:#b3261e;
}
[data-theme="dark"]{
  --paper:#101a2a;
  --card:#16263c;
  --ink:#dbe6f4;
  --muted:#93a5bd;
  --line:#2c425f;
  --accent:#5ea0e6;
  --accent-ink:#0b1626;
  --accent-soft:#1d3350;
  --warn-bg:#2a2410;
  --warn-line:#c9a227;
  --ans-bg:#14293f;
  --ans-line:#5ea0e6;
  --ok-bg:#123324;
  --ok-line:#6fce7f;
  --bad-bg:#3a1414;
  --bad-line:#ef8a80;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.9;font-family:'Segoe UI',Tahoma,'Noto Kufi Arabic','Noto Naskh Arabic',Arial,sans-serif;font-variant-numeric:tabular-nums}
header{background:var(--card);border-bottom:1px solid var(--line);padding:1.2rem 3.2rem 1.2rem 1rem;text-align:center}
header h1{margin:0 0 .3rem;font-size:1.35rem}
header .sub{color:var(--muted);font-size:.95rem}
#burger{position:absolute;top:.9rem;right:.9rem;font-size:1.3rem;line-height:1;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.35rem .7rem;cursor:pointer;font-family:inherit}
#overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:19}
#overlay[hidden]{display:none}
#sidebar{position:fixed;top:0;right:0;height:100%;width:250px;background:var(--card);border-left:1px solid var(--line);z-index:20;padding:1rem;display:flex;flex-direction:column;gap:.6rem}
#sidebar[hidden]{display:none}
#sidebar h2{margin:0 0 .4rem;font-size:1.05rem}
#sidebar button{font-family:inherit;font-size:1rem;text-align:right;background:var(--paper);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.5rem .8rem;cursor:pointer}
#sidebar button.on{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.toolbar{display:flex;gap:.5rem;justify-content:center;padding:.8rem;flex-wrap:wrap;background:var(--card);border-bottom:1px solid var(--line)}
.toolbar input,.toolbar select,.toolbar button{padding:.45rem .8rem;border-radius:6px;border:1px solid var(--line);font-size:1rem;font-family:inherit;background:var(--card);color:var(--ink)}
.toolbar button{background:var(--accent);color:var(--accent-ink);border:1px solid var(--accent);cursor:pointer}
main{max-width:1000px;margin:auto;padding:1rem}
.view[hidden]{display:none}
section{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1rem;margin-bottom:1.5rem}
h2.sec{border-right:4px solid var(--accent);padding-right:.6rem;margin-top:0}
h3.grp{background:var(--accent-soft);border:1px solid var(--line);padding:.4rem .8rem;border-radius:6px}
.card{border:1px solid var(--line);border-radius:6px;padding:.7rem;margin:.7rem 0;background:var(--card)}
details.lesson{margin:.7rem 0}
details.lesson summary{cursor:pointer;font-size:1.05rem;list-style-position:inside;margin:0}
details.lesson summary::marker{color:var(--accent)}
details.lesson .body{margin-top:.6rem}
.badge{border:1px solid var(--line);background:var(--accent-soft);border-radius:4px;padding:.05rem .7rem;font-size:.85rem}
.badge.code{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.idea{background:var(--warn-bg);border-right:4px solid var(--warn-line);padding:.5rem .8rem;border-radius:4px}
.terms{display:flex;flex-wrap:wrap;gap:.4rem}
.term{background:var(--paper);border:1px solid var(--line);border-radius:4px;padding:.05rem .7rem;font-size:.9rem}
.src{color:var(--muted);font-size:.85rem;margin-top:.5rem}
.qid{border:1px solid var(--line);background:var(--paper);border-radius:4px;padding:.05rem .6rem;font-size:.85rem;direction:ltr;display:inline-block}
.ktag{background:var(--accent-soft);border:1px solid var(--line);border-radius:4px;padding:.05rem .6rem;font-size:.85rem}
.ltag{background:var(--paper);border:1px solid var(--line);border-radius:4px;padding:.05rem .6rem;font-size:.85rem}
.qhead{display:flex;gap:.4rem;flex-wrap:wrap;align-items:center}
.opts{display:flex;flex-direction:column;gap:.4rem;margin:.5rem 0}
.opt{display:flex;gap:.5rem;align-items:flex-start;border:1px solid var(--line);border-radius:6px;padding:.4rem .6rem;cursor:pointer;background:var(--card)}
.ol{border:1px solid var(--line);background:var(--paper);min-width:1.7rem;height:1.7rem;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-size:.9rem}
.opt.ok{border-color:var(--ok-line);background:var(--ok-bg)}
.opt.bad{border-color:var(--bad-line);background:var(--bad-bg)}
textarea{width:100%;border:1px solid var(--line);border-radius:6px;padding:.5rem;font-family:inherit;font-size:1rem;background:var(--card);color:var(--ink)}
.ans{background:var(--ans-bg);border-right:4px solid var(--ans-line);padding:.5rem .8rem;border-radius:4px;margin:.4rem 0}
.why{margin-top:.4rem}
.why ul{margin:.3rem 0;padding-right:1.2rem}
.ev{background:var(--paper);border:1px solid var(--line);padding:.4rem .8rem;border-radius:4px;font-size:.92rem}
.note{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:6px;padding:.6rem 1rem;margin-bottom:1rem}
.cnt{color:var(--muted);font-size:.9rem}
.der{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:4px;padding:.05rem .6rem;font-size:.8rem}
.gradeBtn{font-family:inherit;font-size:.9rem;background:var(--accent);color:var(--accent-ink);border:1px solid var(--accent);border-radius:6px;padding:.3rem .9rem;cursor:pointer;margin-top:.4rem}
.resetBtn{font-family:inherit;font-size:.9rem;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.3rem .9rem;cursor:pointer;margin-top:.4rem;margin-right:.4rem}
.score{font-size:.9rem;color:var(--muted);margin-right:.6rem}
.enote{font-size:.82rem;color:var(--muted)}
@media(max-width:640px){main{padding:.5rem}section{padding:.6rem}}
@media print{#sidebar,#burger,#overlay,.toolbar{display:none}.view:not(.on){display:none}.view.on{display:block}details.lesson{break-inside:avoid}}"""

JS_VIEWS = """// SPA views: sidebar switching, hamburger, hash deep-link, mobile drawer
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
"""

JS_STORAGE = """// localStorage persistence for Section 2 answers. Keys: bacai:m:<qid>, bacai:e:<qid>
(function () {
  var P = 'bacai:';
  document.querySelectorAll('#sec2 input[type=radio]').forEach(function (r) {
    var k = P + 'm:' + r.name;
    try { if (localStorage.getItem(k) === r.value) r.checked = true; } catch (e) {}
    r.addEventListener('change', function () {
      try { localStorage.setItem(k, r.value); } catch (e) {}
      var card = r.closest('.card.q');
      if (card) card.querySelectorAll('.opt').forEach(function (o) { o.classList.remove('ok', 'bad'); });
      var sc = card ? card.closest('.view').querySelector('.score[data-score]') : null;
    });
  });
  document.querySelectorAll('#sec2 textarea').forEach(function (t) {
    var k = P + 'e:' + t.dataset.qid;
    try { var v = localStorage.getItem(k); if (v !== null) t.value = v; } catch (e) {}
    t.addEventListener('input', function () { try { localStorage.setItem(k, t.value); } catch (e) {} });
  });
})();
"""

JS_FILTER = """// Unit filter (#uf) + search (#s), scoped to the active view only
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
"""

JS_GRADE = """// Per-group localized grading (MCQ only). ANSWERS consulted only here, on click.
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
"""

JS_MAIN = """// Wiring: theme toggle + print (active view only via CSS)
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
"""

HTML = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>البرمجة والذكاء الاصطناعي — الصف الثاني بكالوريا</title>
<link rel="stylesheet" href="assets/css/styles.css"></head>
<body>
<button id="burger" aria-label="القائمة">☰</button>
<div id="overlay" hidden></div>
<aside id="sidebar">
<h2>الأقسام</h2>
<button data-view="الشرح">الشرح</button>
<button data-view="الأسئلة">الأسئلة</button>
<button data-view="الإجابات">نموذج الإجابات</button>
</aside>
<header><h1>البرمجة والذكاء الاصطناعي — الصف الثاني بكالوريا (الترم الأول)</h1>
<div class="sub">الشرح (14 درسا) • الأسئلة (357 سؤالا) • الإجابات النموذجية — من المستندات الأربعة فقط</div></header>
<div class="toolbar">
<select id="uf"><option value="all">كل الوحدات</option><option value="1">الوحدة 1</option><option value="2">الوحدة 2</option><option value="3">الوحدة 3</option><option value="4">الوحدة 4</option></select>
<input id="s" placeholder="بحث في القسم الحالي..."><button id="themeBtn" type="button">الوضع الليلي</button><button id="printBtn" type="button">طباعة</button>
</div>
<main>
<div id="sec1" class="view on"><section><h2 class="sec">القسم الأول — الشرح (14 درسا)</h2>{SEC1}</section></div>
<div id="sec2" class="view" hidden><section><h2 class="sec">القسم الثاني — الأسئلة (357 سؤالا)</h2>{SEC2}</section></div>
<div id="sec3" class="view" hidden><section><h2 class="sec">القسم الثالث — الإجابات النموذجية</h2>{SEC3}</section></div>
</main>
<script src="assets/js/answers.js"></script>
<script src="assets/js/views.js"></script>
<script src="assets/js/storage.js"></script>
<script src="assets/js/filter.js"></script>
<script src="assets/js/grade.js"></script>
<script src="assets/js/main.js"></script>
</body></html>"""

# ---------- acceptance checks ----------
sec2_region = SEC2
for bad in ["data-correct", "data-answer", "correct", "الإجابة الصحيحة", "نموذج الإجابة"]:
    assert bad not in sec2_region, f"LEAK: {bad} in section 2"
assert "ANSWERS" not in sec2_region and "answers.js" not in sec2_region
for bad in ["تكميلي", "class=\"src\"", ".pdf", "Programming-ArtificialIntelligence", "mragaa", "Examify"]:
    assert bad not in sec2_region, f"LABEL LEAK: {bad} in section 2"
# standalone source label only (التحيز الخوارزمي is a lesson term, allowed)
assert not re.search(r'(?<!التحيز )الخوارزمي', sec2_region), "LABEL LEAK: standalone الخوارزمي in section 2"
assert 'المصدر:' not in sec2_region, "source line in section 2"
assert sec2_region.count("resetBtn") == 15, sec2_region.count("resetBtn")
assert sec2_region.count("gradeBtn") == 15, sec2_region.count("gradeBtn")
assert "هل أنت متأكد من مسح إجابات هذا القسم؟" in JS_GRADE, "reset confirm missing"
assert "bacai:m:" in JS_GRADE and "bacai:e:" in JS_GRADE, "reset keys missing"
assert "bacai:theme" not in JS_GRADE, "reset touches theme key"
assert "sec3" not in JS_GRADE.lower() and "scroll" not in JS_GRADE.lower(), "grade escapes group"
assert "fetch(" not in JS_GRADE and "fetch(" not in JS_STORAGE and "fetch(" not in JS_FILTER, "network call found"
sec2_qids = set(re.findall(r"data-qid='([^']+)'", sec2_region))
sec3_qids = set(re.findall(r'<span class="qid">([^<]+)</span>', SEC3))
assert sec2_qids == sec3_qids, f"QID mismatch: {len(sec2_qids)} vs {len(sec3_qids)}"
assert len(sec2_qids) == 357, len(sec2_qids)
assert sec2_region.count('type="radio"') == sum(len(q["opts"]) for q in ALLQ if q["kind"] == "mcq")
assert sec2_region.count("<textarea") == sum(1 for q in ALLQ if q["kind"] == "essay")
# split-file structure, no inline code, no CDN
assert "<style>" not in HTML and "<script>" not in HTML, "inline style/script found"
for ref in ['href="assets/css/styles.css"', 'src="assets/js/answers.js"',
            'src="assets/js/views.js"', 'src="assets/js/storage.js"',
            'src="assets/js/filter.js"', 'src="assets/js/grade.js"',
            'src="assets/js/main.js"']:
    assert ref in HTML, f"missing asset ref {ref}"
assert 'onclick=' not in HTML, "inline handler found"
assert "bacai:m:" in JS_STORAGE and "bacai:e:" in JS_STORAGE, "storage keys changed"
assert "getElementById('uf')" in JS_FILTER and "getElementById('s')" in JS_FILTER
assert ".view.on" in JS_FILTER, "filter not scoped to active view"
assert "ANSWERS[qid]" in JS_GRADE and "ANSWERS" not in JS_STORAGE and "ANSWERS" not in JS_FILTER
assert 'data-theme' in CSS and 'bacai:theme' in JS_MAIN, "theme persistence missing"
for blob, name in [(HTML, "html"), (CSS, "css"), (ANS_JS, "answers"),
                   (JS_VIEWS, "views"), (JS_STORAGE, "storage"),
                   (JS_FILTER, "filter"), (JS_GRADE, "grade"), (JS_MAIN, "main")]:
    assert "http://" not in blob and "https://" not in blob, f"external URL in {name}"
# justifications present for every gradeable MCQ in Section 3
missing_j = [q["qid"] for q in ALLQ if q["kind"] == "mcq" and q["qid"] in gradeable and q["qid"] not in JUST_ALL]

assert not missing_j, missing_j[:10]

import os
BASE = "/media/Games/Programming"
os.makedirs(f"{BASE}/assets/css", exist_ok=True)
os.makedirs(f"{BASE}/assets/js", exist_ok=True)
open(f"{BASE}/index.html", "w", encoding="utf-8").write(HTML)
open(f"{BASE}/assets/css/styles.css", "w", encoding="utf-8").write(CSS)
open(f"{BASE}/assets/js/answers.js", "w", encoding="utf-8").write(ANS_JS)
open(f"{BASE}/assets/js/views.js", "w", encoding="utf-8").write(JS_VIEWS)
open(f"{BASE}/assets/js/storage.js", "w", encoding="utf-8").write(JS_STORAGE)
open(f"{BASE}/assets/js/filter.js", "w", encoding="utf-8").write(JS_FILTER)
open(f"{BASE}/assets/js/grade.js", "w", encoding="utf-8").write(JS_GRADE)
open(f"{BASE}/assets/js/main.js", "w", encoding="utf-8").write(JS_MAIN)
print("OK lessons=14 totalQ=357 mcq=%d essay=%d gradeable=%d" % (
    sum(1 for q in ALLQ if q["kind"] == "mcq"),
    sum(1 for q in ALLQ if q["kind"] == "essay"), len(gradeable)))
print("groups:")
for gtitle, gkind, gkey, qs in HGROUPS:
    print(" - %s: %d (%d mcq gradeable / %d essay)" % (
        gtitle, len(qs),
        sum(1 for q in qs if q["kind"] == "mcq" and q["qid"] in gradeable),
        sum(1 for q in qs if q["kind"] == "essay")))
print("no-grading-leak section2: PASS; sec2<->sec3 QID match: PASS (357)")
print("bytes:", os.path.getsize("/media/Games/Programming/index.html"))
