(() => {
  const SAMPLE_HTML = `<!doctype html>
<html>
  <head></head>
  <body>
    <h1>Student dashboard</h1>
    <img src="student.jpg">
    <form>
      <input id="email" type="email">
      <button></button>
    </form>
    <a href="/profile"></a>
    <section id="content"></section>
    <aside id="content"></aside>
  </body>
</html>`;

  const editor = document.querySelector('#htmlEditor');
  const lineNumbers = document.querySelector('#lineNumbers');
  const editorWrap = document.querySelector('#editorWrap');
  const previewFrame = document.querySelector('#previewFrame');
  const previewEmpty = document.querySelector('#previewEmpty');
  const issueList = document.querySelector('#issueList');
  const learnPanel = document.querySelector('#learnPanel');
  const learnContent = document.querySelector('#learnContent');
  const toast = document.querySelector('#toast');
  const undoStack = [];
  let analysis = null;
  let selectedIssueId = null;
  let toastTimer;

  const qs = (selector) => document.querySelector(selector);
  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
  }

  function updateLineNumbers() {
    const lines = editor.value.split('\n').length;
    lineNumbers.replaceChildren();
    for (let index = 1; index <= lines; index += 1) {
      const line = make('span', '', String(index));
      line.dataset.line = String(index);
      lineNumbers.append(line);
    }
    qs('#characterCount').textContent = `${editor.value.length.toLocaleString()} / ${window.WEBWIZ_MAX_LENGTH.toLocaleString()}`;
    qs('#undoCode').disabled = undoStack.length === 0;
  }

  function setEditorValue(value, saveUndo = false) {
    if (saveUndo && editor.value !== value) undoStack.push(editor.value);
    editor.value = value;
    updateLineNumbers();
    clearLineHighlight();
  }

  function clearLineHighlight() {
    lineNumbers.querySelectorAll('.active').forEach((line) => line.classList.remove('active'));
  }

  function focusLine(lineNumber) {
    if (!lineNumber) return;
    const lines = editor.value.split('\n');
    const index = Math.max(0, Math.min(lines.length - 1, lineNumber - 1));
    const start = lines.slice(0, index).reduce((total, line) => total + line.length + 1, 0);
    editor.focus();
    editor.setSelectionRange(start, start + lines[index].length);
    const lineHeight = parseFloat(getComputedStyle(editor).lineHeight) || 20;
    editor.scrollTop = Math.max(0, index * lineHeight - 100);
    lineNumbers.scrollTop = editor.scrollTop;
    clearLineHighlight();
    const gutterLine = lineNumbers.querySelector(`[data-line="${lineNumber}"]`);
    if (gutterLine) gutterLine.classList.add('active');
  }

  function renderPreview() {
    previewFrame.srcdoc = editor.value;
    previewEmpty.hidden = true;
    showToast('Preview refreshed in an isolated frame.');
  }

  function renderReport(report) {
    qs('#totalIssues').textContent = report.total;
    qs('#scoreValue').textContent = `${report.score}`;
    qs('#scoreMeter').style.width = `${report.score}%`;
    qs('#scoreLabel').textContent = report.score_label;
    qs('#criticalCount').textContent = report.severity_counts.critical || 0;
    qs('#warningCount').textContent = report.severity_counts.warning || 0;
    qs('#analyzedState').textContent = `Analyzed ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    const bars = qs('#categoryBars');
    bars.replaceChildren();
    const categories = Object.entries(report.category_counts);
    if (!categories.length) {
      bars.append(make('p', 'muted', 'No issues across the implemented checks. Nice work.'));
    } else {
      categories.forEach(([category, count]) => {
        const row = make('div', 'category-row');
        row.append(make('span', '', category));
        const track = make('div', 'bar-track');
        const fill = make('span');
        fill.style.width = `${Math.min(100, (count / report.total) * 100)}%`;
        track.append(fill);
        row.append(track, make('b', '', String(count)));
        bars.append(row);
      });
    }
  }

  function createIssueCard(issue) {
    const card = make('article', `issue-card ${issue.severity}`);
    if (issue.id === selectedIssueId) card.classList.add('selected');
    const rail = make('div', 'issue-rail');
    const main = make('div', 'issue-main');
    main.append(make('p', 'issue-message', issue.message));
    const meta = make('div', 'issue-meta');
    meta.append(make('span', '', issue.category), make('span', 'severity', issue.severity));
    meta.append(make('span', '', issue.line ? `line ${issue.line}` : 'document')); 
    main.append(meta);
    const actions = make('div', 'issue-actions');
    const inspect = make('button', 'issue-action', 'Focus');
    inspect.type = 'button';
    inspect.addEventListener('click', () => selectIssue(issue));
    const learn = make('button', 'issue-action', 'Learn');
    learn.type = 'button';
    learn.addEventListener('click', () => { selectIssue(issue); learnPanel.hidden = false; learnPanel.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    actions.append(inspect, learn);
    card.append(rail, main, actions);
    if (issue.id === selectedIssueId) {
      const detail = make('div', 'issue-detail');
      detail.append(make('strong', '', 'Suggested correction: '));
      detail.append(document.createTextNode(issue.fix));
      const apply = make('button', 'apply-button', issue.fix_type ? 'Apply safe fix' : 'Manual fix needed');
      apply.type = 'button';
      apply.disabled = !issue.fix_type;
      if (issue.fix_type) apply.addEventListener('click', () => applyFix(issue));
      detail.append(document.createElement('br'), apply);
      card.append(detail);
    }
    return card;
  }

  function renderIssues() {
    issueList.replaceChildren();
    if (!analysis || !analysis.issues.length) {
      const empty = make('div', 'empty-issues');
      empty.append(make('span', '', '✓'), make('strong', '', analysis ? 'No issues flagged' : 'Nothing flagged yet'));
      empty.append(make('p', '', analysis ? 'The implemented checks found no findings.' : 'Analyze your HTML to get a focused list of improvements.'));
      issueList.append(empty);
      return;
    }
    analysis.issues.forEach((issue) => issueList.append(createIssueCard(issue)));
  }

  function renderLesson(issue) {
    learnContent.replaceChildren();
    const grid = make('div', 'lesson-grid');
    const copy = make('div', 'lesson-copy');
    copy.append(make('p', 'eyebrow', `${issue.category} · ${issue.severity}`));
    copy.append(make('h3', '', issue.message));
    const what = make('p');
    what.append(make('strong', '', 'What it is: '), document.createTextNode(issue.message));
    const why = make('p');
    why.append(make('strong', '', 'Why it matters: '), document.createTextNode(issue.why));
    const how = make('p');
    how.append(make('strong', '', 'How to fix it: '), document.createTextNode(issue.fix));
    copy.append(what, why, how);
    const examples = make('div', 'lesson-examples');
    const bad = make('div');
    bad.append(make('span', 'example-label', 'Incorrect example'));
    bad.append(make('pre', 'code-example', issue.bad_example));
    const good = make('div');
    good.append(make('span', 'example-label good', 'Corrected example'));
    good.append(make('pre', 'code-example good', issue.good_example));
    examples.append(bad, good);
    grid.append(copy, examples);
    learnContent.append(grid);
  }

  function selectIssue(issue) {
    selectedIssueId = issue.id;
    focusLine(issue.line);
    renderIssues();
    renderLesson(issue);
    learnPanel.hidden = false;
    showToast(issue.line ? `Focused line ${issue.line}.` : 'Focused the document-level issue.');
  }

  function replaceOnLine(lineNumber, replacer) {
    const lines = editor.value.split('\n');
    const index = Math.max(0, Math.min(lines.length - 1, (lineNumber || 1) - 1));
    lines[index] = replacer(lines[index]);
    return lines.join('\n');
  }

  function applyFix(issue) {
    const before = editor.value;
    let after = before;
    const type = issue.fix_type;
    if (type === 'add-doctype') after = `<!doctype html>\n${before}`;
    else if (type === 'add-title') after = /<head\b[^>]*>/i.test(before) ? before.replace(/(<head\b[^>]*>)/i, '$1\n    <title>My page</title>') : `<head><title>My page</title></head>\n${before}`;
    else if (type === 'add-language') after = replaceOnLine(issue.line, (line) => line.replace(/<html\b([^>]*)>/i, (_, attrs) => `<html${attrs} lang="en">`));
    else if (type === 'add-alt') after = replaceOnLine(issue.line, (line) => line.replace(/<img\b(?![^>]*\balt\s*=)([^>]*)>/i, '<img alt="Describe this image"$1>'));
    else if (type === 'add-label') after = replaceOnLine(issue.line, (line) => line.replace(/<(input|select|textarea)\b/i, '<$1 aria-label="Describe this field"'));
    else if (type === 'add-link-text') after = replaceOnLine(issue.line, (line) => line.replace(/(<a\b[^>]*>)\s*(<\/a>)/i, '$1Link text$2'));
    else if (type === 'add-button-text') after = replaceOnLine(issue.line, (line) => line.replace(/(<button\b[^>]*>)\s*(<\/button>)/i, '$1Button action$2'));
    else if (type === 'rename-duplicate-id') after = replaceOnLine(issue.line, (line) => line.replace(/id\s*=\s*(["'])[^"']+\1/i, 'id="unique-section"'));
    if (after === before) { showToast('This suggestion needs a manual edit.'); return; }
    setEditorValue(after, true);
    selectedIssueId = null;
    analysis = null;
    renderIssues();
    qs('#analyzedState').textContent = 'Code changed — re-analyze when ready';
    showToast('Safe fix applied. Undo is available.');
  }

  async function analyze() {
    const button = qs('#analyzeButton');
    button.disabled = true;
    button.querySelector('span').textContent = 'Analyzing…';
    try {
      const response = await fetch('/api/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ html: editor.value }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Analysis failed.');
      analysis = data;
      selectedIssueId = null;
      renderReport(data);
      renderIssues();
      showToast(`${data.total} issue${data.total === 1 ? '' : 's'} found.`);
      qs('#reportSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      showToast(error.message || 'Analysis failed.');
    } finally {
      button.disabled = false;
      button.querySelector('span').textContent = 'Analyze HTML';
    }
  }

  editor.addEventListener('input', () => { updateLineNumbers(); qs('#analyzedState').textContent = 'Code changed — re-analyze when ready'; });
  editor.addEventListener('scroll', () => { lineNumbers.scrollTop = editor.scrollTop; });
  editorWrap.addEventListener('click', (event) => {
    if (event.target.closest('#lineNumbers')) {
      const line = event.target.closest('[data-line]');
      if (line) focusLine(Number(line.dataset.line));
    }
  });
  qs('#loadSample').addEventListener('click', () => { setEditorValue(SAMPLE_HTML, true); analysis = null; renderIssues(); showToast('Sample HTML loaded. It includes teachable issues.'); });
  qs('#clearCode').addEventListener('click', () => { setEditorValue('', true); analysis = null; renderIssues(); previewFrame.removeAttribute('srcdoc'); previewEmpty.hidden = false; showToast('Editor cleared.'); });
  qs('#undoCode').addEventListener('click', () => { if (!undoStack.length) return; editor.value = undoStack.pop(); updateLineNumbers(); analysis = null; renderIssues(); showToast('Last edit undone.'); });
  qs('#analyzeButton').addEventListener('click', analyze);
  qs('#runPreview').addEventListener('click', renderPreview);
  qs('#learnToggle').addEventListener('click', () => { learnPanel.hidden = false; learnPanel.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  qs('#closeLearn').addEventListener('click', () => { learnPanel.hidden = true; });
  qs('#themeToggle').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('webwiz-theme', next);
    qs('#themeToggle').textContent = next === 'light' ? '☾' : '☼';
    qs('#themeToggle').setAttribute('aria-label', `Switch to ${next === 'light' ? 'dark' : 'light'} theme`);
  });

  const savedTheme = localStorage.getItem('webwiz-theme');
  if (savedTheme === 'light') { document.documentElement.dataset.theme = 'light'; qs('#themeToggle').textContent = '☾'; }
  setEditorValue(SAMPLE_HTML);
  renderIssues();
})();
