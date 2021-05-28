from rlpython.protocol import encode_edit_message

from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.editor import NoEditorError, run_editor


class EditCommand:
    """
    Open source code of given object in $EDITOR if source code is available
    """

    NAME = 'edit'

    def __init__(self, repl):
        self.repl = repl

    def complete(self, text, state, line_buffer):
        return self.repl.completer.python_complete(
            text=text,
            state=state,
            line_buffer=line_buffer[len(self.NAME)+1:],
        )

    def run(self, argv):
        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='edit')
        argument_parser.add_argument('object')

        arguments = argument_parser.parse_args(argv[1:])

        # find object
        obj = self.repl.python_runtime.eval(arguments.object)

        if not obj:
            self.repl.write_error(
                '{} not found\n'.format(repr(arguments.object)),
            )

            return 1

        # find file
        filename, lineno = self.repl.python_runtime.get_file(obj)

        if not filename:
            self.repl.write_error(
                '{} source file not found\n'.format(repr(obj)),  # NOQA
            )

            return 1

        if not filename.endswith('.py'):
            self.repl.write(
                "'{}' is no python file\n".format(filename),  # NOQA
            )

            return 1

        # local
        if self.repl.domain == self.repl.DOMAIN.LOCAL:
            try:
                run_editor(filename, lineno=lineno)

            except NoEditorError:
                self.repl.write_error('no editor found\n')

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
