import json
import unittest
from unittest.mock import patch

import mycroft
from mycroft.audio.audioservice import AudioService
from ovos_utils.messagebus import FakeBus

# Patch Configuration in the audioservice module to ensure its patched
from ovos_config.config import Configuration
mycroft.audio.audioservice.Configuration = Configuration


BASE_CONF = {"Audio":
    {
        "native_sources": ["debug_cli", "audio"],
        "default-backend": "OCP",  # only used by mycroft-core
        "preferred_audio_services": ["ovos_test", "mycroft_test"],
        "backends": {
            "OCP": {
                "type": "ovos_common_play",
                "active": True,
                "mode": "external",
                "disable_mpris": True
            },
            "mycroft_test": {
                "type": "mycroft_test",
                "active": True
            },
            "ovos_test": {
                "type": "ovos_test",
                "active": True
            }
        }
    }
}


class TestExternalOCP(unittest.TestCase):
    bus = FakeBus()

    @classmethod
    def setUpClass(cls) -> None:
        cls.bus.emitted_msgs = []

        def get_msg(msg):
            msg = json.loads(msg)
            msg.pop("context")
            cls.bus.emitted_msgs.append(msg)

        cls.bus.on("message", get_msg)

    @patch.object(Configuration, 'load_all_configs')
    def test_external_ocp(self, mock):
        mock.return_value = BASE_CONF
        audio = AudioService(self.bus)
        self.assertEqual(audio.config, BASE_CONF["Audio"])
        # assert that ocp is in external mode
        self.assertEqual(audio.default.config["mode"], "external")
        # assert that OCP is not loaded
        self.assertTrue(audio.default.ocp is None)
        audio.shutdown()


if __name__ == '__main__':
    unittest.main()
