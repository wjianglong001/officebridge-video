# 主剪辑程序：按配音时间线逐段合成，再拼接、烧字幕、配音轨。
# 用法：python3 make.py            → 生成全部
#      python3 make.py d2 subs    → 只重做指定步骤（open project d1 d2 d3 d4 outro subs final）
import json, re, subprocess, sys
from pathlib import Path
import params as P

ROOT = Path('/home/user/obvideo')
A = ROOT / 'out/anim'
SEGDIR = ROOT / 'out/seg'; SEGDIR.mkdir(parents=True, exist_ok=True)
FOOT = ROOT / 'footage'
FPS = 30
ENC = ['-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS)]

# 录屏放进 16:9 画面：按高度缩放到 1080，水平居中
FW, FH, FX = 1668, 1080, 126


def ff(args):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *args], check=True)


def bg_input(dur):
    return ['-stream_loop', '-1', '-t', f'{dur:.3f}', '-i', str(A / 'bg.mp4')]


def scene_segment(name, scene_mov):
    """开头/结尾：背景 + 数字人占位 + 右侧动画。"""
    s, e = P.SEG[name]; dur = e - s
    ff([*bg_input(dur), '-loop', '1', '-t', f'{dur:.3f}', '-i', str(A / 'placeholder_full.png'), '-i', str(A / scene_mov),
        '-filter_complex', f'[0][1]overlay=0:0[a];[a][2]overlay=0:0:eof_action=pass,trim=0:{dur:.3f}[v]',
        '-map', '[v]', *ENC, str(SEGDIR / f'{name}.mp4')])


