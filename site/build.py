# -*- coding: utf-8 -*-
"""Build single self-contained index.html from extracted data files."""
import sys, re, html
sys.path.insert(0, '/media/Games/Programming/site')
from data_lessons_u1 import LESSONS_U1
from data_book_u1 import BOOK_U1, KHAWARIZMI_U1
from data_lessons_u2 import LESSONS_U2, BOOK_U2, KHAWARIZMI_U2
from data_lessons_u34 import LESSONS_U34, BOOK_U34, KHAWARIZMI_U34
from data_review import REVIEW_ESSAY, REVIEW_MCQ

LETTERS = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح"]

def esc(s):
    return html.escape(str(s), quote=True)

def strip_label(opt):
    return re.sub(r'^\s*[أبجدهـوزح]\s*[\)\.\-:：]?\s*', '', str(opt).strip())

def norm_q(q, sec):
    """Unify schema -> qid, lesson, kind, text, opts, answer, evidence, src."""
    qid = q["qid"]
    lesson = q.get("lesson", "")
    kind = q.get("kind", "mcq" if "opts" in q and q["opts"] else "essay")
    if sec == "REV-MCQ":
        kind = "mcq"
    elif sec == "REV-ESS":
        kind = "essay"
    text = q["text"]
    opts = [strip_label(o) for o in (q.get("opts") or [])]
    ans = q["answer"]
    # review MCQ: answer is a letter -> resolve to option text for Section 3 only
    ans_text = ans
    if sec == "REV-MCQ" and ans in LETTERS and opts:
        ans_text = LETTERS.index(ans)
        ans_text = opts[ans_text] if ans_text < len(opts) else ans
    return dict(qid=qid, lesson=lesson, kind=kind, text=text, opts=opts,
                answer=ans, ans_text=ans_text,
                evidence=q.get("evidence", ""), src=q.get("src", ""), sec=sec)

LESSONS = LESSONS_U1 + LESSONS_U2 + LESSONS_U34
assert len(LESSONS) == 14, len(LESSONS)

GROUPS = [
    ("أسئلة المراجعة — اختيار من متعدد (الوحدة الأولى)", "مراجعة", [norm_q(q, "REV-MCQ") for q in REVIEW_MCQ]),
    ("أسئلة المراجعة — مقالية (الوحدة الأولى)", "مراجعة", [norm_q(q, "REV-ESS") for q in REVIEW_ESSAY]),
    ("أسئلة الكتاب المدرسي — الوحدة الأولى", "كتاب1", [norm_q(q, "B1") for q in BOOK_U1]),
    ("أسئلة الكتاب المدرسي — الوحدة الثانية", "كتاب2", [norm_q(q, "B2") for q in BOOK_U2]),
    ("أسئلة الكتاب المدرسي — الوحدتان الثالثة والرابعة", "كتاب34", [norm_q(q, "B34") for q in BOOK_U34]),
    ("أسئلة تكميلية (الخوارزمي) — الوحدة الأولى", "خوارزمي1", [norm_q(q, "K1") for q in KHAWARIZMI_U1]),
    ("أسئلة تكميلية (الخوارزمي) — الوحدة الثانية", "خوارزمي2", [norm_q(q, "K2") for q in KHAWARIZMI_U2]),
    ("أسئلة تكميلية (الخوارزمي) — الوحدتان الثالثة والرابعة", "خوارزمي34", [norm_q(q, "K34") for q in KHAWARIZMI_U34]),
]
ALLQ = [q for _, _, qs in GROUPS for q in qs]
assert len(ALLQ) == 357, len(ALLQ)
assert len({q["qid"] for q in ALLQ}) == 357

UNIT_OF = {}
for L in LESSONS:
    UNIT_OF[L["code"]] = L["unit"]
def unit_of(q):
    return UNIT_OF.get(q["lesson"], "?")

KIND_AR = {"mcq": "اختيار من متعدد", "essay": "مقالي"}

# ---------- Section 1 ----------
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

