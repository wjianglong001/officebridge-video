#!/usr/bin/env bash
# 新会话里先运行一次：把仓库挂到 /home/user/obvideo（所有脚本用这个路径），下载字体，整理录屏文件名。
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
[ -e /home/user/obvideo ] || ln -s "$REPO" /home/user/obvideo
[ -e /home/user/OfficeBridge口播稿_定稿.txt ] || ln -s "$REPO/OfficeBridge口播稿_定稿.txt" /home/user/OfficeBridge口播稿_定稿.txt
mkdir -p "$REPO/vendor" "$REPO/out/anim" "$REPO/out/seg"
if [ ! -d "$REPO/vendor/package" ]; then
  (cd "$REPO/vendor" && npm pack @fontsource/noto-sans-sc@5 --silent && tar xzf fontsource-noto-sans-sc-*.tgz)
fi
cd "$REPO/footage"
ln -sf ../第一个视频.mp4 v1.mp4
ln -sf 第二个视频.mp4 v2.mp4
ln -sf ../第三个视频.mp4 v3.mp4
ln -sf ../第四个视频.mp4 v4.mp4
echo "准备完成。下一步：bash build_anim.sh 导出动画，然后 cd build && python3 make.py 合成成片"
