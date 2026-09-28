# BaccalaureateAI

Arabic study page for **Programming & Artificial Intelligence — 2nd Year Egyptian Baccalaureate (Term 1)**.

## What's inside `index.html`

A single self-contained page (no CDN, no external calls, RTL Arabic) with three sections:

1. **الشرح** — 14 lesson cards (1-1 → 4-4) with goals, key concepts, main idea, explanations, and verbatim terms.
2. **الأسئلة** — 357 questions: 42 MCQ + 40 essay from the Unit 1 review banks, 124 main-textbook exercises, 151 supplementary (الخوارزمي) questions. MCQ answers are clickable radio buttons, essays have text areas; all answers persist via `localStorage` with **no auto-grading**.
3. **الإجابات النموذجية** — model answer + evidence quote for every question ID.

## Rebuild

```bash
python3 site/build.py
```

This regenerates `index.html` from the data files in `site/` (`data_*.py`) and runs acceptance checks (question counts, Section 2/3 QID match, no grading leak in Section 2).

## Sources (kept locally, intentionally untracked)

- `Programming-ArtificialIntelligence-Ar-EB-part1.pdf` — official textbook, Term 1 (Ch. 1–4)
- `الخوارزمي ثانية ثانوي عام.pdf` — supplementary explanations (labeled تكميلي)
- `mragaa-alohd-alaol-student.pdf` — Unit 1 essay review bank (student copy)
- `mragaa-alohd-alaol-akhtyar-mn-mtaadd-student.pdf` — Unit 1 MCQ review bank (student copy)

> **Note:** the review PDFs are blank student copies (no official answer key exists in the sources), so all answers in Section 3 are derived from the lesson text and marked accordingly: «لا توجد إجابة نموذجية في المستندات — الإجابة مستنتجة من شرح الدرس».
