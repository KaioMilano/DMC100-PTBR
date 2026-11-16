const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({testDir:'./browser-tests',workers:1,reporter:'list',
  use:{headless:true,viewport:{width:1440,height:1100},deviceScaleFactor:1,
    launchOptions:process.env.DMC_CHROME_PATH?{executablePath:process.env.DMC_CHROME_PATH}:{}},
});
