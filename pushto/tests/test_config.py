import unittest
import pushto.config


class TestConfiguration(unittest.TestCase):

    def test_load_default(self):
        cfg = pushto.config.Configuration()
        self.assertIn('COMMUNICATION', cfg.config)

    def test_load_file(self):
        cfg = pushto.config.Configuration(filename=pushto.config.DEFAULT_CONFIG_FILE)
        self.assertIn('COMMUNICATION', cfg.config)

    def test_save_default(self):
        cfg = pushto.config.Configuration()
        cfg.save()


if __name__ == '__main__':
    unittest.main()
