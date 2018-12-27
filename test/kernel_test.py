import unittest
import jupyter_kernel_test

class KernelTests(jupyter_kernel_test.KernelTests):

    # Required by jupyter_kernel_test.KernelTests:
    kernel_name = "coq"
    language_name = "coq"

    # Used by tests inherited from jupyter_kernel_test.KernelTests:
    code_execute_result = [{
        'code': 'Check True.',
        'result': '\x1b[92;49;22;23;24;27mTrue\x1b[39;49;22;23;24;27m\r\n     : \x1b[33;49;1;23;24;27mProp\x1b[39;49;22;23;24;27m\r\n\r\n'
    }]

    # Custom tests:
    def test_coq_jupyter_execute_one_line(self):
        self.flush_channels()
        reply, output_msgs = self.execute_helper(code='Check True.')

        self.assertEqual(reply['content']['status'], 'ok')
        self.assertEqual(len(output_msgs), 1)
        self.assertEqual(output_msgs[0]['msg_type'], 'execute_result')
        self.assertIn('text/plain', output_msgs[0]['content']['data'])
        self.assertIn("Prop", output_msgs[0]['content']['data']['text/plain'])


if __name__ == '__main__':
    unittest.main()
