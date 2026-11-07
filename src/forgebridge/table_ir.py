"""Bounded probability tickets for native uniform range tables; never eval dice."""
from collections import Counter
import re
MAX_TICKETS=1000000

def ranges(source):
    rows=source.get('results',[])
    if not isinstance(rows,list) or not 1<=len(rows)<=256:raise ValueError('Table needs 1..256 source entries')
    formula=source.get('formula')
    match=re.fullmatch(r'\s*(\d*)[dD](\d+)\s*([+-]\s*\d+)?\s*',str(formula or ''))
    if not match:raise ValueError('Unsupported dice formula; only bounded NdS +/- integer supported')
    dice,sides=int(match[1] or 1),int(match[2]);offset=int(re.sub(r'\s+','',match[3] or '0'))
    if not 1<=dice<=8 or not 1<=sides<=1000000 or sides**dice>MAX_TICKETS or abs(offset)>1000000:raise ValueError('Dice formula exceeds native ticket/convolution limits')
    weights=[r.get('weight',1) for r in rows]
    if any(type(w) is not int or w<0 for w in weights) or not 0<sum(weights)<=MAX_TICKETS:raise ValueError('Weights must be nonnegative integers with bounded positive total')
    adjustments=[]
    # The standard normalized weighted form is 1d(sum(weights)). A stale range
    # list is not silently trusted: emit a visible approximation if normalized.
    if any(w!=1 for w in weights) and dice==1 and sides==sum(weights) and offset==0:
        counts=weights;cursor=1
        expected=[]
        for w in weights:expected.append([cursor,cursor+w-1]);cursor+=w
        if any(r.get('range')!=span for r,span in zip(rows,expected)):
            adjustments.append('Weights normalized into ticket ranges; source ranges differ. Source numeric ranges/formula retained for review; not claimed equivalent.')
    else:
        spans=[r.get('range') for r in rows]
        if any(not isinstance(s,list) or len(s)!=2 or any(type(v) is not int for v in s) or s[0]>s[1] for s in spans):raise ValueError('Invalid source ranges')
        if any(a[0]<=b[1] and b[0]<=a[1] for i,a in enumerate(spans) for b in spans[i+1:]):raise ValueError('Overlapping source ranges')
        if any(w!=1 for w in weights) and any(b-a+1!=w for (a,b),w in zip(spans,weights)):
            raise ValueError('Nonuniform dice and inconsistent weights/ranges are ambiguous; normalize source table explicitly')
        if dice==1:
            low,high=1+offset,sides+offset
            counts=[max(0,min(b,high)-max(a,low)+1) for a,b in spans]
            if sum(counts)!=sides:raise ValueError('Dice outcomes without exactly one source result')
        else:
            counts=None
        dist=Counter({0:1}) if counts is None else Counter()
        for _ in range(dice if counts is None else 0):
            next_dist=Counter()
            for total,n in dist.items():
                for face in range(1,sides+1):next_dist[total+face]+=n
            dist=next_dist
        if counts is None:counts=[0]*len(rows)
        for roll,n in dist.items():
            matches=[i for i,(a,b) in enumerate(spans) if a<=roll+offset<=b]
            if len(matches)!=1:raise ValueError('Dice outcomes without exactly one source result; reference-only rather than invented outcomes')
            counts[matches[0]]+=n
    result=[];cursor=1
    for i,count in enumerate(counts):
        if count:result.append((i,cursor,cursor+count-1));cursor+=count
        else:adjustments.append('Entry '+str(i)+' has zero probability and remains only in source/reference settings')
    if cursor-1>MAX_TICKETS:raise ValueError('Native ticket bound exceeded')
    return result,{'source_formula':formula,'tickets':cursor-1,'result_tickets':counts,'adjustments':adjustments,
        'numeric_roll_preserved':dice==1 and offset==0 and all(rows[i].get('range')==[a,b] for i,a,b in result)}