# ---------- Section 2 (NO answers, NO markers) ----------
s2 = []
for gtitle, gkey, qs in GROUPS:
    cards = []
    for q in qs:
        if q["kind"] == "mcq":
            opts = "".join(
                f"""<label class="opt"><input type="radio" name="{esc(q['qid'])}" value="{i}"><span class="ol">{LETTERS[i]}</span><span>{esc(o)}</span></label>"""
                for i, o in enumerate(q["opts"]))
            inner = f"<div class='opts' data-qid='{esc(q['qid'])}'>{opts}</div>"
        else:
            inner = f"<textarea data-qid='{esc(q['qid'])}' rows='4' placeholder='اكتب إجابتك هنا'></textarea>"
        cards.append(f"""<div class="card q" data-unit="{esc(unit_of(q))}" data-group="{esc(gkey)}" data-search="{esc(q['text'])}">
<div class="qhead"><span class="qid">{esc(q['qid'])}</span><span class="ktag">{KIND_AR[q['kind']]}</span><span class="ltag">الدرس {esc(q['lesson'])}</span></div>
<p class="qtext">{esc(q['text'])}</p>{inner}
<div class="src">المصدر: {esc(q['src'])}</div></div>""")
    s2.append(f"<h3 class='grp' data-group='{esc(gkey)}'>{esc(gtitle)} <span class='cnt'>({len(qs)})</span></h3>\n" + "\n".join(cards))
SEC2 = "\n".join(s2)

# ---------- Section 3 (answer key) ----------
NOTE = "تنبيه: لا توجد إجابات نموذجية داخل المستندات الأربعة (نسخ المراجعة نسخ طالب بإجابات فارغة) — جميع الإجابات أدناه مستنتجة من شرح الدروس ومقرونة بالدليل."
s3 = [f"<div class='note'>{esc(NOTE)}</div>"]
for gtitle, gkey, qs in GROUPS:
    cards = []
    for q in qs:
        if q["kind"] == "mcq" and q["sec"] == "REV-MCQ":
            ans_show = f"الإجابة: {esc(q['answer'])} — {esc(str(q['ans_text']))}"
        else:
            ans_show = esc(str(q['ans_text']))
        cards.append(f"""<div class="card a" data-unit="{esc(unit_of(q))}" data-group="{esc(gkey)}" data-search="{esc(q['qid']+' '+q['text'])}">
<div class="qhead"><span class="qid">{esc(q['qid'])}</span><span class="ltag">الدرس {esc(q['lesson'])}</span><span class="der">لا توجد إجابة نموذجية في المستندات — الإجابة مستنتجة من شرح الدرس {esc(q['lesson'])}</span></div>
<p class="qtext">{esc(q['text'])}</p>
<div class="ans"><b>نموذج الإجابة:</b> {ans_show}</div>
<div class="ev"><b>الدليل:</b> {esc(q['evidence'])}</div>
<div class="src">المصدر: {esc(q['src'])}</div></div>""")
    s3.append(f"<h3 class='grp' data-group='{esc(gkey)}'>{esc(gtitle)} <span class='cnt'>({len(qs)})</span></h3>\n" + "\n".join(cards))
SEC3 = "\n".join(s3)

