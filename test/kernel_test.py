import unittest
import jupyter_kernel_test

class KernelTests(jupyter_kernel_test.KernelTests):

    # Required by jupyter_kernel_test:
    kernel_name = "coq"
    language_name = "coq"

    # Actual tests:
    code_execute_result = [
        {'code': 'Check True.', 'result': '\x1b[92;49;22;23;24;27mTrue\x1b[39;49;22;23;24;27m\r\n     : \x1b[33;49;1;23;24;27mProp\x1b[39;49;22;23;24;27m\r\n\r\n'}
    ]

def validate_message(msg, msg_type=None, parent_id=None):
    pass

if __name__ == '__main__':
    unittest.main()
