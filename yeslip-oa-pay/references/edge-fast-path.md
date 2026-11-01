# Edge 快速路径与已验证脚本

本文件用于本机 Edge + `kimi-webbridge`。目标是把每份合同的浏览器调用压缩为“合同关联一次、付款信息一次、截图一次、提交一次、已办核验一次”，同时保留精确匹配和读回校验。

## 固定地址

门户：

```text
http://114.116.12.172:8899/wui/index.html#/main/portal/portal-10-15
```

销售设备付款创建页（`workflowid=108`，包含已验证的门户参数）：

```text
http://114.116.12.172:8899/spa/workflow/static4form/index.html?_rdm=1677035146187#/main/workflow/req?iscreate=1&workflowid=108&isagent=0&beagenter=0&f_weaver_belongto_userid=&f_weaver_belongto_usertype=0&menuIds=1,12&menuPathIds=1,12&preloadkey=1677035146187&timestamp=1677035146187&_key=prfqcd
```

首次没有可用创建页时，用 `navigate` 打开一次销售付款创建页。后续合同复用该标签：提交后页面仍保留时，在当前标签原地 `navigate` 到同一创建地址，刷新为空白表单后继续；不要为每份合同设置 `newTab:true`，也不要重开首页。若创建页自动关闭，复用本任务已有标签进入创建页。若 OA 后续更新导致该地址无权限，回已有门户读取「销售付款」快捷入口配置里的 `link`，不要反复尝试点击。

## 合同关联模板

把 `__CONTRACT_NO__` 替换为文件名开头的 GHI 编号，把 `__SALES_CONTRACT_NO__` 替换为文件名中的 BGJ 编号；若文件名没有 BGJ 编号，可替换为空字符串。将整段作为 WebBridge `evaluate` 的 `code` 执行。

该脚本只关联合同和读到款，不选择付款内容、不提交。返回 `earlyPass:false` 时立即停止本单。

```javascript
(async () => {
  const id = '__CONTRACT_NO__';
  const sales = '__SALES_CONTRACT_NO__';
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  function docs() {
    const a = [document];
    for (const f of document.querySelectorAll('iframe')) {
      try { if (f.contentDocument) a.push(f.contentDocument); } catch (e) {}
    }
    return a;
  }
  function all(selector) {
    return docs().flatMap(d => [...d.querySelectorAll(selector)]);
  }
  async function wait(fn, ms = 12000) {
    const start = Date.now();
    while (Date.now() - start < ms) {
      try { const value = fn(); if (value) return value; } catch (e) {}
      await sleep(200);
    }
    throw new Error('页面联动等待超时');
  }
  function setValue(el, value) {
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  const row = label => {
    const el = all('td').find(x => x.textContent.trim() === label);
    return el ? el.parentElement.innerText.trim() : null;
  };
  const nums = text => (text || '').match(/-?\d+(?:\.\d+)?/g) || [];

  const label = await wait(() => all('td').find(x => x.textContent.trim() === '合同编号'));
  const searchButton = label.closest('tr').querySelector('button');
  if (!searchButton) throw new Error('未找到合同搜索按钮');
  searchButton.click();

  const search = await wait(() => all('button').find(x => x.textContent.trim() === '搜 索'));
  const input = search.ownerDocument.querySelector('form input');
  if (!input) throw new Error('未找到合同编号输入框');
  setValue(input, id);
  search.click();

  const cell = await wait(() => all('td').find(x => x.textContent.trim() === id));
  cell.closest('tr').click();
  await wait(() => {
    const text = document.body.innerText;
    const linkedAmount = Number(nums(row('合同金额(万元)')).slice(-1)[0]);
    return text.includes(id) && (!sales || text.includes(sales)) && linkedAmount > 0;
  });

  const amountText = row('合同金额(万元)');
  const receivedText = row('已到款金额(万元)');
  const receiverLabel = all('td').find(x => x.textContent.trim() === '收款单位');
  const receiverValue = receiverLabel && receiverLabel.nextElementSibling
    ? receiverLabel.nextElementSibling.innerText.trim() : '';
  const contract = Number(nums(amountText).slice(-1)[0]);
  const received = Number(nums(receivedText).slice(-1)[0]);
  const minReceived = contract / 0.8;
  return JSON.stringify({
    stage: 'contract_linked',
    id,
    amountText,
    receivedText,
    receiverRow: row('收款单位'),
    receiverValue,
    contract,
    received,
    minReceived,
    difference: Math.max(0, minReceived - received),
    earlyPass: Boolean(receiverValue) && contract > 0 && received >= minReceived
  });
})()
```

