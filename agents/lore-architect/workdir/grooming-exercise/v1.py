#!/usr/bin/env python3
"""v1.py file summary [parent] [H1 title] : prepend v1 frontmatter (+H1 if given)"""
import sys
f,summary=sys.argv[1],sys.argv[2]
parent=sys.argv[3] if len(sys.argv)>3 else "lore-context.md"
title=sys.argv[4] if len(sys.argv)>4 else None
assert len(summary)<=240,(len(summary),f)
s=open(f).read(); assert not s.startswith("---")
q=summary.replace('"','\\"')
fm=f'---\nlore: 1\ntype: topic\nsummary: "{q}"\nparent: {parent}\n---\n\n'
if title: fm+=f'# {title}\n\n'
open(f,'w').write(fm+s)
