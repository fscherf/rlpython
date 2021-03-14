from rlpython.utils.argument_parser import ReplArgumentParser
from rlpython.utils.editor import NoEditorError, run_editor


class EditCommand:
    NAME = 'edit'

    def run(self, repl, argv):
        if repl.domain != repl.DOMAIN.LOCAL:
            repl.write('ERROR: editing over network is not supported\n')

            return 1

        # parse command line
        argument_parser = ReplArgumentParser(repl=repl, prog='edit')
        argument_parser.add_argument('object')

        arguments = argument_parser.parse_args(argv[1:])

        # find object
        obj = repl.python_runtime.eval(arguments.object)

        if not obj:
            repl.write("ERROR: '{}' not found\n".format(arguments.object))

            return 1

        # find file
        filename, lineno = repl.python_runtime.get_file(obj)

        if not filename:
            repl.write("ERROR: '{}' source file not found\n".format(repr(obj)))

            return 1

        # start editor
        try:
            run_editor(filename, lineno=lineno)

        except NoEditorError:
            repl.write('ERROR: no editor found\n')
