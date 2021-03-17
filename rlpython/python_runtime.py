from rlcompleter import Completer
from pprint import pformat
import inspect

from rlpython.utils.attribute_table import AttributeTable


class PythonRuntime:
    def __init__(self, repl, globals={}, locals={}):
        self.repl = repl
        self.globals = globals
        self.locals = locals

        self.completer = Completer(namespace=self.locals)

        # override print
        self.globals['print'] = self.print_function

        # prepare special keywords
        self.locals['_'] = None
        self.locals['_rlpython'] = self.repl
        self.locals['_exception'] = None

    def shutdown(self):
        del self.globals['print']

        del self.locals['_']
        del self.locals['_rlpython']
        del self.locals['_exception']

    def complete(self, text, state):
        return self.completer.complete(text, state)

    def print_function(self, *strings, end='\n'):
        string = ' '.join([str(i) for i in strings]) + end

        return self.repl.write(string)

    # introspection ###########################################################
    def get_file(self, obj):
        filename = None
        lineno = None

        try:
            filename = inspect.getabsfile(obj)

        except Exception:
            pass

        if not filename and hasattr(obj, '__class__'):
            try:
                obj = obj.__class__
                filename = inspect.getabsfile(obj)

            except Exception:
                pass

        if filename:
            try:
                lineno = inspect.getsourcelines(obj)[1]

            except Exception:
                pass

        return filename, lineno

    def get_file_string(self, obj):
        filename, lineno = self.get_file(obj)
        string = ''

        if filename:
            string = filename

            if lineno:
                string += ':' + str(lineno)

        return string

    def write_short_description(self, value):
        attribute_table = AttributeTable()

        attribute_table.add_row(['id', hex(id(value))])
        attribute_table.add_row(['type', repr(type(value))])

        # filename
        filename = self.get_file_string(value)

        if filename:
            attribute_table.add_row(['file', filename])

        # signature
        if callable(value):
            try:
                signature = '{}{}'.format(
                    value.__name__,
                    inspect.signature(value),
                )

                attribute_table.add_row(['signature', signature])

            except Exception:
                pass

        # write to repl
        for line in attribute_table:
            self.repl.write(line + '\n')

    def write_long_description(self, value):
        documentation = inspect.getdoc(value)

        if not documentation:
            return

        self.repl.write(documentation + '\n')

    def write_description(self, value, length):
        if length == 1:
            self.write_short_description(value)

        elif length == 2:
            self.write_long_description(value)

    # source code helper ######################################################
    def parse_source(self, raw_source):
        multiline = len(raw_source.splitlines()) > 1
        terminated = raw_source.endswith('\n\n')
        describe = 0
        source = raw_source.strip()

        # long description
        if source[len(source)-2:] == '??':
            source = source[:-2]
            describe = 2

        # short description
        elif source[-1] == '?':
            source = source[:-1]
            describe = 1

        return source, multiline, terminated, describe

    def validate_source(self, raw_source):
        source, multiline, terminated, describe = self.parse_source(raw_source)

        if multiline and not terminated:
            return False

        try:
            compile(source, filename='<string>', mode='exec')

            return True

        except Exception:
            return False

    # code running ############################################################
    def eval(self, source):
        try:
            return eval(source, self.globals, self.locals)

        except Exception:
            return None

    def run(self, raw_source):
        exit_code = 0
        source, multiline, terminated, describe = self.parse_source(raw_source)

        # compile source
        try:
            run_code = eval

            code = compile(
                source=source,
                filename='<input>',
                mode='eval',
            )

        except SyntaxError:
            code = None

        if not code:
            try:
                run_code = exec

                code = compile(
                    source=source,
                    filename='<input>',
                    mode='exec',
                )

            except SyntaxError as exception:
                self.locals['_exception'] = exception
                self.repl.write_exception(exception)

                return 1

        # run code
        try:
            return_value = run_code(code, self.globals, self.locals)

        except KeyboardInterrupt:
            exit_code = 1

            self.repl.write('\n')

        except Exception as exception:
            exit_code = 1

            self.locals['_exception'] = exception
            self.repl.write_exception(exception)

        else:
            if run_code is eval:
                self.locals['_'] = return_value

                if describe:
                    self.write_description(return_value, describe)

                elif return_value is not None:
                    try:
                        self.repl.write(pformat(return_value) + '\n')

                    except Exception:
                        self.repl.write(repr(return_value) + '\n')

        return exit_code
