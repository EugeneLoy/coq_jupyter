import unittest
import jupyter_kernel_test

class KernelTests(jupyter_kernel_test.KernelTests):

    # Required by jupyter_kernel_test.KernelTests:
    kernel_name = "coq"
    language_name = "coq"

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