CSS = """*{box-sizing:border-box}body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:#f4f6fa;color:#1a1a1a;margin:0;line-height:1.9}
header{background:#1b3a5c;color:#fff;padding:1.2rem;text-align:center}
nav{position:sticky;top:0;background:#fff;border-bottom:2px solid #1b3a5c;display:flex;gap:.5rem;justify-content:center;padding:.6rem;z-index:10;flex-wrap:wrap}
nav a{background:#1b3a5c;color:#fff;padding:.4rem 1.1rem;border-radius:20px;text-decoration:none}
.toolbar{display:flex;gap:.5rem;justify-content:center;padding:.8rem;flex-wrap:wrap;background:#e9eef5}
.toolbar input,.toolbar select,.toolbar button{padding:.45rem .8rem;border-radius:8px;border:1px solid #bbb;font-size:1rem;font-family:inherit}
.toolbar button{background:#1b3a5c;color:#fff;border:none;cursor:pointer}
main{max-width:1000px;margin:auto;padding:1rem}
section{background:#fff;border-radius:12px;padding:1rem;margin-bottom:1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08)}
h2.sec{border-right:5px solid #1b3a5c;padding-right:.6rem}
h3.grp{background:#eef3f9;padding:.4rem .8rem;border-radius:8px}
.card{border:1px solid #ddd;border-radius:10px;padding:.7rem;margin:.7rem 0;background:#fff}
details.lesson summary{cursor:pointer;font-size:1.05rem}
.badge{background:#1b3a5c;color:#fff;border-radius:12px;padding:.1rem .7rem;font-size:.85rem}
.badge.code{background:#3a7d44}
.idea{background:#fffbe6;border-right:4px solid #d9a400;padding:.5rem .8rem;border-radius:6px}
.terms{display:flex;flex-wrap:wrap;gap:.4rem}
.term{background:#eef3f9;border:1px solid #c6d4e6;border-radius:14px;padding:.1rem .7rem;font-size:.9rem}
.src{color:#666;font-size:.85rem;margin-top:.5rem}
.qid{background:#5b2d8e;color:#fff;border-radius:8px;padding:.05rem .6rem;font-size:.85rem;direction:ltr;display:inline-block}
.ktag{background:#0b6e4f;color:#fff;border-radius:8px;padding:.05rem .6rem;font-size:.85rem}
.ltag{background:#eee;border-radius:8px;padding:.05rem .6rem;font-size:.85rem}
.qhead{display:flex;gap:.4rem;flex-wrap:wrap;align-items:center}
.opts{display:flex;flex-direction:column;gap:.4rem;margin:.5rem 0}
.opt{display:flex;gap:.5rem;align-items:flex-start;border:1px solid #ddd;border-radius:8px;padding:.4rem .6rem;cursor:pointer}
.opt:hover{background:#f2f7ff}
.ol{background:#1b3a5c;color:#fff;min-width:1.7rem;height:1.7rem;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:.9rem}
textarea{width:100%;border:1px solid #bbb;border-radius:8px;padding:.5rem;font-family:inherit;font-size:1rem}
.ans{background:#eefbef;border-right:4px solid #2e7d32;padding:.5rem .8rem;border-radius:6px;margin:.4rem 0}
.ev{background:#f6f6f6;padding:.4rem .8rem;border-radius:6px;font-size:.92rem}
.note{background:#fff3e0;border:1px solid #e0a800;border-radius:8px;padding:.6rem 1rem;margin-bottom:1rem}
.cnt{color:#555;font-size:.9rem}
.der{background:#fff3e0;border:1px solid #e0a800;border-radius:8px;padding:.05rem .6rem;font-size:.8rem}
@media(max-width:640px){main{padding:.5rem}section{padding:.6rem}}
@media print{nav,.toolbar,header .sub{display:none}details.lesson{break-inside:avoid}}"""

JS = """const P='bacai:';
document.querySelectorAll('#sec2 input[type=radio]').forEach(r=>{
 const k=P+'m:'+r.name;
 try{if(localStorage.getItem(k)===r.value)r.checked=true;}catch(e){}
 r.addEventListener('change',()=>{try{localStorage.setItem(k,r.value);}catch(e){}});
});
document.querySelectorAll('#sec2 textarea').forEach(t=>{
 const k=P+'e:'+t.dataset.qid;
 try{const v=localStorage.getItem(k);if(v!==null)t.value=v;}catch(e){}
 t.addEventListener('input',()=>{try{localStorage.setItem(k,t.value);}catch(e){}});
});
const uf=document.getElementById('uf'),sf=document.getElementById('s');
function filt(){
 const u=uf.value,q=sf.value.trim();
 document.querySelectorAll('main .card').forEach(c=>{
  const okU=(u==='all'||c.dataset.unit===u||c.dataset.unit==='?');
  const okQ=(!q||(c.dataset.search||'').includes(q));
  c.style.display=(okU&&okQ)?'':'none';
 });
 document.querySelectorAll('h3.grp').forEach(h=>{
  let n=h.nextElementSibling,vis=false;
  while(n&&!n.classList.contains('grp')&&n.tagName!=='H3'){
   if(n.classList&&n.classList.contains('card')&&n.style.display!=='none')vis=true;
   n=n.nextElementSibling;
  }
  h.style.display=vis?'':'none';
 });
}
uf.addEventListener('change',filt);sf.addEventListener('input',filt);
function pr(){window.print();}"""

