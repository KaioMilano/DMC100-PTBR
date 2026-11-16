const {test,expect}=require('@playwright/test'),{pathToFileURL}=require('node:url'),path=require('node:path');
test.beforeEach(async({page})=>page.goto(pathToFileURL(path.resolve(__dirname,'../index.html')).href));
test('offline reference screens have valid dimensions and no external requests',async({page})=>{
  const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});await page.reload();
  await expect(page.locator('#nav-pt svg')).toHaveAttribute('viewBox','0 0 240 320');
  for(const area of ['measurement','history','settings','reset','about']){await page.locator(`[data-go="${area}"]`).click();expect(await page.evaluate(()=>DmcNavigatorState.issues)).toEqual([]);}
  expect(errors).toEqual([]);expect(requests).toEqual([]);
});
test('Portuguese menu selection applies only after explicit confirmation and follows chosen locale',async({page})=>{
  await page.locator('[data-go="settings"]').click();
  await expect(page.locator('#nav-pt [data-label="option2"]')).toHaveText('Português (BR) *');
  await page.locator('#nav-pt [data-action="OPTION"][data-index="2"]').click();
  expect(await page.evaluate(()=>DmcNavigatorState.state.settings.language)).toBe(1);
  await page.locator('#cancel-language').click();expect(await page.evaluate(()=>DmcNavigatorState.state.settings.language)).toBe(1);
  await page.locator('#nav-pt [data-action="OPTION"][data-index="2"]').click();await page.locator('#apply-language').click();
  await expect(page.locator('#nav-language')).toHaveValue('selected');await expect(page.locator('[data-panel="en"]')).toBeHidden();
  await expect(page.locator('#nav-feedback')).toContainText('pt-BR');await page.locator('[data-go="history"]').click();
  await expect(page.locator('#nav-pt [data-label="title"]')).toHaveText('Histórico');
});
test('English and Chinese remain selectable and preview does not override the saved model locale',async({page})=>{
  await page.locator('[data-go="settings"]').click();
  await page.locator('#nav-pt [data-action="OPTION"][data-index="0"]').click();await page.locator('#apply-language').click();
  await expect(page.locator('[data-panel="zh"]')).toBeVisible();await expect(page.locator('#nav-zh [data-label="title"]')).toHaveText('系统设置');
  await expect(page.locator('#nav-evidence')).toContainText('prévia autoral não validada');
  await page.locator('#nav-zh [data-action="OPTION"][data-index="1"]').click();await page.locator('#apply-language').click();
  await expect(page.locator('[data-panel="en"]')).toBeVisible();await expect(page.locator('#nav-en [data-label="title"]')).toHaveText('System settings');
  await page.locator('#nav-language').selectOption('pt');expect(await page.evaluate(()=>DmcNavigatorState.state.settings.language)).toBe(1);
});
test('physical controls navigate tabs and change menu focus',async({page})=>{
  await page.locator('#menu-toggle').click();await page.locator('[data-key="RIGHT"]').click();
  await expect(page.locator('#nav-pt [data-label="title"]')).toHaveText('Configurações');
  await page.locator('[data-key="MODE"]').click();await page.locator('[data-key="RIGHT"]').click();
  await expect(page.locator('#nav-evidence')).toContainText('não demonstrada');
  await page.locator('[data-key="MODE"]').click();await page.locator('[data-key="RIGHT"]').click();await page.locator('[data-key="MODE"]').click();
  expect(await page.evaluate(()=>DmcNavigatorState.state.settings.brightness)).toBe(4);
});
test('language selector, font stress and export remain separate from navigation state',async({page})=>{
  await page.locator('[data-go="settings"]').click();await page.locator('#nav-language').selectOption('pt');
  await expect(page.locator('[data-panel="en"]')).toBeHidden();await expect(page.locator('[data-panel="pt"]')).toBeVisible();
  await page.locator('#nav-variant').selectOption('ascii');await expect(page.locator('#nav-pt [data-label="title"]')).toHaveText('Configuracoes');
  await page.locator('#nav-font').selectOption('32');expect((await page.evaluate(()=>DmcNavigatorState.issues)).length).toBeGreaterThan(0);
  const promise=page.waitForEvent('download');await page.locator('#nav-export-svg').click();const download=await promise;
  const stream=await download.createReadStream();let svg='';for await(const b of stream)svg+=b.toString();expect(svg).toContain('width="240" height="320"');expect(svg).not.toContain('<image');
});
test('reset button requires two explicit clicks and affects local options only',async({page})=>{
  await page.locator('[data-page="1"]').click();await page.locator('#nav-pt [data-action="OPTION"][data-index="0"]').click();
  await page.locator('[data-go="reset"]').click();await page.locator('#nav-pt [data-action="RESET_CONFIRM"]').click();
  expect(await page.evaluate(()=>DmcNavigatorState.state.settings.brightness)).toBe(0);
  await page.locator('#nav-pt [data-action="RESET_CONFIRM"]').click();await expect(page.locator('#nav-feedback')).toContainText('valores simulados');
  expect(await page.evaluate(()=>DmcNavigatorState.state.settings.brightness)).toBe(3);
});
test('long SAVE opens menu without saving a sample, keyboard and mobile stay usable',async({page})=>{
  const button=page.locator('#save-menu');await button.hover();await page.mouse.down();await page.waitForTimeout(700);await page.mouse.up();
  expect(await page.evaluate(()=>DmcNavigatorState.state.area)).toBe('menu');expect(await page.evaluate(()=>DmcNavigatorState.state.records.length)).toBe(6);
  await page.keyboard.press('ArrowRight');expect(await page.evaluate(()=>DmcNavigatorState.state.tab)).toBe(1);
  await page.setViewportSize({width:390,height:844});await page.locator('[data-go="about"]').click();
  await expect(page.locator('#nav-pt [data-label="version"]')).toHaveText('DMC-100 V1.3');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
