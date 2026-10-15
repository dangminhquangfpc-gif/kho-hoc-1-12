const {chromium}=require('playwright');
(async()=>{
 const token=process.env.KHOHOC_ADMIN_TOKEN; if(!token) throw Error('Set local KHOHOC_ADMIN_TOKEN');
 const browser=await chromium.launch({executablePath:process.env.CHROME_EXECUTABLE||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 page.setDefaultTimeout(90000); await page.goto('http://127.0.0.1:3000/',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForURL('**/login');
 await page.getByLabel('Token quản trị').fill('wrong-token');
 await page.getByRole('button',{name:'Đăng nhập'}).click();
 await page.locator('p[role="alert"]').waitFor();
 await page.getByLabel('Token quản trị').fill(token);
 await page.getByRole('button',{name:'Đăng nhập'}).click();
 await page.getByRole('heading',{name:'Kiểm duyệt nội dung'}).waitFor();
 const exported=await page.evaluate(async()=>{const r=await fetch('/api/export');return {status:r.status,data:r.ok?await r.json():null};});
 if(exported.status!==200)throw Error('Admin export failed: '+exported.status);
 if(exported.data.questions.length!==108)throw Error('Wrong dataset count');
 
 await page.getByRole('button',{name:'Đăng xuất'}).click();
 await page.waitForURL('**/login');
 const afterLogout=await page.evaluate(async()=>{const r=await fetch('/api/export');return r.status;});
 if(afterLogout!==401)throw Error('Export authorization bypass');
 console.log('PASS: login rejection, login, 108-question export, logout, export denied');
 } finally { await browser.close(); }
})().catch(e=>{console.error(e.message);process.exit(1)});
