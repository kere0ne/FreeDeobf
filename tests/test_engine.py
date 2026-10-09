import unittest
from freedeobf.engine import deobfuscate

class DeobfuscatorTests(unittest.TestCase):
    def test_lua_decimal_escapes(self):
        output, _ = deobfuscate(r'print("\104\105")', "lua")
        self.assertIn('"hi"', output)
    def test_explicit_base64(self):
        output, _ = deobfuscate("x = base64.decode('SGVsbG8=')", "python")
        self.assertIn("Hello", output)
    def test_whitespace(self):
        output, _ = deobfuscate("print('ok')  \r\n\r\n\r\n")
        self.assertEqual(output, "print('ok')\n")
    def test_does_not_execute_input(self):
        output, _ = deobfuscate("__import__('os').system('echo SHOULD_NOT_RUN')")
        self.assertIn("SHOULD_NOT_RUN", output)
    def test_pass_validation(self):
        with self.assertRaises(ValueError): deobfuscate("x", passes=0)

if __name__ == "__main__": unittest.main()