from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.editor import NoEditorError, run_editor


class EditCommand:
    NAME = 'edit'

    def __init__(self, repl):
        self.repl = repl

    def run(self, argv):
        if self.repl.domain != self.repl.DOMAIN.LOCAL:
            self.repl.write('ERROR: editing over network is not supported\n')

            return 1

        # parse command line
        argument_parser = ReplArgumentParser(repl=self.repl, prog='edit')
        argument_parser.add_argument('object')

        arguments = argument_parser.parse_args(argv[1:])

        # find object
        obj = self.repl.python_runtime.eval(arguments.object)

        if not obj:
            self.repl.write("ERROR: '{}' not found\n".format(arguments.object))

            return 1

        # find file
        filename, lineno = self.repl.python_runtime.get_file(obj)

        if not filename:
            self.repl.write(
                "ERROR: '{}' source file not found\n".format(repr(obj)))

            return 1

        # start editor
        try:
            run_editor(filename, lineno=lineno)

        except NoEditorError:
            self.repl.write('ERROR: no editor found\n')
