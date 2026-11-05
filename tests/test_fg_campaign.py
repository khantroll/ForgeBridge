"""Synthetic Fantasy Grounds NPCs, items, spells and story.

Validation note: these tests are file-level only. They prove notes, links and
images were written with the expected native shapes. They are never proof that
the Arkenforge Toolkit lists or renders them. Toolkit check pending.
"""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image

from forgebridge.fantasy_grounds import main
from forgebridge.fg_campaign import build_campaign, write_campaign
from forgebridge.native_dependencies import read_package
from test_campaign import content, find, node


def png():
    out = io.BytesIO()
    Image.new('RGB', (8, 8), (20, 80, 20)).save(out, 'PNG')
    return out.getvalue()


DEFINITION = b'''<?xml version="1.0"?><root version="4.1">
<name>FBCampaign</name><displayname>FG Campaign</displayname><author>synthetic</author><ruleset>5E</ruleset>
</root>'''

DB = '''<?xml version="1.0" encoding="utf-8"?>
<root version="4.1">
  <npc>
    <id-00001>
      <name type="string">Goblin</name>
      <size type="string">Small</size>
      <type type="string">humanoid (goblinoid)</type>
      <alignment type="string">neutral evil</alignment>
      <ac type="number">15</ac>
      <actext type="string">15 (leather armor, shield)</actext>
      <hp type="number">7</hp>
      <hd type="string">2d6</hd>
      <speed type="string">climb 20 ft., 30 ft.</speed>
      <abilities>
        <dexterity><score type="number">14</score></dexterity>
        <constitution><score type="number">10</score></constitution>
      </abilities>
      <savingthrows><dexterity><prof type="number">1</prof></dexterity></savingthrows>
      <skills><stealth><prof type="number">1</prof></stealth></skills>
      <senses type="string">darkvision 60 ft.</senses>
      <languages type="string">Common, Goblin, common</languages>
      <cr type="string">1/4</cr>
      <token type="token">tokens/goblin.png</token>
      <traits>
        <id-00001><name type="string">Nimble Escape</name><desc type="string">Disengage or Hide as a bonus action.</desc></id-00001>
      </traits>
      <actions>
        <id-00001>
          <name type="string">Scimitar</name>
          <attackstat type="string">dexterity</attackstat>
          <desc type="formattedtext"><p><i>Melee Weapon Attack:</i> +9 to hit. <i>Hit:</i> 5 slashing. A rider grants +7 to hit.</p></desc>
        </id-00001>
      </actions>
      <bonusactions>
        <id-00002><name type="string">Nimble</name><desc type="string">Disengage.</desc></id-00002>
      </bonusactions>
      <reactions>
        <id-00003><name type="string">Redirect</name><desc type="string">See <link recordname="encounter.id-00001">the room</link>.</desc></id-00003>
      </reactions>
      <legendaryactions>
        <id-00004><name type="string">Move</name><desc type="string">The goblin moves up to its speed.</desc></id-00004>
      </legendaryactions>
    </id-00001>
    <id-00002>
      <name type="string">Blank</name>
      <token type="token">../secret.png</token>
    </id-00002>
    <id-00003>
      <name type="string">Mixed Speed</name>
      <speed type="string">30 ft., swim 10 m</speed>
    </id-00003>
  </npc>
  <item>
    <id-00001>
      <name type="string">Potion of Healing</name>
      <type type="string">Potion</type>
      <rarity type="string">common</rarity>
      <description type="formattedtext"><p>Regain 2d4+2 hit points. Brewed by <link recordname="npc.id-00001">Goblin</link>.</p></description>
    </id-00001>
    <id-00002>
      <name type="string">Magic Missile</name>
      <type type="string">spell</type>
      <level type="number">1</level>
      <school type="string">evocation</school>
      <castingtime type="string">1 action</castingtime>
      <range type="string">120 feet</range>
      <components type="string">V, S</components>
      <duration type="string">Instantaneous</duration>
      <description type="formattedtext"><p>You create three glowing darts of magical force.</p></description>
    </id-00002>
    <id-00003>
      <name type="string">Fireball</name>
      <type type="string">spell</type>
      <description type="formattedtext"><p><link recordname="spell.fireball@DD5E">Fireball</link></p></description>
    </id-00003>
    <id-00004>
      <name type="string">Cantrip Glow</name>
      <type type="string">spell</type>
      <school type="string">evocation</school>
      <castingtime type="string">1 action</castingtime>
      <range type="string">Touch</range>
      <components type="string">V, S</components>
      <duration type="string">1 minute</duration>
      <description type="formattedtext"><p>Your hand sheds bright light.</p></description>
    </id-00004>
  </item>
  <encounter>
    <id-00001>
      <name type="string">Room 1</name>
      <text type="formattedtext"><p>Read aloud. <link recordname="npc.id-00001">Goblin</link> waits. Also <link recordname="npc.missing">nobody</link>.</p></text>
      <image type="image"><bitmap>images/room.png</bitmap></image>
    </id-00001>
    <id-00002>
      <name type="string">Empty</name>
    </id-00002>
  </encounter>
</root>'''