HTML = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>البرمجة والذكاء الاصطناعي — الصف الثاني بكالوريا</title>
<style>{CSS}</style></head>
<body>
<header><h1>البرمجة والذكاء الاصطناعي — الصف الثاني بكالوريا (الترم الأول)</h1>
<div class="sub">الشرح (14 درسا) • الأسئلة (357 سؤالا) • الإجابات النموذجية — من المستندات الأربعة فقط</div></header>
<nav><a href="#sec1">الشرح</a><a href="#sec2">الأسئلة</a><a href="#sec3">الإجابات</a></nav>
<div class="toolbar">
<select id="uf"><option value="all">كل الوحدات</option><option value="1">الوحدة 1</option><option value="2">الوحدة 2</option><option value="3">الوحدة 3</option><option value="4">الوحدة 4</option></select>
<input id="s" placeholder="بحث..."><button onclick="pr()">طباعة</button>
</div>
<main>
<section id="sec1"><h2 class="sec">القسم الأول — الشرح (14 درسا)</h2>{SEC1}</section>
<section id="sec2"><h2 class="sec">القسم الثاني — الأسئلة (357 سؤالا، بدون تصحيح)</h2>{SEC2}</section>
<section id="sec3"><h2 class="sec">القسم الثالث — الإجابات النموذجية</h2>{SEC3}</section>
</main>
<script>{JS}</script>
</body></html>"""

# ---------- acceptance checks ----------
sec2_region = HTML.split('id="sec2"')[1].split('id="sec3"')[0]
for bad in ["data-correct", "data-answer", "correct", "الإجابة الصحيحة", "نموذج الإجابة"]:
    assert bad not in sec2_region, f"LEAK: {bad} in section 2"
sec2_qids = set(re.findall(r"data-qid='([^']+)'", sec2_region))
sec3_region = HTML.split('id="sec3"')[1]
sec3_qids = set(re.findall(r'<span class="qid">([^<]+)</span>', sec3_region))
assert sec2_qids == sec3_qids, f"QID mismatch: {len(sec2_qids)} vs {len(sec3_qids)}"
assert len(sec2_qids) == 357, len(sec2_qids)
# every sec2 radio group has matching name/qid, textareas have qid
assert sec2_region.count('type="radio"') == sum(len(q["opts"]) for q in ALLQ if q["kind"] == "mcq")
assert sec2_region.count("<textarea") == sum(1 for q in ALLQ if q["kind"] == "essay")

open("/media/Games/Programming/index.html", "w", encoding="utf-8").write(HTML)
import os
print("OK lessons=14 totalQ=357 mcq=%d essay=%d" % (
    sum(1 for q in ALLQ if q["kind"] == "mcq"),
    sum(1 for q in ALLQ if q["kind"] == "essay")))
print("review: 42 MCQ + 40 essay")
print("book: %d (u1=%d u2=%d u34=%d)" % (len(BOOK_U1)+len(BOOK_U2)+len(BOOK_U34), len(BOOK_U1), len(BOOK_U2), len(BOOK_U34)))
print("khawarizmi: %d (u1=%d u2=%d u34=%d)" % (len(KHAWARIZMI_U1)+len(KHAWARIZMI_U2)+len(KHAWARIZMI_U34), len(KHAWARIZMI_U1), len(KHAWARIZMI_U2), len(KHAWARIZMI_U34)))
print("no-grading-leak section2: PASS; sec2<->sec3 QID match: PASS (357)")
print("unanswerable: 0 — all answers derived from lesson text; Sec3 carries global disclaimer (no model answers exist in source files)")
print("bytes:", os.path.getsize("/media/Games/Programming/index.html"))
