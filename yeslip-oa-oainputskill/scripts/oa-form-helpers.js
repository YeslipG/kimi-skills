window.OAInput = (() => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const value = id => document.querySelector(`#${id}`)?.value || '';
  const visibleModals = () => [...document.querySelectorAll('.ant-modal')].filter(e => e.offsetParent);

  const waitFor = async (fn, timeout = 6000) => {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      const result = fn();
      if (result) return result;
      await sleep(150);
    }
    throw new Error('OA 控件等待超时');
  };

  const setInput = (element, text) => {
    if (!element) throw new Error('找不到输入框');
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(element, text);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const setTextarea = (id, text) => {
    const element = document.querySelector(`#${id}`);
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(element, text);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const fieldCell = label => {
    const cell = [...document.querySelectorAll('td')].find(e => e.textContent.trim() === label);
    if (!cell?.nextElementSibling) throw new Error(`找不到字段：${label}`);
    return cell.nextElementSibling;
  };

  const openModal = async label => {
    fieldCell(label).querySelector('button').click();
    const hints = { '合同类型': '合同类型', '甲方': '客户', '乙方': '客户', '上级编号': '合同编号LC' };
    return waitFor(() => visibleModals().find(m => m.innerText.includes(hints[label])));
  };

  const selectOption = async (label, text) => {
    fieldCell(label).querySelector('.ant-select').click();
    const option = await waitFor(() => [...document.querySelectorAll('.ant-select-dropdown li')]
      .find(e => e.offsetParent && e.textContent.trim() === text));
    option.click();
    await sleep(350);
  };

  const doubleClickRow = async (modal, text, targetId) => {
    const row = [...modal.querySelectorAll('td')].find(e => e.textContent.trim() === text);
    if (!row) throw new Error(`找不到选项：${text}`);
    row.click();
    row.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, detail: 2 }));
    await sleep(600);
    if (visibleModals().includes(modal) && (!targetId || value(targetId))) {
      const cancel = [...modal.querySelectorAll('button')]
        .find(e => e.offsetParent && e.textContent.replace(/\s/g, '') === '取消');
      if (cancel) cancel.click();
      await sleep(300);
    }
  };

  const selectParty = async (label, name, targetId) => {
    const modal = await openModal(label);
    const advanced = [...modal.querySelectorAll('button')]
      .find(e => e.offsetParent && e.textContent.replace(/\s/g, '') === '高级搜索');
    advanced.click();
    await waitFor(() => modal.querySelector('#name')?.offsetParent);
    setInput(modal.querySelector('#name'), name);
    const search = [...modal.querySelectorAll('button')]
      .find(e => e.offsetParent && e.textContent.replace(/\s/g, '') === '搜索');
    search.click();
    await sleep(900);
    if (![...modal.querySelectorAll('td')].some(e => e.textContent.trim() === name)) {
      const next = modal.querySelector('.ant-pagination-next');
      if (next) {
        next.click();
        await sleep(800);
      }
    }
    await doubleClickRow(modal, name, targetId);
  };

  const fillSelections = async ({ parent, upload = true }) => {
    if (upload) {
      [...document.querySelectorAll('button')].find(b => b.textContent.includes('上传附件')).click();
      await waitFor(() => value('field7071'));
    }
    const typeModal = await openModal('合同类型');
    await doubleClickRow(typeModal, '销售采购合同', 'field7048');
    await selectOption('合同年份', '2026');
    await selectOption('合同单位', '唐山国华科技国际工程有限公司');
    await selectParty('甲方', '唐山国华科技国际工程有限公司', 'field7155');
    await selectParty('乙方', '南通厚普机械科技有限公司', 'field7156');
    const parentModal = await openModal('上级编号');
    setInput(parentModal.querySelector('#htbh1'), parent);
    const search = [...parentModal.querySelectorAll('button')]
      .find(e => e.offsetParent && e.textContent.replace(/\s/g, '') === '搜索');
    search.click();
    await sleep(900);
    const row = [...parentModal.querySelectorAll('td')].find(e => e.textContent.trim() === parent);
    if (!row) throw new Error(`找不到上级合同：${parent}`);
    row.closest('tr').querySelector('input[type=checkbox]').click();
    await sleep(200);
    const confirm = [...parentModal.querySelectorAll('button')]
      .find(e => e.offsetParent && e.textContent.replace(/\s/g, '').startsWith('确定'));
    confirm.click();
    await sleep(400);
    await selectOption('文件类型', '复印件');
    return {
      attachment: value('field7071'),
      first: value('field7155'),
      second: value('field7156'),
      parent: value('field7074'),
      year: value('field8501'),
      unit: value('field8615')
    };
  };

  const fillTextDate = async ({ date, summary }) => {
    setTextarea('field7072', '开票、挂账、付全款');
    setTextarea('field7086', summary);
    document.querySelector('#field7070').parentElement.querySelector('.picker-icon').click();
    const calendar = await waitFor(() => [...document.querySelectorAll('.ant-calendar')].find(e => e.offsetParent));
    const [year, month, day] = date.split('-').map(Number);
    const currentYear = parseInt(calendar.querySelector('.ant-calendar-year-select').textContent, 10);
    const currentMonth = parseInt(calendar.querySelector('.ant-calendar-month-select').textContent, 10);
    const difference = (currentYear - year) * 12 + currentMonth - month;
    const button = calendar.querySelector(difference >= 0 ? '.ant-calendar-prev-month-btn' : '.ant-calendar-next-month-btn');
    for (let i = 0; i < Math.abs(difference); i++) {
      button.click();
      await sleep(70);
    }
    const cell = calendar.querySelector(`td[title="${year}-${month}-${day}"]`);
    if (!cell) throw new Error(`日历中找不到日期：${date}`);
    cell.click();
    await sleep(300);
    return {
      date: value('field7070'),
      display: document.querySelector('#field7070').parentElement.innerText,
      payment: value('field7072'),
      summary: value('field7086')
    };
  };

  const saveAndNew = async () => {
    const button = [...document.querySelectorAll('button')]
      .find(e => e.offsetParent && e.textContent.replace(/\s/g, '') === '保存并新建');
    if (!button) throw new Error('找不到保存并新建按钮');
    button.click();
    const start = Date.now();
    while (Date.now() - start < 6000) {
      await sleep(250);
      if (!value('field7071') && !value('field8172')) {
        return { blank: true, tail: document.body.innerText.slice(-100) };
      }
    }
    return { blank: false, tail: document.body.innerText.slice(-150) };
  };

  return { fillSelections, fillTextDate, saveAndNew, value };
})();
