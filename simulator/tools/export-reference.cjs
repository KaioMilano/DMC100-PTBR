const {chromium}=require('@playwright/test'),path=require('node:path'),fs=require('node:fs/promises'),{pathToFileURL}=require('node:url');
(async()=>{const directory=path.resolve(process.argv[2]||'../docs/images');await fs.mkdir(directory,{recursive:true});const browser=await chromium.launch({headless:true,...(process.env.DMC_CHROME_PATH?{executablePath:process.env.DMC_CHROME_PATH}:{})});
  try{const page=await browser.newPage({viewport:{width:1200,height:1100},deviceScaleFactor:1});await page.goto(pathToFileURL(path.resolve(__dirname,'../reference-gallery.html')).href);await page.locator('section').last().waitFor();await page.screenshot({path:path.join(directory,'navegacao-v13-comparacao.png'),fullPage:true});
    for(const area of ['measurement','settings','history','about'])await page.locator(`section[data-area="${area}"]`).screenshot({path:path.join(directory,`navegacao-v13-${area}.png`)});
    await page.goto(pathToFileURL(path.resolve(__dirname,'../index.html')).href);await page.locator('#nav-scale').selectOption('1');await page.locator('[data-go="reset"]').click();await page.locator('.comparison').screenshot({path:path.join(directory,'navegacao-v13-reset.png')});console.log('Authorial reference comparisons saved.');
  }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
