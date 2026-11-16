const {test,expect}=require('@playwright/test');
const {pathToFileURL}=require('node:url');const path=require('node:path');
const url=pathToFileURL(path.resolve(__dirname,'../lab.html')).href;
test.beforeEach(async({page})=>{await page.goto(url);});
test('opens directly from file, has no errors or network access and both 240x320 SVGs',async({page})=>{
  const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
  await page.reload();await expect(page.locator('#en svg')).toHaveAttribute('width','240');
  await expect(page.locator('#pt svg')).toHaveAttribute('height','320');
  await expect(page.locator('body')).toContainText('Dados sintéticos');
  expect(errors).toEqual([]);expect(requests).toEqual([]);
});
test('all five default screens are readable within declared boxes',async({page})=>{
  for(const name of ['measurement','settings','history','about','alerts']) {
    await page.locator(`[data-screen="${name}"]`).click();
    expect(await page.evaluate(()=>DmcDiagnostics.issues)).toEqual([]);
    await expect(page.locator(`[data-screen="${name}"]`)).toHaveAttribute('aria-pressed','true');
  }
});
test('full/compact/ascii, font stress and custom strings update actual rendering',async({page})=>{
  await page.locator('[data-screen="settings"]').click();
  await page.locator('#variant').selectOption('full');
  await expect(page.locator('#pt [data-label="temperature"]')).toHaveText('Unidade de temperatura');
  await page.locator('#font').selectOption('32');
  expect((await page.evaluate(()=>DmcDiagnostics.issues)).length).toBeGreaterThan(0);
  await expect(page.locator('#diagnostics')).toContainText('Nada foi reduzido');
  await page.locator('#variant').selectOption('ascii');
  await expect(page.locator('#pt [data-label="title"]')).toHaveText('Configuracoes');
  await page.locator('#custom').fill('<script>teste</script>');
  await expect(page.locator('#pt [data-label="title"]')).toHaveText('<script>teste</script>');
  expect(await page.locator('#pt script').count()).toBe(0);
});
test('catalog search finds the duplicate offset and export preserves metadata',async({page})=>{
  await page.locator('summary').click();await page.locator('#catalog-search').fill('0x006150');
  await expect(page.locator('#catalog-body tr')).toHaveCount(1);
  await expect(page.locator('#catalog-body')).toContainText('0x005A44 · 0x006150');
  const downloadPromise=page.waitForEvent('download');await page.locator('#export-catalog').click();
  const download=await downloadPromise;const stream=await download.createReadStream();let data='';for await(const chunk of stream)data+=chunk.toString();
  const catalog=JSON.parse(data);expect(catalog.entries.find(x=>x.id==='language').occurrences).toEqual([0x5a44,0x6150]);
});
test('SVG export is the exact display, scale changes only presentation',async({page})=>{
  await page.locator('#scale').selectOption('2');
  expect(await page.locator('#pt svg').evaluate(e=>e.getBoundingClientRect().width)).toBe(480);
  const promise=page.waitForEvent('download');await page.locator('[data-export="pt"]').click();
  const download=await promise;const stream=await download.createReadStream();let svg='';for await(const chunk of stream)svg+=chunk.toString();
  expect(svg).toContain('width="240" height="320"');expect(svg).toContain('Medição');expect(svg).not.toContain('<image');
});
test('mobile keeps controls accessible and comparison horizontally scrollable',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.locator('[data-screen="history"]').click();
  await expect(page.locator('#screen-name')).toHaveText('Histórico');
  expect(await page.locator('.pair').evaluate(e=>e.scrollWidth>e.clientWidth)).toBe(true);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
