"""Split an llms-full.txt doc export into one Markdown file per page.

Usage: python3 -I split-llms-full.py <llms-full.txt> <output-dir>
Pages in the OpenAI exports (learn.chatgpt.com/docs/llms-full.txt,
developers.openai.com/plugins/llms-full.txt) are separated by a "---" line
followed by a "# Title" line. Output files are NNN-<slug>.md; grep them.
"""
import sys, re, os
src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
lines = open(src, encoding='utf-8').read().split('\n')
pages = []; cur_title=None; cur=[]
i=0
while i < len(lines):
    l = lines[i]
    if l == '---':
        # look ahead for title
        j=i+1
        while j < len(lines) and lines[j].strip()=='' : j+=1
        if j < len(lines) and lines[j].startswith('# '):
            if cur_title: pages.append((cur_title, cur))
            cur_title = lines[j][2:].strip(); cur=[lines[j]]; i=j+1; continue
    cur.append(l); i+=1
if cur_title: pages.append((cur_title, cur))
for n,(t,c) in enumerate(pages):
    slug = re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')[:60]
    fn = f"{n:03d}-{slug}.md"
    open(os.path.join(outdir, fn),'w',encoding='utf-8').write('\n'.join(c))
    print(fn, len('\n'.join(c)))
