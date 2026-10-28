# 把口播稿按标点切成小句，用配音里的停顿位置估算每个小句的起止时间。
import json, re, subprocess

AUDIO = '/home/user/obvideo/audio'
paras = [p.strip() for p in open('/home/user/OfficeBridge口播稿_定稿.txt', encoding='utf-8').read().split('\n\n') if p.strip()]
timing = json.load(open(f'{AUDIO}/timing.json'))

def weight(s):
    # 估算念这段文字要多久的相对权重：汉字记 1，英文单词按音节粗算
    w = len(re.findall(r'[一-鿿]', s))
    for word in re.findall(r'[A-Za-z]+', s):
        w += {'AI': 2, 'WPS': 3, 'Hello': 2, 'OfficeBridge': 4, 'Codex': 2, 'WorkBuddy': 3, 'Excel': 2, 'Windows': 2}.get(word, max(1, len(word) // 3))
    return max(w, 1)

def pauses(path):
    out = subprocess.run(['ffmpeg', '-v', 'info', '-i', path, '-af', 'silencedetect=n=-38dB:d=0.12', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', out)]
    en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', out)]
    return list(zip(st, en))

result = []
for i, text in enumerate(paras, 1):
    dur = timing[i - 1]['时长']; base = timing[i - 1]['开始']
    ps = pauses(f'{AUDIO}/p{i}.mp3')
    v0 = ps[0][1] if ps and ps[0][0] < 0.05 else 0.0           # 开头静音结束
    v1 = ps[-1][0] if ps and ps[-1][1] > dur - 0.1 else dur      # 结尾静音开始
    inner = [p for p in ps if p[0] > v0 + 0.05 and p[1] < v1 - 0.05]
    clauses = [c for c in re.findall(r'[^，。：；！？、]+[，。：；！？、]?', text) if c.strip()]
    ws = [weight(c) for c in clauses]
    # 逐个边界：按剩余字数比例估算位置，就近吸附到停顿（±1.0 秒内），吸附后重新以此为锚点
    starts = [v0]; ends = []
    anchor_t, anchor_k = v0, 0
    used = -1
    for k in range(1, len(clauses)):
        rem_w = sum(ws[anchor_k:]); done_w = sum(ws[anchor_k:k])
        est = anchor_t + (v1 - anchor_t) * done_w / rem_w
        cands = [(abs((a + b) / 2 - est), j) for j, (a, b) in enumerate(inner) if j > used and abs((a + b) / 2 - est) < 1.0]
        if cands:
            _, j = min(cands); a, b = inner[j]; used = j
            ends.append(a); starts.append(b); anchor_t, anchor_k = b, k
        else:
            ends.append(est); starts.append(est)
    ends.append(v1)
    for c, s, e in zip(clauses, starts, ends):
        result.append({'段': i, 'text': c, 'start': round(base + s, 2), 'end': round(base + e, 2)})

json.dump(result, open('/home/user/obvideo/build/clauses.json', 'w'), ensure_ascii=False, indent=1)
for r in result:
    print(f"{r['段']} {r['start']:7.2f}-{r['end']:7.2f} {r['text']}")
