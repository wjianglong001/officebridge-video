# 把 p1..p8 拼成一整条，段间留 0.5 秒停顿，并记录每段起止时间
import subprocess, json, sys
gap = 0.5; t = 0; segs = []; inputs = []; chain = []; pieces = []
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for i in range(1, N + 1):
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'p{i}.mp3']).decode())
    segs.append({'段': i, '开始': round(t, 2), '结束': round(t + d, 2), '时长': round(d, 2)})
    inputs += ['-i', f'p{i}.mp3']
    chain.append(f'[{i-1}:a]aresample=32000,aformat=channel_layouts=mono[a{i}]')
    pieces.append(f'[a{i}]')
    if i < N:
        chain.append(f'anullsrc=r=32000:cl=mono,atrim=0:{gap}[s{i}]'); pieces.append(f'[s{i}]')
    t += d + (gap if i < N else 0)
chain.append(''.join(pieces) + f'concat=n={len(pieces)}:v=0:a=1[out]')
subprocess.check_call(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(chain), '-map', '[out]', '-c:a', 'libmp3lame', '-b:a', '192k', sys.argv[1]])
json.dump(segs, open('timing.json', 'w'), ensure_ascii=False, indent=1)
for s in segs: print(s)
print('总长', round(t, 2))
