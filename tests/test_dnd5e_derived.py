from copy import deepcopy
import unittest
from forgebridge.campaign_dnd5e import actor_ir
from forgebridge.dnd5e_derived import static_number, armor_class, attacks
from test_campaign import actor


class DerivedTests(unittest.TestCase):
    def test_natural_is_stored_flat_not_flat_plus_dex(self):
        a=actor();a['system']['attributes']['ac']={'calc':'natural','flat':10}
        a['system']['abilities']['dex']['value']=16
        self.assertEqual(actor_ir(a)['ac'],'10')
        a['system']['attributes']['ac']={'calc':'flat','flat':17,'bonus':4}
        self.assertEqual(actor_ir(a)['ac'],'17')

    def test_equipped_light_medium_heavy_and_shield(self):
        a=actor();a['system']['attributes']['ac']={'calc':'default','flat':99}
        a['system']['abilities']['dex']['value']=22
        gear={'_id':'armor','name':'Armor','type':'equipment','system':{'type':{'value':'light'},'equipped':True,'armor':{'value':12,'dex':None}}}
        a['items']=[gear];self.assertEqual(actor_ir(a)['ac'],'18')
        gear['system']['type']['value']='medium';gear['system']['armor']['value']=14
        self.assertEqual(actor_ir(a)['ac'],'16')
        gear['system']['type']['value']='heavy';gear['system']['armor']['value']=18
        self.assertEqual(actor_ir(a)['ac'],'18')
        a['items'].append({'name':'Shield','type':'equipment','system':{'type':{'value':'shield'},'equipped':True,'armor':{'value':2}}})
        self.assertEqual(actor_ir(a)['ac'],'20')
        gear['system']['equipped']=False
        self.assertEqual(actor_ir(a)['ac'],'18')  # unarmored 10 + DEX 6 + shield 2

    def test_explicit_mental_ability_is_honored_and_bonus_is_derived(self):
        a=actor();a['system']['abilities']['int']['value']=8;a['system']['abilities']['dex']['value']=16
        weapon=a['items'][0];weapon['system']['proficient']=1
        weapon['system']['activities']={'attack':{'type':'attack','attack':{'ability':'int','bonus':'','type':{'value':'melee','classification':'weapon'}}}}
        weapon['system']['description']['value']='Melee Weapon Attack: +99 to hit. Hit: 6 damage. Target gains +7 to hit.'
        ir=actor_ir(a)
        self.assertIn('+1 to hit',ir['actions']['actions'][0]['description'])
        self.assertIn('Target gains +7 to hit.',ir['actions']['actions'][0]['description'])
        self.assertEqual(ir['derived_values']['attacks'][0]['ability'],'int')
        weapon['system']['activities']['attack']['attack'].update(ability='dex',bonus='1')
        weapon['system']['magicalBonus']=2
        a['system']['bonuses']={'mwak':{'attack':'1'}}
        self.assertEqual(actor_ir(a)['derived_values']['attacks'][0]['total'],9)

    def test_flat_attack_and_unknown_formula_do_not_use_partial_bonus(self):
        a=actor();w=a['items'][0];w['system']['activities']={'hit':{'type':'attack','attack':{'ability':'dex','bonus':'7','flat':True}}}
        self.assertEqual(actor_ir(a)['derived_values']['attacks'][0]['total'],7)
        w['system']['activities']['hit']['attack'].update(flat=False,bonus='1d4')
        ir=actor_ir(a)
        self.assertIsNone(ir['derived_values']['attacks'][0]['total'])
        self.assertTrue(ir['approximations'])

    def test_language_deduplication_and_walk_first(self):
        a=actor();a['system']['traits']['languages']={'value':['common','elvish'],'custom':'Common; Elvish, Dwarvish'}
        a['system']['attributes']['movement']={'climb':30,'fly':60,'walk':30,'units':'ft'}
        ir=actor_ir(a)
        self.assertEqual(ir['languages'],'common, elvish, Dwarvish')
        self.assertEqual(ir['speed'],'30 ft, climb 30 ft, fly 60 ft')

    def test_safe_numeric_terms_never_execute_source_expressions(self):
        self.assertEqual(static_number('10 + @abilities.dex.mod',{'abilities.dex.mod':-1}),9)
        self.assertIsNone(static_number('__import__("os").system("x")'))
        self.assertIsNone(static_number('@prof2',{'prof':2}))
        self.assertIsNone(static_number('1d20'))

    def test_custom_simple_ac_and_unsupported_formula(self):
        a=actor();a['system']['attributes']['ac']={'calc':'custom','formula':'13 + @abilities.dex.mod'}
        self.assertEqual(actor_ir(a)['ac'],'14')
        a['system']['attributes']['ac']['formula']='1d20 + 10'
        self.assertIn('Unknown',actor_ir(a)['ac'])

    def test_finesse_default_and_legacy_attack_bonus(self):
        a=actor();a['system']['abilities']['dex']['value']=18
        w=a['items'][0];w['system'].update(actionType='mwak',properties=['fin'],proficient=1,attackBonus='1')
        ir=actor_ir(a)
        self.assertEqual(ir['derived_values']['attacks'][0]['total'],7)
