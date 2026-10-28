#!/usr/bin/env bash
# 新会话里先运行一次：下载思源黑体（Noto Sans SC，OFL 开源字体）到 vendor/
set -e
cd "$(dirname "$0")"
mkdir -p vendor && cd vendor
npm pack @fontsource/noto-sans-sc@5 --silent
tar xzf fontsource-noto-sans-sc-*.tgz
echo "字体就绪：$(pwd)/package"
