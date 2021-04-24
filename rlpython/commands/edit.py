from rlpython.protocol import encode_edit_message

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.editor import NoEditorError, run_editor
from rlpython.utils.strings import color


class EditCommand:
    """
    Open source code of given object in $EDITOR if source code is available
    """

    NAME = 'edit'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='edit')
        argument_parser.add_argument('object')

        arguments = argument_parser.parse_args(argv[1:])

        # find object
        obj = self.repl.python_runtime.eval(arguments.object)

        if not obj:
            self.repl.write(
                color("ERROR: '{}' not found\n".format(arguments.object), fg='red'),  # NOQA
            )

            return 1

        # find file
        filename, lineno = self.repl.python_runtime.get_file(obj)

        if not filename:
            self.repl.write(
                color("ERROR: '{}' source file not found\n".format(repr(obj)), fg='red'),  # NOQA
            )

            return 1

        if not filename.endswith('.py'):
            self.repl.write(
                color("ERROR: '{}' is no python file\n".format(filename), fg='red'),  # NOQA
            )

            return 1

        # local
        if self.repl.domain == self.repl.DOMAIN.LOCAL:
            try:
                run_editor(filename, lineno=lineno)

            except NoEditorError:
                self.repl.write(
                    color('ERROR: no editor found\n', fg='red'),
                )

        # network
        else:
            encode_text = False

            if self.repl.domain == self.repl.DOMAIN.NETWORK:
                encode_text = True

            message = encode_edit_message(
                filename=filename,
                lineno=lineno,
                encode_text=encode_text,
            )

            self.repl.write_message(message)
