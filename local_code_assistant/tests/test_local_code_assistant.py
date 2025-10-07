import os
import unittest
import tempfile
from pathlib import Path

from local_code_assistant import LocalCodeAssistant


class TestLocalCodeAssistant(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory as a fake project root
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)

        # Create some files and directories
        (self.root / 'a.txt').write_text('hello\nworld\n')
        (self.root / 'dir').mkdir()
        (self.root / 'dir' / 'b.txt').write_text('line1\nTODO: fix\n')

        # Create excluded directories
        (self.root / '.git').mkdir()
        (self.root / '.git' / 'ignored').write_text('x')
        (self.root / 'node_modules').mkdir()
        (self.root / 'node_modules' / 'pkg.js').write_text('x')

        self.assistant = LocalCodeAssistant(str(self.root))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_list_files_basic(self):
        res = self.assistant.list_files(directory='.')
        self.assertEqual(res['status'], 'success')
        files = set(res['files'])
        # Expect to see our files
        self.assertIn('a.txt', files)
        self.assertIn('dir/b.txt', files)
        # Excluded directories should not appear
        for path in files:
            self.assertFalse(path.startswith('.git'))
            self.assertFalse(path.startswith('node_modules'))

    def test_read_write_file(self):
        # Write a new file
        write_res = self.assistant.write_file('out/new.txt', 'abc\n')
        self.assertEqual(write_res['status'], 'success')
        # Read it back
        read_res = self.assistant.read_file('out/new.txt')
        self.assertEqual(read_res['status'], 'success')
        self.assertEqual(read_res['content'], 'abc\n')

    def test_search_in_files(self):
        res = self.assistant.search_in_files('TODO')
        self.assertEqual(res['status'], 'success')
        results = res['results']
        self.assertTrue(any(r['filepath'] == 'dir/b.txt' and r['line_number'] == 2 for r in results))

    def test_path_traversal_protection(self):
        # Attempt to read a file outside the project
        outside = str(self.root.parent / 'outside_tmp.txt')
        Path(outside).write_text('outside')
        # Provide a relative path that escapes
        read_res = self.assistant.read_file(os.path.join('..', Path(outside).name))
        self.assertEqual(read_res['status'], 'error')


if __name__ == '__main__':
    unittest.main()
