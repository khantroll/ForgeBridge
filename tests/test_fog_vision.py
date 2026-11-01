import unittest

from forgebridge.uvtt import _grade_scene_fields


def lines_for(scene):
    lines = []
    _grade_scene_fields({"_id": "s1", "name": "Crypt", **scene}, "bg.webp", lines)
    return lines


def fog_lines(scene):
    return [l for l in lines_for(scene) if l["code"] == "fog-vision"]


class FogVisionTests(unittest.TestCase):
    def test_no_vision_tells_gm_to_disable_toolkit_fog(self):
        (line,) = fog_lines({"tokenVision": False, "fog": {"exploration": False}})
        self.assertEqual(line["grade"], "manual")
        self.assertIn("tokenVision=false", line["summary"])
        self.assertIn("disable Arkenforge fog of war", line["summary"])

    def test_token_vision_with_exploration_explains_manual_reveal(self):
        (line,) = fog_lines({"tokenVision": True, "fog": {"exploration": True},
                             "environment": {"globalLight": {"enabled": False}}})
        self.assertIn("explored areas stayed revealed", line["summary"])
        self.assertIn("environment.globalLight.enabled=false", line["summary"])
        self.assertIn("not converted", line["summary"])

    def test_v10_flat_fields_are_read(self):
        (line,) = fog_lines({"tokenVision": True, "fogExploration": False, "globalLight": True})
        self.assertIn("fogExploration=false", line["summary"])
        self.assertIn("globalLight=true", line["summary"])
        self.assertNotIn("explored areas stayed revealed", line["summary"])

    def test_fields_no_longer_reported_as_unknown_scene_fields(self):
        lines = lines_for({"tokenVision": True, "fog": {"exploration": True}, "globalLight": False})
        unknown = {l.get("path") for l in lines if l["code"] == "scene-field"}
        self.assertFalse(unknown & {"tokenVision", "fog", "globalLight"})

    def test_unreadable_values_still_flag_fog(self):
        (line,) = fog_lines({"fog": {"exploration": "yes"}})
        self.assertIn("could not be read", line["summary"])

    def test_scene_without_fog_data_has_no_line(self):
        self.assertEqual(fog_lines({}), [])


if __name__ == "__main__":
    unittest.main()


class SceneMusicTests(unittest.TestCase):
    def test_linked_playlist_track_is_manual_not_unknown_field(self):
        lines = lines_for({"playlist": "x6wMBGvOgzRIMrAF", "playlistSound": "9jxvW76WO32Crw65"})
        (line,) = [l for l in lines if l["code"] == "scene-playlist"]
        self.assertEqual(line["grade"], "manual")
        self.assertIn("9jxvW76WO32Crw65", line["summary"])
        unknown = {l.get("path") for l in lines if l["code"] == "scene-field"}
        self.assertFalse(unknown & {"playlist", "playlistSound"})

    def test_null_links_emit_nothing(self):
        lines = lines_for({"playlist": None, "playlistSound": None})
        self.assertEqual([l for l in lines if l["code"] == "scene-playlist"], [])
