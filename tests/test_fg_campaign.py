"""Synthetic Fantasy Grounds NPCs, items, spells and story. File-level only."""
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from PIL import Image

from forgebridge.fantasy_grounds import main
from forgebridge.fg_campaign import build_campaign
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
    </id-00001>
    <id-00002>
      <name type="string">Blank</name>
      <token type="token">../secret.png</token>
    </id-00002>
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


def module(root):
    path = Path(root) / 'campaign.mod'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('definition.xml', DEFINITION)
        archive.writestr('db.xml', DB.encode())
        archive.writestr('tokens/goblin.png', png())
        archive.writestr('images/room.png', png())
    return path


class FantasyGroundsCampaignTests(unittest.TestCase):
    def test_npcs_items_spells_and_story_become_native_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            files, report = build_campaign(module(tmp))
        self.assertEqual(report['evidence'], 'file-level only, Toolkit check pending')
        self.assertEqual(report['runtime_validation'], 'not performed')
        self.assertEqual(report['counts']['actors'], 2)
        self.assertEqual(report['counts']['items'], 1)
        self.assertEqual(report['counts']['spells'], 1)
        self.assertEqual(report['counts']['stories'], 1)
        notes = {row['name']: row for row in report['documents']}
        self.assertEqual(set(notes), {'Goblin', 'Blank', 'Potion of Healing', 'Magic Missile', 'Room 1'})
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
        self.assertTrue(any(name.endswith('goblin.png.rwfile') or 'ForgeBridgeCampaign-' in name for name in files))
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
        story = node(files[notes['Room 1']['target'][:-7] + '.rwnote'])
        story_text = find(story, 'ArkenNoteFieldText')[0].members['_text']
        self.assertIn('Read aloud.', content(story_text))
        self.assertTrue(any(char.members['_link'] == report['links']['npc.id-00001']
                            for char in story_text.members['_characters'].members['_items'].items))
        self.assertTrue(find(story, 'ArkenNoteFieldMedia'))
        joined = json.dumps(report['losses'])
        self.assertIn('Fireball', joined)
        self.assertIn('no dnd5e spell-pack', joined)
        self.assertIn('strength score is not stored', joined)
        self.assertIn('Bonus action', joined)
        self.assertIn('Empty', joined)
        self.assertIn('npc.missing', joined)
        self.assertIn('../secret.png', joined)
        self.assertNotIn('writeFileSync', joined)
        self.assertFalse(any('../' in name or name.startswith('/') for name in files))
        root = Path(__file__).resolve().parents[1] / 'fixtures' / 'arkenforge-5e-templates'
        for name in ('5e-Character.rwnote', '5e-Item.rwnote', '5e-Spell.rwnote'):
            self.assertTrue((root / name).is_file(), name)
        with tempfile.TemporaryDirectory() as tmp:
            mod = module(tmp)
            out = Path(tmp) / 'notes'
            self.assertEqual(main([str(mod), '--campaign-out', str(out)]), 0)
            self.assertTrue((out / 'fg-campaign-report.json').is_file())
            self.assertTrue(any(path.name.endswith('.rwnote') for path in out.rglob('*.rwnote')))


if __name__ == '__main__':
    unittest.main()
