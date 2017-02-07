# -*- coding: utf-8 -*-
__author__ = 'Administrator'

from proto import *
import proto
pb2s = []
tmp = dir(proto)
for p in tmp:
    if p.endswith("pb2"):
        pb2s.append(getattr(proto,p))

print pb2s

for pb2 in pb2s:
    tmp = dir(pb2)

    for c in tmp:
        cls = getattr(pb2,c)
        if c.endswith("Req") or c.endswith("Resp") or c.endswith("Event"):
                if hasattr(cls,"DEF") and hasattr(cls,"ID"):
                    MessageMapping._mapping[cls.ID] = MessageDef(None,cls)
