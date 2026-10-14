"""Validated editorial supplements; original bibliography stays immutable."""
import copy
import hashlib
from collections import Counter


def topic_title(articles):
    labels={'梦与幻觉':'梦与想象','自我与意识':'自我与意识','AGI与智能体':'智能体'}
    topics=[labels.get(c,c) for c,_ in Counter(a.get('category','') for a in articles).most_common(3) if c]
    return '、'.join(topics) or '神经科学与人工智能研究进展'


def apply_editorial(issue, supplement, source_bytes):
    out=copy.deepcopy(issue)
    if not supplement:
        if out.get('title')=='本周神经科学 × AI 精选':out['title']=topic_title(out['articles'])
        return out
    allowed={'version','id','source_sha256','editor','basis','edited_at','title','subtitle','topline','highlights','briefs','deepdives'}
    if set(supplement)-allowed:raise ValueError('Unknown editorial fields')
    if supplement.get('version')!=1 or supplement.get('id')!=issue['id']:raise ValueError('Invalid editorial issue')
    if supplement.get('source_sha256')!=hashlib.sha256(source_bytes).hexdigest():raise ValueError('Stale editorial source hash')
    if supplement.get('basis') not in {'abstracts','existing_briefs'}:raise ValueError('Missing editorial evidence basis')
    for key in ('title','subtitle','topline','editor','edited_at'):
        value=supplement.get(key)
        if not isinstance(value,str) or not value.strip() or len(value)>1200:raise ValueError(f'Invalid editorial {key}')
    papers={a['id']:a for a in out['articles']};seen=set()
    briefs=supplement.get('briefs',[])
    if not isinstance(briefs,list) or len(briefs)>len(papers):raise ValueError('Invalid editorial briefs')
    for brief in briefs:
        if not isinstance(brief,dict) or set(brief)-{'id','title_zh','summary','angle'}:raise ValueError('Editorial cannot edit bibliography')
        aid=brief.get('id')
        if aid not in papers or aid in seen:raise ValueError('Unknown or duplicate editorial paper')
        seen.add(aid)
        if ('summary' in brief or 'angle' in brief) and not papers[aid].get('abstract'):raise ValueError('New analysis requires source abstract')
        for key,value in brief.items():
            if key=='id':continue
            if not isinstance(value,str) or not value.strip() or len(value)>1200:raise ValueError('Invalid editorial brief')
            papers[aid][key]=value
        if 'summary' in brief:
            papers[aid]['ai_status']='generated'
            papers[aid]['evidence']='AI 根据公开摘要整理，未阅读全文。'
    for key,fields,limit in [('highlights',{'id','headline','summary'},3),('deepdives',{'id','headline','insight','experiment'},5)]:
        items=supplement.get(key,[])
        if not isinstance(items,list) or len(items)>limit:raise ValueError('Invalid editorial notes')
        ids=set()
        for item in items:
            if not isinstance(item,dict) or set(item)!=fields or item['id'] not in papers or item['id'] in ids:raise ValueError('Unknown or duplicate editorial note')
            ids.add(item['id'])
            if any(not isinstance(v,str) or not v.strip() or len(v)>1200 for v in item.values()):raise ValueError('Invalid editorial note text')
            if supplement['basis']=='abstracts' and not papers[item['id']].get('abstract'):raise ValueError('Editorial note requires source abstract')
        if key in supplement:out[key]=copy.deepcopy(items)
    for key in ('title','subtitle','topline'):out[key]=supplement[key]
    out['editorial']={k:supplement[k] for k in ('editor','basis','edited_at')}
    out['method_note']=('中文导读由 AI 根据公开摘要整理；研究思考和实验建议属于推测，未经验证。' if supplement['basis']=='abstracts' else '本期为人工精选试刊；中文标题与导读基于已有简报整理，部分条目尚待逐篇核实。')+' 预印本尚未经同行评议，请结合原文判断。'
    return out
