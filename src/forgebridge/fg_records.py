"""Additional FG record adapters: tables, manual navigation, parcels and quests.

Only source data is read. Rolls, rewards, scripts and cross-module loads are never
executed. Unsupported record types and range/behavior mismatches remain losses.
"""
import re
from forgebridge.fantasy_grounds import ModuleError

RECORD_GROUPS = {
    'table': ('tables','table','reference.tabledata'),
    'parcel': ('treasureparcel','treasureparcels','parcel','parcels'),
    'quest': ('quest','quests'),
}
REFERENCE_NAVIGATION_GROUPS = {'equipmentlists','magicrefitemlists','magicitemlists','npclists'}
REFERENCE_GROUPS = {'npcdata','equipmentdata','magicrefitemdata','magicitemdata',
                    'spelldata','refmanualdata','refmanualindex','tabledata'}


def extra_documents(root, module, seen, losses, image_for_record=None):
    from forgebridge.fg_campaign import _field, _formatted, _child_number
    docs=[]
    def loss(grade,feature,summary,identity,**details):
        losses.append(dict(grade=grade,feature=feature,summary=summary,source_id=identity,**details))
    def document(identity, name, body='', *, kind='Story', form='fg-story', payload=None):
        if identity in seen:
            loss('unsupported','duplicate-record','Duplicate FG address not converted twice',identity)
            return
        seen.add(identity)
        docs.append(dict(kind=kind,format=form,id=identity,source_path='db.xml',adventure_id=module,
            uuid_aliases=[identity,identity+'@'+module,identity+'@*'],display={},
            payload=payload or dict(name=name,text=body)))
    def records(node,prefix):
        for child in node:
            if child.tag=='category': yield from records(child,prefix)
            elif child.tag not in ('categoryname','label','index'): yield prefix+'.'+child.tag,child
    def link(ref,label):
        return '@UUID['+ref+']{'+label+'}' if ref else label
    def plain_tree(node,depth=0):
        if depth>32: raise ModuleError('FG text tree exceeds 32 levels')
        if node.get('type')=='windowreference':
            return link(node.findtext('recordname'),_field(node,'name') or node.findtext('recordname') or '')
        if node.get('type')=='formattedtext': return _formatted(node) or ''
        if not list(node): return _formatted(node) or ''
        return '\n'.join(child.tag+': '+plain_tree(child,depth+1) for child in node)
    for form,paths in RECORD_GROUPS.items():
        for path in paths:
            parent=root.find(path.replace('.','/'))
            if parent is None: continue
            for identity,record in records(parent,path):
                name=_field(record,'name') or identity
                if form!='table':
                    body='\n'.join(child.tag+': '+plain_tree(child) for child in record if child.tag!='name')
                    document(identity,name,form='fg-'+form,payload=dict(name=name,text=body or 'No source detail stored.',image=image_for_record(record,identity) if image_for_record else None))
                    loss('approximate',form,'Source reward/items/coins/status retained as text and links; no reward or inventory automation',identity)
                    continue
                unknown=[c.tag for c in record if c.tag not in {'name','locked','description','notes','output','hiderollresults','mod','dice','resultscols','tablerows'} and not re.fullmatch(r'labelcol[0-9]+',c.tag)]
                if unknown: loss('manual','table-fields','Unmapped table fields',identity,fields=unknown)
                rows=[]
                table_rows=record.find('tablerows')
                if table_rows is None:
                    loss('manual','table','Table has no stored ranges; retained as a text note',identity)
                    document(identity,name,plain_tree(record),form='fg-table-reference')
                    continue
                if len(table_rows)>256: loss('manual','table','More than 256 rows: native range writer will retain a reference instead',identity)
                for row in table_rows:
                    values=[];results=row.find('results')
                    if results is not None:
                        for col,value in enumerate(results,1):
                            label=_field(record,'labelcol'+str(col))
                            value_text=_field(value,'result') or ''
                            ref=value.findtext('resultlink/recordname') or value.findtext('link/recordname')
                            value_text=link(ref,value_text or ref or '')
                            values.append(((label+': ') if label else '')+value_text)
                            unknown=[c.tag for c in value if c.tag not in ('result','resultlink','link')]
                            if unknown: loss('manual','table-result','Unmapped result fields',identity,fields=unknown,row=row.tag,column=col)
                    if not values: loss('manual','table-result','Row has no stored results',identity,row=row.tag)
                    rows.append(dict(fg_range=[row.findtext('fromrange'),row.findtext('torange')],range=[_child_number(row,'fromrange'),_child_number(row,'torange')],
                                     name='',description='\n'.join(values),weight=1))
                    unknown=[c.tag for c in row if c.tag not in ('fromrange','torange','results')]
                    if unknown: loss('manual','table-row','Unmapped table row fields',identity,fields=unknown,row=row.tag)
                dice=record.findtext('dice') or ''
                formula='1'+dice if re.fullmatch(r'd[1-9][0-9]*',dice) else dice if re.fullmatch(r'[1-9][0-9]*d[1-9][0-9]*(?:[+-][0-9]+)?',dice) else 'FG dice: '+dice
                mod=_child_number(record,'mod')
                if mod:
                    match=re.fullmatch(r'(\d+d\d+)([+-]\d+)?',formula)
                    if type(mod) is int and match:
                        offset=int(match[2] or 0)+mod;formula=match[1]+(f'{offset:+d}' if offset else '')
                    else:
                        loss('manual','table-formula','Unsupported FG modifier; reference-only formula retained',identity,modifier=mod)
                        formula='Unsupported FG modifier: '+str(mod)+'; '+formula
                payload=dict(name=name,results=rows,formula=formula,replacement=True,
                    fg_settings={c.tag:plain_tree(c) for c in record if c.tag!='tablerows'})
                document(identity,name,kind='RollTable',form='fg-table',payload=payload)
                loss('approximate','table-settings','Range rows and column text/links retained; supported dice/modifiers mapped separately; output, hidden rolls, chained tables and replacement behavior require review; source settings retained',identity,settings=payload['fg_settings'])
    # FG manual chapters are database records; leaf listlinks address page records.
    index=root.find('reference/refmanualindex')
    if index is not None:
        def navigation(node,identity,depth=0):
            if depth>32: raise ModuleError('FG reference manual nesting exceeds 32 levels')
            ref=node.findtext('listlink/recordname') or node.findtext('link/recordname')
            name=_field(node,'name')
            if ref: return [(ref,name or ref)]
            children=[]
            for child in node:
                if child.tag not in ('name','keywords','group','subgroup','text','description'):
                    children.extend(navigation(child,identity+'.'+child.tag,depth+1))
            body=_field(node,'text','description') or ''
            if name or node is index:
                title=name or module+' — Reference Manual'
                content='\n'.join(([body] if body else [])+[link(ref,label) for ref,label in children])
                document(identity,title,content or 'No source page links stored.',form='fg-reference-chapter')
                return [(identity,title)]
            return children
        navigation(index,'reference.refmanualindex')
    handled={'npc','item','spell','story','encounter','image','reference'}|{p for paths in RECORD_GROUPS.values() for p in paths if '.' not in p}
    for group in root:
        if group.tag in handled: continue
        if group.tag in ('library','list','lists'):
            loss('approximate','navigation','Source library/list navigation is replaced by converted note links; custom list behavior not converted',group.tag)
            continue
        for identity,record in records(group,group.tag):
            loss('unsupported','unknown-record-type','Unknown FG record type; not converted or executed',identity,record_type=group.tag)
        if not list(group):loss('unsupported','unknown-record-type','Unknown FG section',group.tag,record_type=group.tag)
    reference=root.find('reference')
    if reference is not None:
        for group in reference:
            if group.tag in REFERENCE_GROUPS: continue
            if group.tag in REFERENCE_NAVIGATION_GROUPS:
                loss('approximate','navigation','Reference list navigation is not reproduced; converted note links retained','reference.'+group.tag)
                continue
            for identity,record in records(group,'reference.'+group.tag):
                loss('unsupported','unknown-record-type','Unknown FG reference record type; not converted',identity,record_type=group.tag)
    return docs
