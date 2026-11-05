"""File-level regressions for the 2026-11-05 Toolkit display findings."""
import tempfile
import unittest

from forgebridge.campaign_dnd5e import text, actor_ir, item_ir
from forgebridge.fg_campaign import build_campaign
from forgebridge.native_campaign import campaign_files
from forgebridge.native_export import TextCompiler
from test_campaign import actor, campaign, document, node, find, content
from test_fg_campaign import module


class DisplayFixTests(unittest.TestCase):
    def test_foundry_enrichers_are_inert_labels_and_uuid_is_preserved(self):
        examples = {
            '&Reference[poisoned apply=false]': 'poisoned',
            '&Reference[poisoned apply=false]{Poisoned condition}': 'Poisoned condition',
            '&Reference[condition=poisoned apply=false]': 'poisoned',
            '@Check[ability=str dc=10]{Strength check}': 'Strength check',
            '@Check[ability=str dc=10]': 'str',
            '@Damage[2d6[fire]]': '2d6[fire]',
            '@Item[abc]{Potion}': 'Potion',
            '@Actor[abc]{Guard}': 'Guard',
            '@Embed[JournalEntry.a caption=false]{Handout}': 'Handout',
            '@Unknown[thing enabled=true]': 'thing',
            '@UUID[Item.spell]{Bless}': '@UUID[Item.spell]{Bless}',
            '@Broken[unfinished': '@Broken[unfinished',
            '<script>doBadThings()</script>&Reference[poisoned apply=false]': 'poisoned',
        }
        for source, expected in examples.items():
            with self.subTest(source=source): self.assertEqual(text(source), expected)
        self.assertEqual(text('[[/r 1d20]]{Roll}'), 'Roll')

    def test_journal_text_strips_references_without_losing_uuid_links(self):
        compiler = TextCompiler(lambda uuid: 'MyAssets/Spell.rwmeta', [], {})
        parts = compiler.compile('<p>&Reference[poisoned apply=false] @UUID[Item.s]{Spell}</p>')
        self.assertEqual(''.join(value for value, link in parts), 'poisoned Spell')
        self.assertIn(('Spell','MyAssets/Spell.rwmeta'), parts)

    def test_foundry_empty_stat_lines_and_unknown_proficiency_are_omitted(self):
        source=actor(); source['system']['skills']={}; source['system']['traits']['languages']={}
        source['system']['attributes']['senses']={}; source['system']['details'].pop('cr')
        with tempfile.TemporaryDirectory() as tmp:
            files, report=campaign_files(campaign([document('Actor',source)]),tmp,notes_folder='Test')
        block=find(node(files[next(p for p in files if p.endswith('.rwnote'))]),'ArkenNoteFieldStatBlock5e')[0]
        for field in ('_skillsText','_sensesText','_languagesText','_proficiencyBonusText'):
            self.assertEqual(content(block.members[field]),'')
        self.assertFalse(block.members['_savingThrowsFieldActive'])
        self.assertTrue(block.members['_damageImmunitiesFieldActive'])
        self.assertEqual(set(block.members),set(block.schema['names']))
        source['system']['details']['cr']=9
        self.assertEqual(actor_ir(source)['proficiency'],'+4')

    def test_fg_empty_stat_lines_and_missing_proficiency_are_omitted(self):
        db='<root><npc><id-1><name>Empty Guard</name></id-1></npc></root>'
        with tempfile.TemporaryDirectory() as tmp: files, report=build_campaign(module(tmp,db=db))
        target=report['documents'][0]['target'][:-7]+'.rwnote'
        block=find(node(files[target]),'ArkenNoteFieldStatBlock5e')[0].members
        for field in ('_skillsText','_sensesText','_languagesText','_proficiencyBonusText'):
            self.assertEqual(content(block[field]),'')
        self.assertFalse(block['_savingThrowsFieldActive'])
        self.assertFalse(block['_damageResistanceFieldActive'])

    def test_parchment_links_keep_targets_and_use_dark_colour(self):
        source=actor(); source['system']['details']['biography']={'value':'@UUID[Item.s]{Spell}'}
        source['items'][0]['system']['description']['value']='@UUID[Item.s]{Spell}'
        docs=[document('Actor',source),document('Item',{'_id':'i','name':'Scroll','type':'consumable','system':{'description':{'value':'@UUID[Item.s]{Spell}'}}}),
              document('Item',{'_id':'s','name':'Spell','type':'spell','system':{'level':0,'school':'evo','description':{'value':'@UUID[Actor.actor]{Guard}'}}})]
        with tempfile.TemporaryDirectory() as tmp: files, report=campaign_files(campaign(docs),tmp,notes_folder='Test')
        links=[]
        for data in (v for k,v in files.items() if k.endswith('.rwnote')):
            root=node(data)
            for kind in ('ArkenNoteFieldStatBlock5e','ArkenNoteField5eItemBlock','ArkenNoteField5eSpellBlock'):
                for block in find(root,kind):
                    for value in find(block,'ArkenTextString'):
                        chars=value.members['_characters'].members['_items'].items
                        links.extend(c for c in chars if c.members['_link'])
        self.assertTrue(links)
        self.assertTrue(all(c.members['_hexColour']=='58180D' for c in links))
        self.assertTrue(all(c.members['_fontSettings'].members['value__'] & 1024 for c in links))
        self.assertEqual({c.members['_link'] for c in links},{report['links']['Item.s'],report['links']['Actor.actor']})

    def test_foundry_and_fg_cantrips_use_school_then_cantrip(self):
        self.assertEqual(item_ir({'type':'spell','system':{'level':0,'school':'evo'}})['type'],'Evocation cantrip')
        self.assertEqual(item_ir({'type':'spell','system':{'level':0}})['type'],'Cantrip')
        db='<root><item><id-1><name>Light</name><type>spell</type><level>0</level><school>evocation</school><description>A light.</description></id-1></item></root>'
        with tempfile.TemporaryDirectory() as tmp: files, report=build_campaign(module(tmp,db=db))
        target=report['documents'][0]['target'][:-7]+'.rwnote'
        block=find(node(files[target]),'ArkenNoteField5eSpellBlock')[0]
        self.assertEqual(content(block.members['_typeText']),'Evocation cantrip')
