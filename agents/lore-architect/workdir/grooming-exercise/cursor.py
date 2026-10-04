#!/usr/bin/env python3
"""cursor.py <workset.yaml> [extra files...] : mark editable files of a workset (plus extras) reviewed, bump last_successful_*"""
import re,sys,datetime,subprocess,os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))
ws=open(sys.argv[1]).read()
ed=ws.split("\n  editable:")[1].split("\n  halo:")[0]
files=set(re.findall(r'file: "([^"]+)"',ed))|set(sys.argv[2:])
st=open("workdir/lore-grooming-state.yaml").read()
old=dict((m[0],m[1]) for m in re.findall(r'file: ([^,]+), at: "([^"]+)"',st))
now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for f in files: old[f]=now
c=subprocess.run(["git","rev-parse","--short","HEAD"],capture_output=True,text=True).stdout.strip()
out=f'lore_grooming: 1\nlast_successful_at: "{now}"\nlast_successful_commit: {c}\nreviewed:\n'+"".join(f'  - {{file: {f}, at: "{old[f]}"}}\n' for f in sorted(old))
open("workdir/lore-grooming-state.yaml","w").write(out); print(len(files),"marked")
