#!/usr/bin/env bash
# 导出成片需要的全部动画到 out/anim/。时间参数由 build/params.py 按配音计算。
set -e
cd /home/user/obvideo/anim
O=../out/anim; mkdir -p $O
P(){ python3 -c "import sys;sys.path.insert(0,'/home/user/obvideo/build');import params;print($1)"; }
r(){ node render.js "$@" >/dev/null; echo "ok $2"; }
r scenes/bg.html $O/bg.mp4 --dur 20
r scenes/s01b_open.html $O/s01b_open.mov --alpha --dur "$(P "params.SEG['open'][1]-params.SEG['open'][0]")" --q "$(P "params.SCENES['open']")"
r scenes/s03b_project.html $O/s03b_project.mov --alpha --dur "$(P "params.SEG['project'][1]-params.SEG['project'][0]")" --q "$(P "params.SCENES['project']")"
r scenes/s09b_summary.html $O/s09b_summary.mov --alpha --dur "$(P "params.SEG['outro'][1]-params.SEG['outro'][0]")" --q "$(P "params.SCENES['outro']")"
r scenes/s08_ai.html $O/ai_switch.mov --alpha --w 1300 --h 340 --dur "$(P "params.SEG['d4'][1]-params.SEG['d4'][0]")" --q "$(P "params.AI_Q")"
r scenes/s07_count.html $O/count27.mov --alpha --w 900 --h 380 --dur "$(P "params.COUNT_DUR")" --q "tOut=$(P "round(params.COUNT_DUR-0.45,2)")"
r scenes/s04_chapter.html $O/ch1.mov --dur 3.2 --alpha --q "n=01&title=你选哪，它改哪&sub=只改你选中的格子"
r scenes/s04_chapter.html $O/ch2.mov --dur 3.2 --alpha --q "n=02&title=多步任务，自动接力&sub=应用之后，它自己接着干"
r scenes/s04_chapter.html $O/ch3.mov --dur 3.2 --alpha --q "n=03&title=多表联合分析&sub=汇总 · 匹配 · 找出超预算"
r scenes/s04_chapter.html $O/ch4.mov --dur 3.2 --alpha --q "n=04&title=自由切换 AI 工具&sub=用你自己的 AI"
r scenes/s06_speed.html $O/speed.mov --dur 2 --alpha --w 420 --h 100
i=0
for t in "只改选中的 8 格|cyan" "选区外的数据，一个没动|green" "第 1 次应用：建好汇总表|cyan" "没输入「继续」，它自己接着干|violet" "第 2 次应用：生成折线图|cyan" "同一份预算，不重复计算|violet"; do
  i=$((i+1)); r scenes/s05_callout.html $O/callout$i.mov --dur 3 --alpha --w 1000 --h 160 --q "text=${t%|*}&color=${t#*|}"
done
shot(){ node -e "
const {chromium}=require('playwright');const path=require('path');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.resolve('scenes/$1')+'?'+process.argv[1]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
await p.screenshot({path:'$O/$2',omitBackground:true});await b.close();})()" "$3"; echo "ok $2"; }
shot s04_chapter.html badge01.png "mode=badge&n=01&title=$(node -p 'encodeURIComponent("你选哪，它改哪")')"
shot s04_chapter.html badge02.png "mode=badge&n=02&title=$(node -p 'encodeURIComponent("多步任务，自动接力")')"
shot s04_chapter.html badge03.png "mode=badge&n=03&title=$(node -p 'encodeURIComponent("多表联合分析")')"
shot s04_chapter.html badge04.png "mode=badge&n=04&title=$(node -p 'encodeURIComponent("自由切换 AI 工具")')"
shot placeholder.html placeholder_full.png "mode=full"
shot placeholder.html placeholder_pip.png "mode=pip"
echo done
