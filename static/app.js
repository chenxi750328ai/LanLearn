(function () {
  "use strict";

  const API = "";

  const state = {
    planId: null,
    studySession: null,
    cardIndex: 0,
    examSession: null,
    importCandidates: [],
  };

  const $ = (id) => document.getElementById(id);

  function showToast(msg, isError) {
    const el = $("toast");
    el.textContent = msg;
    el.classList.toggle("error", !!isError);
    el.classList.remove("hidden");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => el.classList.add("hidden"), 4000);
  }

  async function api(path, opts) {
    const headers = { Accept: "application/json", ...(opts?.headers || {}) };
    if (opts?.body && !(opts.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    const res = await fetch(API + path, { ...opts, headers });
    const body = res.headers.get("content-type")?.includes("json")
      ? await res.json()
      : null;
    if (!res.ok) {
      const detail = body?.message || body?.detail || res.statusText;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return body;
  }

  function setPlanInfo(plan) {
    state.planId = plan.id;
    const box = $("plan-info");
    box.classList.remove("hidden");
    box.innerHTML =
      `<strong>计划 #${plan.id}</strong> · ${plan.exam_type} · 每日 ${plan.daily_quota} 词 · 共 ${plan.days.length} 天`;
    $("btn-start-study").disabled = false;
    $("btn-start-exam").disabled = false;
  }

  async function createPlan() {
    const daily_quota = parseInt($("daily-quota").value, 10) || 5;
    try {
      const plan = await api("/plans", {
        method: "POST",
        body: JSON.stringify({ exam_type: "toefl", daily_quota }),
      });
      setPlanInfo(plan);
      showToast("计划已创建");
    } catch (e) {
      showToast(e.message, true);
    }
  }

  function renderStudyCard() {
    const session = state.studySession;
    if (!session || state.cardIndex >= session.cards.length) {
      $("study-area").classList.add("hidden");
      showToast("本轮背词完成");
      refreshProgress();
      return;
    }
    const card = session.cards[state.cardIndex];
    $("study-word").textContent = card.word;
    const opts = $("study-options");
    opts.innerHTML = "";
    $("study-feedback").classList.add("hidden");

    const choices = card.options || [card.correct_definition];
    choices.forEach((opt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "option-btn";
      btn.textContent = opt;
      btn.addEventListener("click", () => submitStudyAnswer(card, opt, btn));
      opts.appendChild(btn);
    });
    $("study-area").classList.remove("hidden");
  }

  async function submitStudyAnswer(card, answer, btn) {
    $("study-options").querySelectorAll("button").forEach((b) => (b.disabled = true));
    try {
      const result = await api(`/study/sessions/${state.studySession.id}/answer`, {
        method: "POST",
        body: JSON.stringify({ word_id: card.word_id, answer }),
      });
      const fb = $("study-feedback");
      fb.classList.remove("hidden");
      fb.textContent = result.correct
        ? "✓ 正确"
        : `✗ 正确答案：${result.correct_definition}`;
      fb.classList.toggle("correct", result.correct);
      fb.classList.toggle("wrong", !result.correct);
      btn.classList.add(result.correct ? "correct" : "wrong");
      setTimeout(() => {
        state.cardIndex += 1;
        renderStudyCard();
      }, 800);
    } catch (e) {
      showToast(e.message, true);
      $("study-options").querySelectorAll("button").forEach((b) => (b.disabled = false));
    }
  }

  async function startStudy() {
    if (!state.planId) return;
    try {
      state.studySession = await api("/study/sessions", {
        method: "POST",
        body: JSON.stringify({ plan_id: state.planId, day_index: 0, mode: "mcq" }),
      });
      state.cardIndex = 0;
      renderStudyCard();
      showToast("背词已开始");
    } catch (e) {
      showToast(e.message, true);
    }
  }

  function renderExamForm() {
    const session = state.examSession;
    const form = $("exam-form");
    form.innerHTML = "";
    session.questions.forEach((q, i) => {
      const fieldset = document.createElement("fieldset");
      fieldset.className = "exam-question";
      const legend = document.createElement("legend");
      legend.textContent = `第 ${i + 1} 题 · ${q.type === "synonym_mcq" ? "同义" : "填空"}`;
      fieldset.appendChild(legend);
      const stem = document.createElement("p");
      stem.className = "exam-stem";
      stem.textContent = q.stem;
      fieldset.appendChild(stem);
      q.options.forEach((opt) => {
        const label = document.createElement("label");
        label.className = "exam-choice";
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = q.id;
        radio.value = opt;
        radio.required = true;
        label.appendChild(radio);
        label.appendChild(document.createTextNode(" " + opt));
        fieldset.appendChild(label);
      });
      form.appendChild(fieldset);
    });
    $("exam-area").classList.remove("hidden");
    $("exam-result").classList.add("hidden");
  }

  async function startExam() {
    if (!state.planId) return;
    try {
      state.examSession = await api("/exam/sessions", {
        method: "POST",
        body: JSON.stringify({ plan_id: state.planId, question_count: 2 }),
      });
      renderExamForm();
      showToast("模考已开始");
    } catch (e) {
      showToast(e.message, true);
    }
  }

  async function submitExam(ev) {
    ev.preventDefault();
    const session = state.examSession;
    if (!session) return;
    const answers = session.questions.map((q) => {
      const picked = document.querySelector(`input[name="${q.id}"]:checked`);
      return { question_id: q.id, choice: picked ? picked.value : "" };
    });
    try {
      const report = await api(`/exam/sessions/${session.id}/submit`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      });
      $("exam-area").classList.add("hidden");
      const box = $("exam-result");
      box.classList.remove("hidden");
      box.innerHTML = `<strong>得分 ${report.score} / ${report.total}</strong>` +
        (report.wrong_word_ids.length
          ? `<br>错题词 ID：${report.wrong_word_ids.join(", ")}`
          : "<br>全部正确！");
      showToast("模考已提交");
      refreshProgress();
    } catch (e) {
      showToast(e.message, true);
    }
  }

  function renderProgress(data) {
    const box = $("progress-info");
    box.classList.remove("hidden");
    const rate =
      data.study_answered > 0
        ? Math.round((100 * data.study_correct) / data.study_answered)
        : 0;
    box.innerHTML = [
      `<strong>背词</strong>：已答 ${data.study_answered} 题，正确 ${data.study_correct}（${rate}%）`,
      `<strong>模考</strong>：${data.exam_sessions} 次`,
      data.weak_word_ids.length
        ? `<strong>薄弱词</strong>：${data.weak_word_ids.slice(0, 8).join(", ")}`
        : "<strong>薄弱词</strong>：暂无",
    ].join("<br>");
  }

  async function refreshProgress() {
    try {
      const data = await api("/progress/summary");
      renderProgress(data);
    } catch (e) {
      showToast(e.message, true);
    }
  }

  function renderImportPreview(data) {
    const box = $("import-preview");
    box.classList.remove("hidden");
    const failText = data.failures.length
      ? `<br>失败 ${data.failures.length} 行`
      : "";
    box.innerHTML =
      `<strong>候选 ${data.candidates.length} 条</strong>${failText}` +
      (data.candidates.length
        ? `<br>${data.candidates
            .slice(0, 5)
            .map((c) => c.word)
            .join(", ")}${data.candidates.length > 5 ? "…" : ""}`
        : "");
    $("btn-import-confirm").disabled = data.candidates.length === 0;
  }

  async function uploadImportImage() {
    const input = $("import-image");
    const file = input.files?.[0];
    if (!file) {
      showToast("请选择图片文件", true);
      return;
    }
    const form = new FormData();
    form.append("file", file);
    try {
      const data = await api("/ingest/image", { method: "POST", body: form });
      state.importCandidates = data.candidates;
      renderImportPreview({ candidates: data.candidates, failures: [] });
      if (!data.candidates.length) {
        showToast("未识别到单词：请换清晰图片，或安装本机 Tesseract 后重试", true);
      } else {
        showToast(`OCR 解析 ${data.candidates.length} 条候选`);
      }
    } catch (e) {
      showToast(e.message, true);
    }
  }

  async function uploadImportFile() {
    const input = $("import-file");
    const file = input.files?.[0];
    if (!file) {
      showToast("请选择 CSV 或 TXT 文件", true);
      return;
    }
    const form = new FormData();
    form.append("file", file);
    try {
      const data = await api("/ingest/file", { method: "POST", body: form });
      state.importCandidates = data.candidates;
      renderImportPreview(data);
      showToast(`已解析 ${data.candidates.length} 条候选`);
    } catch (e) {
      showToast(e.message, true);
    }
  }

  async function confirmImport() {
    if (!state.importCandidates.length) return;
    try {
      const words = await api("/ingest/confirm", {
        method: "POST",
        body: JSON.stringify({ candidates: state.importCandidates }),
      });
      state.importCandidates = [];
      $("btn-import-confirm").disabled = true;
      $("import-file").value = "";
      renderImportPreview({ candidates: [], failures: [] });
      showToast(`已入库 ${words.length} 条`);
    } catch (e) {
      showToast(e.message, true);
    }
  }

  $("btn-create-plan").addEventListener("click", createPlan);
  $("btn-start-study").addEventListener("click", startStudy);
  $("btn-start-exam").addEventListener("click", startExam);
  $("exam-form").addEventListener("submit", submitExam);
  $("btn-refresh-progress").addEventListener("click", refreshProgress);
  $("btn-import-upload").addEventListener("click", uploadImportFile);
  $("btn-import-image").addEventListener("click", uploadImportImage);
  $("btn-import-confirm").addEventListener("click", confirmImport);

  refreshProgress();
})();
