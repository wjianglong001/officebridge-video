#!/usr/bin/env bash
# 把所有动画场景导出成视频。透明叠加层是 ProRes 4444 (.mov)，背景是 H.264。
# 时间点可通过 --q 传参调整，例如 s03 的 tB/tC、s01 的 tP2、s09 的 tI/tQ/tF、s08 的 t1..t4。
set -e
cd "$(dirname "$0")/anim"
O=../out/anim; mkdir -p $O
r(){ node render.js "$@" >/dev/null; echo "ok $2"; }
r scenes/bg.html $O/bg.mp4 --dur 20
r scenes/s01_hook.html $O/s01_hook.mov --dur 12 --alpha
r scenes/s02_name.html $O/s02_name.mov --dur 11 --alpha
r scenes/s03_project.html $O/s03_project.mov --dur 25 --alpha
r scenes/s09_summary.html $O/s09_summary.mov --dur 27 --alpha
r scenes/s04_chapter.html $O/ch1.mov --dur 3.2 --alpha --q "n=01&title=你选哪，它改哪&sub=只改你选中的格子"
r scenes/s04_chapter.html $O/ch2.mov --dur 3.2 --alpha --q "n=02&title=多步任务，自动接力&sub=应用之后，它自己接着干"
r scenes/s04_chapter.html $O/ch3.mov --dur 3.2 --alpha --q "n=03&title=多表联合分析&sub=汇总 · 匹配 · 找出超预算"
r scenes/s04_chapter.html $O/ch4.mov --dur 3.2 --alpha --q "n=04&title=自由切换 AI 工具&sub=用你自己的 AI"
r scenes/s07_count.html $O/count27.mov --dur 5 --alpha --w 900 --h 380
r scenes/s08_ai.html $O/ai_switch.mov --dur 12 --alpha --w 1300 --h 340
r scenes/s06_speed.html $O/speed.mov --dur 2 --alpha --w 420 --h 100
i=0
for t in "只改选中的 8 格|cyan" "选区外的数据，一个没动|green" "第 1 次应用：建好汇总表|cyan" "没输入「继续」，它自己接着干|violet" "第 2 次应用：生成折线图|cyan" "同一份预算，不重复计算|violet"; do
  i=$((i+1)); r scenes/s05_callout.html $O/callout$i.mov --dur 3 --alpha --w 1000 --h 160 --q "text=${t%|*}&color=${t#*|}"
done
# 章节常驻角标（透明 PNG）
for n in "01|你选哪，它改哪" "02|多步任务，自动接力" "03|多表联合分析" "04|自由切换 AI 工具"; do
node -e "
const {chromium}=require('playwright');const path=require('path');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.resolve('scenes/s04_chapter.html')+'?mode=badge&n=${n%%|*}&title='+encodeURIComponent('${n#*|}'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
await p.screenshot({path:'$O/badge${n%%|*}.png',omitBackground:true});await b.close();})()"
done
echo done
