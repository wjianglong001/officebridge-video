# 用 MiniMax 语音合成接口逐段生成配音（读环境变量，不在任何文件里保存 key）。
# 环境变量：MINIMAX_API_BASE_URL、MINIMAX_TTS_API_KEY、MINIMAX_VOICE_ID
# 用法：SPEED=1.1 python3 tools/tts.py [段号...]   之后用 tools/concat.py 拼接，再按 HANDOFF.md 做后期提亮
import json, os, sys, urllib.request, pathlib

HOST = os.environ['MINIMAX_API_BASE_URL'].rstrip('/')
KEY = os.environ['MINIMAX_TTS_API_KEY']
VOICE = os.environ.get('MINIMAX_VOICE_ID', 'wjianglong001_A3plus1_20261027')
OUT = pathlib.Path('/home/user/obvideo/audio')

paras = [p.strip() for p in open('/home/user/OfficeBridge口播稿_定稿.txt', encoding='utf-8').read().split('\n\n') if p.strip()]
only = [int(x) for x in sys.argv[1:]] or list(range(1, len(paras) + 1))
speed = float(os.environ.get('SPEED', '1.1'))
pitch = int(os.environ.get('PITCH', '0'))
emotion = os.environ.get('EMOTION')
suffix = os.environ.get('SUFFIX', '')

for i in only:
    payload = {
        'model': 'speech-2.8-hd',
        'text': paras[i - 1],
        'stream': False,
        'voice_setting': {'voice_id': VOICE, 'speed': speed, 'vol': 1.0, 'pitch': pitch, **({'emotion': emotion} if emotion else {})},
        'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1},
        'language_boost': 'Chinese',
    }
    req = urllib.request.Request(HOST + '/v1/t2a_v2', data=json.dumps(payload).encode(),
                                 headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print(f'段{i} HTTP {e.code}: {e.read()[:300]!r}'); continue
    base = data.get('base_resp', {})
    if base.get('status_code') != 0:
        print(f'段{i} 失败: {base}'); continue
    (OUT / f'p{i}{suffix}.mp3').write_bytes(bytes.fromhex(data['data']['audio']))
    info = data.get('extra_info', {})
    print(f'段{i} 成功 时长{info.get("audio_length")}ms')
