const SHEET_CONFIG = {
  tasks: 'Today',
  habits: 'Habits',
  finance: 'Finance',
  goals: 'Goals',
  projects: 'Projects',
  dashboard: 'Dashboard',
  settings: 'Settings'
};

// Тестова функція: її можна вибрати в списку і натиснути «Виконати» для перевірки
function testConnection() {
  const snapshot = getSnapshot();
  Logger.log('Тест успішний! Дані з таблиці:');
  Logger.log(JSON.stringify(snapshot, null, 2));
}

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action ? e.parameter.action : 'snapshot').toLowerCase();

  try {
    if (action === 'snapshot') {
      return jsonResponse(getSnapshot());
    }
    if (action === 'ping') {
      return jsonResponse({ ok: true, message: 'LIFE OS API online', time: new Date().toISOString() });
    }
    return jsonResponse({ error: 'Unknown action. Use ?action=snapshot or ?action=ping' }, 400);
  } catch (err) {
    return jsonResponse({ error: err.message }, 500);
  }
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ error: 'Empty post data' }, 400);
    }
    const body = JSON.parse(e.postData.contents);
    const action = (body.action || '').toLowerCase();

    if (action === 'push') {
      applyPush(body.data || body);
      return jsonResponse({ ok: true, message: 'Data pushed to Sheets', time: new Date().toISOString() });
    }
    if (action === 'add_task') {
      addTaskRow(body.task);
      return jsonResponse({ ok: true, message: 'Task added' });
    }
    if (action === 'add_finance') {
      addFinanceRow(body.item);
      return jsonResponse({ ok: true, message: 'Finance entry added' });
    }
    if (action === 'set_habit') {
      setHabitDay(body.habit, body.day, body.done);
      return jsonResponse({ ok: true, message: 'Habit updated' });
    }

    return jsonResponse({ error: 'Unknown POST action' }, 400);
  } catch (err) {
    return jsonResponse({ error: err.message }, 500);
  }
}

function jsonResponse(obj, code) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function getSnapshot() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return {
    source: 'LIFE OS Google Sheets',
    updated: new Date().toISOString(),
    spreadsheetId: ss.getId(),
    spreadsheetUrl: ss.getUrl(),
    goals: readGoals_(ss),
    projects: readProjects_(ss),
    finance: readFinance_(ss),
    habitsSummary: readHabitsSummary_(ss)
  };
}

function readGoals_(ss) {
  const sh = ss.getSheetByName(SHEET_CONFIG.goals);
  if (!sh) return [];
  const values = sh.getDataRange().getValues();
  const rows = [];
  for (let i = 0; i < values.length; i++) {
    const name = String(values[i][2] || values[i] || '').trim();
    if (!name || name === 'Goal' || name === '#' || name.length < 2) continue;
    rows.push({
      name: name,
      area: String(values[i][3] || ''),
      type: String(values[i][4] || ''),
      progress: Number(values[i][5]) || 0,
      status: String(values[i][6] || values[i][7] || '')
    });
  }
  return rows.slice(0, 20);
}

function readProjects_(ss) {
  const sh = ss.getSheetByName(SHEET_CONFIG.projects);
  if (!sh) return [];
  const values = sh.getDataRange().getValues();
  const rows = [];
  for (let i = 1; i < values.length; i++) {
    const name = String(values[i] || '').trim();
    if (!name) continue;
    rows.push({
      name: name,
      status: String(values[i][2] || ''),
      priority: String(values[i][3] || ''),
      next: String(values[i][5] || ''),
      progress: Number(values[i][6]) || 0
    });
  }
  return rows.slice(0, 20);
}

function readFinance_(ss) {
  const sh = ss.getSheetByName(SHEET_CONFIG.finance);
  if (!sh) return { income: 0, expenses: 0, balance: 0 };
  let income = 0, expenses = 0;
  try {
    income = Number(sh.getRange('D12').getValue()) || 0;
    expenses = Number(sh.getRange('D25').getValue()) || 0;
  } catch (e) {}
  return { income, expenses, balance: income - expenses };
}

function readHabitsSummary_(ss) {
  const sh = ss.getSheetByName(SHEET_CONFIG.habits);
  if (!sh) return [];
  const values = sh.getDataRange().getValues();
  const summary = [];
  for (let i = 0; i < values.length; i++) {
    const name = String(values[i] || '').trim();
    if (!name || name === 'Habit' || name === 'Month') continue;
    const last = values[i][values[i].length - 1];
    const prev = values[i][values[i].length - 2];
    summary.push({
      name: name,
      count: Number(prev) || 0,
      pct: typeof last === 'number' ? Math.round(last * 100) : (Number(last) || 0)
    });
  }
  return summary.slice(0, 15);
}

function applyPush(payload) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const log = ss.getSheetByName(SHEET_CONFIG.settings) || ss.insertSheet(SHEET_CONFIG.settings);
  log.getRange('A30').setValue('Last push from Web-App:');
  log.getRange('B30').setValue(new Date().toISOString());
  log.getRange('A31').setValue(JSON.stringify(payload).substring(0, 500));
}

function logToSheet_(type, data) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let log = ss.getSheetByName('_API_Log');
  if (!log) {
    log = ss.insertSheet('_API_Log');
    log.appendRow(['Timestamp', 'Type', 'Data']);
  }
  let text = '';
  try {
    text = JSON.stringify(data);
  } catch (e) {
    text = String(data);
  }
  if (text.length > 2000) text = text.substring(0, 2000);
  log.appendRow([new Date().toISOString(), type, text]);
}

function addTaskRow(task) {
  if (!task || !task.text) throw new Error('task.text required');
  logToSheet_('task', task);
}

function addFinanceRow(item) {
  if (!item) throw new Error('item required');
  logToSheet_('finance', item);
}

function setHabitDay(habit, day, done) {
  logToSheet_('habit', { habit, day, done });
}
