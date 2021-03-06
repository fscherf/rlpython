import subprocess
import shutil
import shlex
import os

EDITORS = [
    'vim',
    'vi',
    'nano',
]


class NoEditorError(Exception):
    pass


def run_editor(filename, lineno=None):
    editor = os.environ.get('EDITOR')

    if not editor:
        for name in EDITORS:
            if shutil.which(name):
                editor = name

                break

    if not editor:
        raise NoEditorError()

    command = '{} {}'.format(editor, filename)

    if lineno is not None:
        command = '{} +{}'.format(command, lineno)

    subprocess.call(shlex.split(command))