def demo_segment(name):
    """演示段：录屏按锚点变速 + 背景 + 章节卡/角标/提示条/快进标记/小窗占位。"""
    src, anchors = P.DEMO[name]
    s, e = P.SEG[name]; dur = e - s
    pieces, speed_windows = [], []
    for (f0, t0), (f1, t1) in zip(anchors, anchors[1:]):
        d = t1 - t0
        if d <= 0.02:
            continue
        i = len(pieces)
        if f1 - f0 < 0.02:  # 停住画面
            pieces.append(f'[0:v]trim=start={f0:.3f}:duration=0.05,setpts=PTS-STARTPTS,fps={FPS},'
                          f'tpad=stop_mode=clone:stop_duration={d:.3f},trim=duration={d:.3f}[p{i}]')
        else:
            k = d / (f1 - f0)
            pieces.append(f'[0:v]trim=start={f0:.3f}:end={f1:.3f},setpts=(PTS-STARTPTS)*{k:.5f},fps={FPS}[p{i}]')
            if 1 / k >= 1.8 and f1 - f0 >= 5:
                speed_windows.append((t0 - s, t1 - s))
    n = len(pieces)
    graph = ';'.join(pieces)
    graph += ';' + ''.join(f'[p{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0,scale={FW}:{FH}:flags=lanczos,setsar=1[foot]'

    inputs = ['-i', str(FOOT / src), *bg_input(dur)]
    graph += f';[1][foot]overlay={FX}:0[v0]'
    cur, idx = 'v0', 2

    def add(file, at, x, y, loop_png=False, until=None):
        nonlocal graph, cur, idx, inputs
        if loop_png:
            inputs += ['-loop', '1', '-t', f'{dur:.3f}', '-i', str(A / file)]
            en = f":enable='between(t,{at:.3f},{until:.3f})'"
            graph += f';[{cur}][{idx}]overlay={x}:{y}{en}[v{idx}]'
        else:
            inputs += ['-i', str(A / file)]
            graph += f';[{idx}]setpts=PTS+{at:.3f}/TB[o{idx}];[{cur}][o{idx}]overlay={x}:{y}:eof_action=pass[v{idx}]'
        cur = f'v{idx}'; idx += 1

    # 快进标记
    for a, b in speed_windows:
        add('speed.mov', a, 40, 120, loop_png=False)  # 2 秒循环素材，窗口较长时下面再补
        reps = int((b - a) // 2)
        for r in range(1, reps):
            add('speed.mov', a + 2 * r, 40, 120)
    # 章节卡与常驻角标
    ch = {'d1': 1, 'd2': 2, 'd3': 3, 'd4': 4}[name]
    for file, at, x, y in P.OVERLAYS:
        if s <= at < e:
            add(file, at - s, x, y)
    add(f'badge0{ch}.png', 3.3, 0, 0, loop_png=True, until=dur)
    add('placeholder_pip.png', 0, 0, 0, loop_png=True, until=dur)
    graph += f';[{cur}]trim=0:{dur:.3f}[v]'
    ff([*inputs, '-filter_complex', graph, '-map', '[v]', *ENC, str(SEGDIR / f'{name}.mp4')])
    print(name, '快进区间', [(round(a, 1), round(b, 1)) for a, b in speed_windows])


def make_subs():
    """按小句时间生成 ASS 字幕：相邻小句合并成一行（不超过 16 字），去掉句末逗号句号。"""
    C = P.C
    lines, cur = [], None
    for c in C:
        text = c['text']
        if cur and cur['段'] == c['段'] and not re.search(r'[。！？]$', cur['text']) and len(cur['text'] + text) <= 16 and c['end'] - cur['start'] <= 4.0:
            cur['text'] += text; cur['end'] = c['end']
        else:
            if cur: lines.append(cur)
            cur = dict(c)
    lines.append(cur)
    for i, l in enumerate(lines):
        nxt = lines[i + 1]['start'] if i + 1 < len(lines) else l['end'] + 0.5
        l['end'] = nxt - 0.02 if nxt - l['end'] < 0.6 else l['end'] + 0.2
        l['text'] = re.sub(r'[，。；：、]$', '', l['text']).replace('"', '“', 1).replace('"', '”', 1)

    def ts(t):
        h = int(t // 3600); m = int(t % 3600 // 60); sec = t % 60
        return f'{h}:{m:02d}:{sec:05.2f}'

    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,OBSub,58,&H00FFFFFF,&H00FFFFFF,&H00180B07,&H96000000,0,0,0,0,100,100,1,0,1,5,2,2,60,60,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = ''.join(f'Dialogue: 0,{ts(l["start"])},{ts(l["end"])},Sub,,0,0,0,,{l["text"]}\n' for l in lines)
    (ROOT / 'build/subs.ass').write_text(head + body, encoding='utf-8')
    print('字幕', len(lines), '行')


def final():
    order = ['open', 'project', 'd1', 'd2', 'd3', 'd4', 'outro']
    lst = SEGDIR / 'list.txt'
    lst.write_text(''.join(f"file '{SEGDIR / n}.mp4'\n" for n in order))
    ff(['-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(SEGDIR / 'all.mp4')])
    total = P.SEG['outro'][1]
    out = ROOT / 'out/OfficeBridge_成片_数字人占位版.mp4'
    ff(['-i', str(SEGDIR / 'all.mp4'), '-i', str(ROOT / 'audio/OfficeBridge配音_定稿.mp3'),
        '-filter_complex',
        f"[0:v]subtitles={ROOT / 'build/subs.ass'}:fontsdir={ROOT / 'build/fonts'},"
        f"fade=t=in:st=0:d=0.4,fade=t=out:st={total - 0.8:.2f}:d=0.8[v];"
        f"[1:a]apad,atrim=0:{total:.3f},afade=t=out:st={total - 0.8:.2f}:d=0.8[a]",
        '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)])
    print('成片', out)


if __name__ == '__main__':
    steps = sys.argv[1:] or ['open', 'project', 'd1', 'd2', 'd3', 'd4', 'outro', 'subs', 'final']
    for st in steps:
        if st == 'open': scene_segment('open', 's01b_open.mov')
        elif st == 'project': scene_segment('project', 's03b_project.mov')
        elif st == 'outro': scene_segment('outro', 's09b_summary.mov')
        elif st in ('d1', 'd2', 'd3', 'd4'): demo_segment(st)
        elif st == 'subs': make_subs()
        elif st == 'final': final()
        print('完成', st)
