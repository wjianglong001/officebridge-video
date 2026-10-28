// 把一个 HTML 动画场景逐帧截图，交给 ffmpeg 编码成视频。
// 用法：node render.js <场景.html> <输出文件> --dur 6 [--w 1920 --h 1080 --fps 30 --alpha --q "text=..."]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

function parseArgs(argv) {
  const opts = { w: 1920, h: 1080, fps: 30, dur: 5, alpha: false, q: '' };
  const pos = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--alpha') opts.alpha = true;
    else if (a.startsWith('--')) opts[a.slice(2)] = argv[++i];
    else pos.push(a);
  }
  ['w', 'h', 'fps', 'dur'].forEach((k) => (opts[k] = Number(opts[k])));
  return { scene: pos[0], out: pos[1], ...opts };
}

(async () => {
  const o = parseArgs(process.argv.slice(2));
  const frames = Math.round(o.dur * o.fps);
  const codec = o.alpha
    ? ['-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le']
    : ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p'];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(o.fps), '-i', '-', ...codec, o.out], {
    stdio: ['pipe', 'inherit', 'inherit'],
  });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: o.w, height: o.h } });
  const url = 'file://' + path.resolve(o.scene) + (o.q ? '?' + o.q : '');
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  for (let f = 0; f < frames; f++) {
    const t = f / o.fps;
    await page.evaluate((ms) => {
      document.getAnimations().forEach((a) => {
        a.pause();
        a.currentTime = ms;
      });
      if (window.seek) window.seek(ms / 1000);
    }, t * 1000);
    const buf = await page.screenshot({ type: 'png', omitBackground: o.alpha });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await browser.close();
  await new Promise((r) => ff.on('close', r));
  console.log(`done ${o.out} (${frames} frames)`);
})();
