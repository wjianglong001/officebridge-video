# 从配音的小句时间推算：各画面段起止、动画时间参数、录屏变速方案、叠加元素出场时间。
import json

C = json.load(open('/home/user/obvideo/build/clauses.json', encoding='utf-8'))
TIMING = json.load(open('/home/user/obvideo/audio/timing.json', encoding='utf-8'))
AUDIO_END = TIMING[-1]['结束']
TAIL = 1.8  # 配音结束后，关注卡多停留的秒数


def T(prefix, seg=None, end=False):
    """返回以 prefix 开头的小句在整条配音里的开始（或结束）时间。"""
    for c in C:
        if c['text'].startswith(prefix) and (seg is None or c['段'] == seg):
            return c['end'] if end else c['start']
    raise KeyError(prefix)


# 画面段边界：取两段配音之间停顿的中点
starts = [t['开始'] for t in TIMING]
V = [0.0] + [round(s - 0.25, 2) for s in starts[1:]] + [round(AUDIO_END + TAIL, 2)]
SEG = {  # 名称: (开始, 结束)
    'open': (V[0], V[1]), 'project': (V[1], V[2]),
    'd1': (V[2], V[3]), 'd2': (V[3], V[4]), 'd3': (V[4], V[5]), 'd4': (V[5], V[6]),
    'outro': (V[6], V[7]),
}


def local(t, seg):
    return round(t - SEG[seg][0], 2)


def q(d):
    return '&'.join(f'{k}={v:.2f}' for k, v in d.items())


SCENES = {
    'open': q({
        'tName': local(T('我是王师兄', 1), 'open') - 0.2,
        'tFirst': local(T('这是我的第一个视频'), 'open'),
        'tAsk': local(T('不知道你'), 'open'),
        'tHead': local(T('让AI帮你'), 'open'),
        'tP1': local(T('你得先把'), 'open'),
        'tP2': local(T('再跟它解释'), 'open'),
        'tP3': local(T('好不容易'), 'open'),
        'tP4': local(T('一不小心'), 'open'),
    }),
    'project': q({
        'tT': local(T('所以我做了'), 'project') + 0.2,
        'tCN': local(T('中文名办公桥'), 'project'),
        'tB': local(T('它直接装在'), 'project'),
        'tN2': local(T('一头连着你电脑'), 'project'),
        'tC': local(T('你选中哪里'), 'project'),
        'tC2': local(T('它先给你看'), 'project'),
        'tD': local(T('下面我用'), 'project'),
    }),
    'outro': q({
        'tP1': local(T('办公桥就在'), 'outro'),
        'tP2': local(T('选哪改哪', 7), 'outro'),
        'tP3': local(T('还能接你'), 'outro'),
        'tI1': local(T('项目本身开源'), 'outro'),
        'tI2': local(T('目前支持'), 'outro'),
        'tI3': local(T('Excel版'), 'outro'),
        'tMe': local(T('我写了五年'), 'outro'),
        'tShare': local(T('以后会在这里'), 'outro'),
        'tQ': local(T('用的时候'), 'outro'),
        'tF': local(T('关注王师兄'), 'outro'),
        'tBye': local(T('我们下期见'), 'outro'),
    }),
}

# 录屏变速方案：每段是 (录屏起点, 录屏终点, 对应的配音时刻)。
# 录屏起点=终点 表示停住画面。锚点之间按比例变速。
DEMO = {
    'd1': ('v1.mp4', [
        (0.0, SEG['d1'][0]),
        (0.5, T('我框选这八格')),           # 开始框选
        (2.0, T('我框选这八格', end=True)),  # 框选完成
        (4.5, T('统一保留两位小数')),        # 开始输入要求
        (6.0, T('输入框自动带上', end=True)),  # 已发送
        (15.0, T('先看预览') + 0.6),         # 等待分析结束，方案出来
        (16.5, T('再点应用', 3) + 0.4),      # 点“应用”
        (19.3, T('一个都没动', end=True)),
        (19.3, SEG['d1'][1]),
    ]),
    'd2': ('v2.mp4', [
        (1.0, SEG['d2'][0]),
        (1.6, T('我直接说')),
        (3.6, T('再画一张折线图', end=True)),  # 发送
        (18.5, T('方案出来')),               # 汇总方案出现
        (20.0, T('我点第一次应用') + 0.5),    # 第一次点“应用”
        (21.2, T('新表建好了', end=True)),
        (28.6, T('第二次点应用') + 0.2),
        (30.0, T('第二次点应用', end=True)),  # 第二次点“应用”
        (32.8, T('齐活', end=True)),
        (32.8, SEG['d2'][1]),
    ]),
    'd3': ('v3.mp4', [
        (0.0, SEG['d3'][0]),
        (0.0, T('费用明细在一张表')),        # 先停在输入框里的要求
        (1.6, T('每个部门有没有超预算', end=True)),  # 发送
        (22.0, T('核对一下方案')),            # 结果说明出来
        (23.0, T('点应用', 5) + 0.3),         # 点“应用”
        (28.7, SEG['d3'][1]),
    ]),
    'd4': ('v4.mp4', [
        (1.2, SEG['d4'][0]),
        (2.0, T('它不挑AI', end=True)),
        (9.2, T('用的都是你', end=True)),
        (9.2, SEG['d4'][1]),
    ]),
}

# 叠加元素：(素材, 出场时刻, x, y)
OVERLAYS = [
    ('ch1.mov', SEG['d1'][0] + 0.15, 0, 0), ('ch2.mov', SEG['d2'][0] + 0.15, 0, 0),
    ('ch3.mov', SEG['d3'][0] + 0.15, 0, 0), ('ch4.mov', SEG['d4'][0] + 0.15, 0, 0),
    ('callout1.mov', T('八格全变成'), 210, 810),
    ('callout2.mov', T('选区外面的数据'), 210, 810),
    ('callout3.mov', T('新表建好了') - 0.3, 210, 810),
    ('callout4.mov', T('我什么都没输入'), 210, 810),
    ('callout5.mov', T('第二次点应用'), 210, 810),
    ('callout6.mov', T('还特意避免'), 210, 810),
    ('count27.mov', T('二十七组'), 200, 300),
    ('ai_switch.mov', SEG['d4'][0], 310, 140),
]
AI_Q = q({
    't1': T('Codex') - SEG['d4'][0], 't2': T('WorkBuddy') - SEG['d4'][0], 't3': T('豆包，') - SEG['d4'][0],
    't4': T('用的都是你') - SEG['d4'][0], 'tOut': SEG['d4'][1] - SEG['d4'][0] - 0.5,
})
COUNT_DUR = round(SEG['d3'][1] - T('二十七组'), 2)

if __name__ == '__main__':
    print('画面段：', SEG)
    for k, v in SCENES.items(): print(k, v)
    print('ai', AI_Q, 'count_dur', COUNT_DUR)
