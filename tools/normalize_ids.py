#-*-coding:utf-8-*-
"""把 xmltv 里的 <channel id="1"> 改成 <channel id="CCTV1">，
   与播放器 m3u 中的 tvg-id 对齐，否则节目单匹配不上频道。"""
import re, sys, pathlib

def normalize(path):
    s = pathlib.Path(path).read_text(encoding='utf-8')
    pairs = re.findall(r'<channel id="([^"]+)"(.*?)</channel>', s, re.S)
    mapping = {}
    for cid, body in pairs:
        dn = re.search(r'<display-name[^>]*>([^<]*)', body)
        if dn and dn.group(1).strip():
            mapping[cid] = dn.group(1).strip()
    if not mapping:
        return 0
    # 只替换 channel 定义和 programme 的 channel 属性，避免误伤
    def fix_channel(m):
        cid = m.group(1)
        return '<channel id="%s"' % mapping.get(cid, cid)
    s = re.sub(r'<channel id="([^"]+)"', fix_channel, s)
    def fix_prog(m):
        cid = m.group(1)
        return 'channel="%s"' % mapping.get(cid, cid)
    s = re.sub(r'channel="([^"]+)"', fix_prog, s)
    pathlib.Path(path).write_text(s, encoding='utf-8')
    return len(mapping)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        n = normalize(p)
        print('%s：已对齐 %d 个频道 id' % (p, n))
