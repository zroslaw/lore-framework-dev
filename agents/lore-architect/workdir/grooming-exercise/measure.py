#!/usr/bin/env python3
"""Grooming metrics snapshot: python3 measure.py <label> -> appends JSON line to metrics.jsonl"""
import json, re, subprocess, sys, os, datetime
A=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
R="/Users/yaroslav/.claude/plugins/cache/lore-framework/lr/1.47.0/scripts/lr-core"
def mp(view): return subprocess.run(["python3",R,"lore-map","--agent-dir",A,"--view",view,"--engine","claude"],capture_output=True,text=True).stdout
b=mp("boot"); d=mp("detailed")
def g(pat,s,default=None):
    m=re.search(pat,s,re.S); return m.group(1) if m else default
cov=g(r"\ncoverage:(.*?)\nroot:|\ncoverage:(.*?)\n[a-z_]+:",b) or ""
ft=re.search(r"files:\s+total: (\d+)\s+mapped: (\d+)\s+uncovered: (\d+)\s+mapped_percent: ([\d.]+)",b)
et=re.search(r"estimated_tokens:\s+total: (\d+)\s+mapped: (\d+)\s+uncovered: (\d+)\s+mapped_percent: ([\d.]+)",b)
st=lambda k: int(g(rf"{k}: (\d+)",b,0))
recs=re.findall(r'\n\s+- file: "([^"]+)"\n(?:(?!\n\s+- file:).)*?estimated_tokens: (\d+)',d,re.S)
sizes={}
for f,t in re.findall(r'file: "([^"]+)"\s+title:.*?estimated_tokens: (\d+)',d,re.S): sizes[f]=int(t)
types=re.findall(r'\n\s+type: "(\w+)"',d)
val=d.split("\nvalidation:")[-1].split("\ngit_history_error")[0].strip()
m=dict(label=sys.argv[1],at=datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%SZ"),
 files_total=int(ft[1]),files_mapped=int(ft[2]),files_uncovered_legacy=int(ft[3]),files_mapped_pct=float(ft[4]),
 tokens_total=int(et[1]),tokens_mapped=int(et[2]),tokens_uncovered=int(et[3]),tokens_mapped_pct=float(et[4]),
 lore_context_tokens=st("lore_context_estimated_tokens"),boot_footprint_tokens=st("boot_footprint_estimated_tokens"),
 boot_map_tokens=int(g(r"\nestimated_tokens: (\d+)",b,0)),
 area_hubs=types.count("area"),topics_v1=types.count("topic"),
 mapped_over_5k=sum(1 for v in sizes.values() if v>5000),
 mapped_avg_tokens=round(sum(sizes.values())/max(1,len(sizes))),
 root_children=int(g(r"child_count: (\d+)",d,0)),
 validation_issues=0 if val in("[]","") else val.count("\n  - ")+1)
open(os.path.join(os.path.dirname(__file__),"metrics.jsonl"),"a").write(json.dumps(m)+"\n")
print(json.dumps(m,indent=1))