def module(root, db=DB, extra_members=None):
    path = Path(root) / 'campaign.mod'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('definition.xml', DEFINITION)
        archive.writestr('db.xml', db.encode())
        archive.writestr('tokens/goblin.png', png())
        archive.writestr('images/room.png', png())
        for name, data in (extra_members or {}).items():
            archive.writestr(name, data)
    return path


class FantasyGroundsCampaignTests(unittest.TestCase):
    def test_evidence_is_file_level_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = build_campaign(module(tmp))
        self.assertEqual(report['evidence'], 'file-level only, Toolkit check pending')
        self.assertEqual(report['runtime_validation'], 'not performed')
        self.assertTrue(files)
        self.assertFalse(any('../' in name or name.startswith('/') for name in files))

    def test_npc_stat_block_actions_and_legendary(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = build_campaign(module(tmp))
        notes = {row['name']: row for row in report['documents']}
        self.assertIn('Goblin', notes)
        goblin = node(files[notes['Goblin']['target'][:-7] + '.rwnote'])
        block = find(goblin, 'ArkenNoteFieldStatBlock5e')[0].members
        self.assertEqual(content(block['_nameText']), 'Goblin')
        self.assertEqual(content(block['_typeText']), 'Small humanoid (goblinoid), neutral evil')
        self.assertEqual(content(block['_armorClassText']), 'Armor Class 15 (leather armor, shield)')
        self.assertEqual(content(block['_hitPointsText']), '(2d6)')
        self.assertEqual(content(block['_speedText']), 'Speed 30 ft, climb 20 ft')
        self.assertEqual(content(block['_dexValNew']), '14 (+2)')
        self.assertEqual(content(block['_strValNew']), 'Unknown')
        self.assertIn('DEX +4', content(block['_savingThrowsText']))
        self.assertIn('Stealth +4', content(block['_skillsText']))
        self.assertEqual(content(block['_languagesText']), 'Languages Common, Goblin')
        self.assertEqual(content(block['_sensesText']), 'Senses darkvision 60 ft.')
        self.assertEqual(content(block['_challengeText']), 'Challenge 1/4')
        self.assertEqual(content(block['_proficiencyBonusText']), 'Proficiency Bonus +2')
        actions = [content(item) for item in block['_actions'].members['_items'].items]
        self.assertTrue(any('+4 to hit' in item and '+7 to hit' in item for item in actions))
        self.assertTrue(any(item.startswith('Nimble. ') for item in actions))
        self.assertTrue(any('Nimble Escape' in content(item) for item in block['_abilities'].members['_items'].items))
        reactions = content(block['_reactions'].members['_items'].items[0])
        self.assertIn('the room', reactions)
        room_link = report['links']['encounter.id-00001']
        chars = block['_reactions'].members['_items'].items[0].members['_characters'].members['_items'].items
        self.assertTrue(any(char.members['_link'] == room_link for char in chars))
        legendary = [content(item) for item in block['_legendaryActions'].members['_items'].items]
        self.assertTrue(any(item.startswith('Move. ') and 'moves up to its speed' in item for item in legendary))
        self.assertTrue(any(name.endswith('goblin.png.rwfile') or 'ForgeBridgeCampaign-' in name for name in files))
        joined = json.dumps(report['losses'])
        self.assertIn('strength score is not stored', joined)
        self.assertIn('Bonus action', joined)

    def test_mixed_speed_units_keep_source_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = build_campaign(module(tmp))
        notes = {row['name']: row for row in report['documents']}
        mixed = node(files[notes['Mixed Speed']['target'][:-7] + '.rwnote'])
        block = find(mixed, 'ArkenNoteFieldStatBlock5e')[0].members
        self.assertEqual(content(block['_speedText']), 'Speed 30 ft., swim 10 m')
        self.assertIn('Speed mixes units', json.dumps(report['losses']))

    def test_items_spells_and_spell_without_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = build_campaign(module(tmp))
        self.assertEqual(report['counts']['items'], 1)
        self.assertEqual(report['counts']['spells'], 2)
        notes = {row['name']: row for row in report['documents']}
        potion = node(files[notes['Potion of Healing']['target'][:-7] + '.rwnote'])
        item_block = find(potion, 'ArkenNoteField5eItemBlock')[0].members
        self.assertIn('Goblin', content(item_block['_descriptionText']))
        self.assertTrue(any(char.members['_link'] == report['links']['npc.id-00001']
                            for char in item_block['_descriptionText'].members['_characters'].members['_items'].items))
        spell = node(files[notes['Magic Missile']['target'][:-7] + '.rwnote'])
        spell_block = find(spell, 'ArkenNoteField5eSpellBlock')[0].members
        self.assertIn('evocation', content(spell_block['_typeText']))
        self.assertIn('three glowing darts', content(spell_block['_descriptionText']))
        self.assertEqual(content(spell_block['_castingTimeText']), 'Casting Time 1 action')
        glow = node(files[notes['Cantrip Glow']['target'][:-7] + '.rwnote'])
        glow_block = find(glow, 'ArkenNoteField5eSpellBlock')[0].members
        self.assertEqual(content(glow_block['_typeText']), 'evocation spell')
        self.assertIn('sheds bright light', content(glow_block['_descriptionText']))
        joined = json.dumps(report['losses'])
        self.assertIn('Fireball', joined)
        self.assertIn('no dnd5e spell-pack', joined)
        self.assertIn('Cantrip Glow', joined)
        self.assertIn('has no level', joined)

    def test_story_with_module_image_and_empty_story_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = build_campaign(module(tmp))
        self.assertEqual(report['counts']['stories'], 1)
        notes = {row['name']: row for row in report['documents']}
        story = node(files[notes['Room 1']['target'][:-7] + '.rwnote'])
        story_text = find(story, 'ArkenNoteFieldText')[0].members['_text']
        self.assertIn('Read aloud.', content(story_text))
        self.assertTrue(any(char.members['_link'] == report['links']['npc.id-00001']
                            for char in story_text.members['_characters'].members['_items'].items))
        self.assertTrue(find(story, 'ArkenNoteFieldMedia'))
        self.assertTrue(any('room.png' in name or 'ForgeBridgeCampaign-' in name for name in files))
        joined = json.dumps(report['losses'])
        self.assertIn('Empty', joined)
        self.assertIn('npc.missing', joined)
        self.assertIn('../secret.png', joined)

    def test_duplicate_records_are_skipped(self):
        # ElementTree keeps sibling elements that share a tag; campaign_ir skips
        # the second copy of the same category.id identity.
        same_tag = '''<?xml version="1.0" encoding="utf-8"?>
<root version="4.1">
  <npc>
    <id-00001><name type="string">First</name><hp type="number">1</hp></id-00001>
    <id-00001><name type="string">Second</name><hp type="number">2</hp></id-00001>
  </npc>
</root>'''
        with tempfile.TemporaryDirectory() as tmp:
            _files, report = build_campaign(module(tmp, db=same_tag))
        names = [row['name'] for row in report['documents']]
        self.assertEqual(names.count('First'), 1)
        self.assertNotIn('Second', names)
        self.assertIn('Duplicate NPC record skipped', json.dumps(report['losses']))

    def test_cli_writes_native_package_and_installs_add_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod = module(tmp)
            out = Path(tmp) / 'notes'
            self.assertEqual(main([str(mod), '--campaign-out', str(out)]), 0)
            self.assertTrue((out / 'fg-campaign-report.json').is_file())
            self.assertTrue((out / 'native-package.zip').is_file())
            self.assertTrue(any(path.name.endswith('.rwnote') for path in out.rglob('*.rwnote')))
            packaged = read_package(out / 'native-package.zip')
            self.assertTrue(any(name.startswith('MyAssets/') and name.endswith('.rwnote') for name in packaged))
            self.assertIn('fg-campaign-report.json', packaged)
            assets = Path(tmp) / 'MyAssets'; assets.mkdir()
            backups = Path(tmp) / 'Backups'; backups.mkdir()
            installed_out = Path(tmp) / 'notes-install'
            with patch('forgebridge.installer.require_toolkit_closed'):
                self.assertEqual(main([str(mod), '--campaign-out', str(installed_out),
                                       '--install', '--myassets', str(assets),
                                       '--backup-root', str(backups)]), 0)
            self.assertTrue(any(path.suffix == '.rwnote' for path in assets.rglob('*')))
            receipt = next(Path(backups).rglob('uninstall.json'))
            data = json.loads(receipt.read_text(encoding='utf-8'))
            self.assertEqual(data['state'], 'COMPLETE')
            self.assertGreater(len(data['added']), 0)
            report = json.loads((installed_out / 'fg-campaign-report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['evidence'], 'file-level only, Toolkit check pending')
            self.assertTrue(report.get('installed'))

    def test_templates_fixture_still_present(self):
        root = Path(__file__).resolve().parents[1] / 'fixtures' / 'arkenforge-5e-templates'
        for name in ('5e-Character.rwnote', '5e-Item.rwnote', '5e-Spell.rwnote'):
            self.assertTrue((root / name).is_file(), name)


if __name__ == '__main__':
    unittest.main()
