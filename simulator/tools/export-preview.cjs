/* Export authorial previews only. Requires dev dependency and a local browser. */
const {chromium}=require('@playwright/test');const fs=require('node:fs/promises');
const path=require('node:path');const {pathToFileURL}=require('node:url');
(async()=>{
  const directory=path.resolve(process.argv[2]||'../docs/images');await fs.mkdir(directory,{recursive:true});
  const browser=await chromium.launch({headless:true,...(process.env.DMC_CHROME_PATH?{executablePath:process.env.DMC_CHROME_PATH}:{})});
  try {
    const page=await browser.newPage({viewport:{width:1200,height:1100},deviceScaleFactor:1});
    await page.goto(pathToFileURL(path.resolve(__dirname,'../gallery.html')).href);
    await page.locator('#gallery section').last().waitFor();await page.evaluate(()=>document.fonts.ready);
    await page.screenshot({path:path.join(directory,'comparacao-quatro-telas.png'),fullPage:true});
    for(const screen of ['measurement','settings','history','about']) await page.locator(`section[data-screen="${screen}"]`).screenshot({path:path.join(directory,`comparacao-${screen}.png`)});
    await page.goto(pathToFileURL(path.resolve(__dirname,'../index.html')).href);
    await page.locator('#scale').selectOption('1');await page.locator('[data-screen="settings"]').click();
    await page.locator('#variant').selectOption('full');await page.locator('#font').selectOption('32');
    await page.locator('.comparison').screenshot({path:path.join(directory,'estresse-fonte-32.png')});
    console.log('Authorial PNG comparisons saved to '+directory);
  } finally {await browser.close();}
})().catch(error=>{console.error(error.message);process.exitCode=1;});
