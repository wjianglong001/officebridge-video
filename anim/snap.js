// 预览用：在指定时间点截图。node snap.js 场景.html 输出前缀 1,3,8 [w h] [query]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [scene, prefix, times, w = 1920, h = 1080, q = ''] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: +h } });
  await p.goto('file://' + path.resolve(scene) + '?preview=1' + (q ? '&' + q : ''));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  for (const t of times.split(',').map(Number)) {
    await p.evaluate((ms) => { document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }); if (window.seek) window.seek(ms / 1000); }, t * 1000);
    await p.screenshot({ path: `${prefix}_${t}.png` });
  }
  await b.close();
})();