## 付款信息模板

仅在合同关联模板返回 `earlyPass:true` 后执行。替换 `__PAYMENT_RATIO__` 和 `__REMARK__`。该脚本选择到货款、写备注、按稳定异步顺序设置比例，并读回所有关键值；不会点击提交。

```javascript
(async () => {
  const targetRatio = Number('__PAYMENT_RATIO__');
  const remark = '__REMARK__';
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  function docs() {
    const a = [document];
    for (const f of document.querySelectorAll('iframe')) {
      try { if (f.contentDocument) a.push(f.contentDocument); } catch (e) {}
    }
    return a;
  }
  function all(selector) {
    return docs().flatMap(d => [...d.querySelectorAll(selector)]);
  }
  async function wait(fn, ms = 12000) {
    const start = Date.now();
    while (Date.now() - start < ms) {
      try { const value = fn(); if (value) return value; } catch (e) {}
      await sleep(200);
    }
    throw new Error('页面联动等待超时');
  }
  function setValue(el, value) {
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  const row = label => {
    const el = all('td').find(x => x.textContent.trim() === label);
    return el ? el.parentElement.innerText.trim() : null;
  };
  const nums = text => (text || '').match(/-?\d+(?:\.\d+)?/g) || [];

  const payLabel = await wait(() => all('td').find(x => x.textContent.trim() === '付款内容'));
  const select = payLabel.closest('tr').querySelector('.ant-select');
  if (!select) throw new Error('未找到付款内容下拉框');
  select.click();
  const option = await wait(() => all('li').find(x => x.textContent.trim() === '到货款' && x.offsetParent !== null));
  option.click();
  await sleep(500);

  setValue(document.getElementById('field6527'), remark);

  const ratioInput = document.getElementById('field8896');
  ratioInput.focus();
  ratioInput.dispatchEvent(new FocusEvent('focus'));
  await sleep(150);
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(ratioInput, targetRatio.toFixed(2));
  ratioInput.dispatchEvent(new Event('input', { bubbles: true }));
  await sleep(300);
  ratioInput.dispatchEvent(new KeyboardEvent('keyup', { key: '0', bubbles: true }));
  ratioInput.dispatchEvent(new Event('change', { bubbles: true }));
  await sleep(300);
  ratioInput.blur();
  ratioInput.dispatchEvent(new FocusEvent('blur'));
  await sleep(1200);

  const amountText = row('合同金额(万元)');
  const receivedText = row('已到款金额(万元)');
  const contract = Number(nums(amountText).slice(-1)[0]);
  const received = Number(nums(receivedText).slice(-1)[0]);
  const ratio = Number(document.getElementById('field8896').value);
  const paid = Number(document.getElementById('field8269').value);
  const expectedPaid = contract * ratio / 100;
  const content = [...document.querySelectorAll('.ant-select-selection-selected-value')]
    .map(e => e.textContent.trim()).filter(Boolean);
  return JSON.stringify({
    stage: 'payment_filled',
    amountText,
    receivedText,
    receiverRow: row('收款单位'),
    paymentContent: content,
    ratio,
    paid,
    expectedPaid,
    minReceived: contract / 0.8,
    remark: document.getElementById('field6527').value,
    pass: ratio === targetRatio &&
      content.length === 1 && content[0] === '到货款' &&
      received >= contract / 0.8 &&
      Math.abs(paid - expectedPaid) < 0.000001 &&
      document.getElementById('field6527').value === remark
  });
})()
```

## 已办核验模板

提交后切换回本任务已有门户标签，整页 `navigate` 刷新，再读取流程链接；不要重新打开首页。核验后返回已有销售付款标签，原地刷新并继续下一份。不要只做字符串包含匹配，因为 `0.8` 会误中 `0.888`。提取标题中的金额并转为数值，同时核对申请人、日期、收款单位和新记录时间；不要把历史同金额记录当作本单。

第一次整页刷新未找到时只允许再整页刷新一次。仍无结果则标记“提交结果未核实”，不要重复提交；后续仍在原销售付款标签中处理其他合同。
