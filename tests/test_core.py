import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from pet_app.behavior import WalkBounds, automatic_state, next_x
from pet_app.config import PetSettings, SettingsStore
from pet_app.states import PetState, parse_state


TEST_TEMP_ROOT = Path(__file__).parents[1] / ".test-tmp"


def workspace_temp_directory():
    TEST_TEMP_ROOT.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT)


class SettingsTests(unittest.TestCase):
    def test_round_trip(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "settings.json"
            source = PetSettings(x=12, y=34, width=220, opacity=0.7, current_state=PetState.ANGRY)
            store = SettingsStore(path)
            store.save(source)
            loaded = store.load()
            self.assertEqual(loaded.to_dict(), source.to_dict())

    def test_invalid_json_uses_defaults(self):
        with workspace_temp_directory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("not json", encoding="utf-8")
            loaded = SettingsStore(path).load()
            self.assertEqual(loaded.current_state, PetState.IDLE)

    def test_unknown_state_falls_back_to_idle(self):
        self.assertEqual(parse_state("removed-state"), PetState.IDLE)


class BehaviorTests(unittest.TestCase):
    def test_walk_reverses_at_bounds(self):
        bounds = WalkBounds(0, 100, 200)
        self.assertEqual(next_x(99, 2, bounds), (100, -2))
        self.assertEqual(next_x(1, -2, bounds), (0, 2))

    def test_sleep_only_when_active(self):
        self.assertEqual(automatic_state(PetState.IDLE, False, 300, 300), PetState.SLEEPING)
        self.assertEqual(automatic_state(PetState.IDLE, True, 300, 300), PetState.IDLE)
        self.assertEqual(automatic_state(PetState.ANGRY, False, 300, 300), PetState.ANGRY)

    def test_idle_becomes_walking_after_delay(self):
        self.assertEqual(automatic_state(PetState.IDLE, False, 5, 300), PetState.WALKING)


if __name__ == "__main__":
    unittest.main()
