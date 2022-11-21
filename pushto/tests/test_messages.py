import unittest
import pushto.messages


class TestDataMessage(unittest.TestCase):

    def setUp(self):
        self.msg = pushto.messages.DataMessage(time=123, phi_cnt=1000, theta_cnt=-100)

    def test_data_message(self):
        self.assertEqual(self.msg.type, 'DATA')
        self.assertEqual(self.msg.time, 123)
        self.assertEqual(self.msg.phi_cnt, 1000)
        self.assertEqual(self.msg.theta_cnt, -100)
        self.assertIsNone(self.msg.phi_raw)
        self.assertIsNone(self.msg.theta_raw)
        self.assertIsNone(self.msg.phi)
        self.assertIsNone(self.msg.theta)
        self.assertIsNone(self.msg.azi)
        self.assertIsNone(self.msg.alt)
        self.assertIsNone(self.msg.ra)
        self.assertIsNone(self.msg.dec)

        self.msg.ra = 0
        self.assertEqual(self.msg.ra, 0)

    def test_to_json(self):
        msg_json = self.msg.to_json()
        self.assertIn('type', msg_json)
        self.assertIn('time', msg_json)
        self.assertIn('phi_cnt', msg_json)
        self.assertIn('theta_cnt', msg_json)
        self.assertIn('phi_raw', msg_json)
        self.assertIn('theta_raw', msg_json)
        self.assertIn('phi', msg_json)
        self.assertIn('theta', msg_json)
        self.assertIn('azi', msg_json)
        self.assertIn('alt', msg_json)
        self.assertIn('ra', msg_json)
        self.assertIn('dec', msg_json)

    def test_from_json(self):
        msg_json = self.msg.to_json()
        msg = pushto.messages.Message.from_json(msg_json)
        self.assertIsInstance(msg, pushto.messages.DataMessage)


class TestCmdMessage(unittest.TestCase):

    def setUp(self):
        self.msg = pushto.messages.CmdMessage(cmd='stop')

    def test_cmd_message(self):
        self.assertEqual(self.msg.type, 'CMD')
        self.assertEqual(self.msg.cmd, 'stop')
        self.assertIsNone(self.msg.opt)

        self.msg.opt = {'opt1': 1, }
        self.assertEqual(self.msg.opt, {'opt1': 1})

    def test_to_json(self):
        msg_json = self.msg.to_json()
        self.assertIn('type', msg_json)
        self.assertIn('cmd', msg_json)
        self.assertIn('opt', msg_json)

    def test_from_json(self):
        msg_json = self.msg.to_json()
        msg = pushto.messages.Message.from_json(msg_json)
        self.assertIsInstance(msg, pushto.messages.CmdMessage)


class TestAlignMessage(unittest.TestCase):

    def setUp(self):
        self.msg = pushto.messages.AlignMessage(time=321, ra=55, dec=-10)

    def test_align_message(self):
        self.assertEqual(self.msg.type, 'ALIGN')
        self.assertEqual(self.msg.time, 321)
        self.assertEqual(self.msg.ra, 55)
        self.assertEqual(self.msg.dec, -10)
        self.assertIsNone(self.msg.azi)
        self.assertIsNone(self.msg.alt)

        self.msg.alt = 42
        self.assertEqual(self.msg.alt, 42)

    def test_to_json(self):
        msg_json = self.msg.to_json()
        self.assertIn('type', msg_json)
        self.assertIn('time', msg_json)
        self.assertIn('azi', msg_json)
        self.assertIn('alt', msg_json)
        self.assertIn('ra', msg_json)
        self.assertIn('dec', msg_json)

    def test_from_json(self):
        msg_json = self.msg.to_json()
        msg = pushto.messages.Message.from_json(msg_json)
        self.assertIsInstance(msg, pushto.messages.AlignMessage)


if __name__ == '__main__':
    unittest.main()
