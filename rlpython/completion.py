from rlcompleter import Completer as rlCompleter
from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from itertools import chain
from glob import glob
import sys
import os


class Namespace(dict):
    def __init__(self, locals, globals):
        self.locals = locals
        self.globals = globals

    def items(self):
        return chain(
            self.locals.items(),
            self.globals.items(),
        )

    def __getitem__(self, name):
        if name in self.locals:
            return self.locals[name]

        if name in self.globals:
            return self.globals[name]

        raise KeyError


class Completer:
    def __init__(self, repl):
        self.repl = repl

        self.rlcompleter = rlCompleter(
            namespace=Namespace(
                locals=self.repl.locals,
                globals=self.repl.globals,
            ),
        )

        self._module_cache = []

    # python complete #########################################################
    def _complete_imports(self, text, state, line_buffer):
        raw_candidates = []
        line_buffer_parts = line_buffer.strip().split(' ')

        # find completion case ###############################################
        #
        # possible cases:
        #     1. import <TAB>             complete from packages and modules
        #     2. from <TAB>               complete from packages and modules
        #     3. from foo <TAB>           complete 'import'
        #     4. from foo import <TAB>    complete from foo

        case = None

        if line_buffer_parts[0] == 'import':
            case = 1

        elif line_buffer_parts[0] == 'from':
            if len(line_buffer_parts) >= 3:
                if line_buffer_parts[2] == 'import':
                    case = 4

                elif(text and 'import'.startswith(text) and
                     not line_buffer_parts[1].endswith('.')):

                    case = 3

                else:
                    case = 2

            else:
                if(len(line_buffer_parts) > 1 and
                   not line_buffer_parts[1].endswith('.') and
                   line_buffer[-2] == ' '):

                    case = 3

                else:
                    case = 2

        # case 3
        if case == 3:
            return ['import ', None][state]

        # find cursor position ################################################
        # from <POSITION 1> import <POSITION 2>

        if case in (1, 2, 3):
            cursor_position = 1

        else:
            if text == line_buffer_parts[1]:
                cursor_position = 1

            else:
                cursor_position = 2

        # parse completion text ###############################################
        if(case in (1, 2) or
           case == 4 and cursor_position == 1):

            module_name, part = (text.rsplit('.', 1) + [''])[0:2]

            if '.' not in text:
                module_name, part = part, module_name

        elif case == 4:
            module_name = line_buffer_parts[1]
            part = text

        # complete packages ###################################################
        if module_name == '':
            if not self._module_cache:
                for module_info in iter_modules():
                    self._module_cache.append([module_info.name])

            raw_candidates.extend(self._module_cache)

        # complete modules ####################################################
        else:
            if module_name in sys.modules:
                clear_module = False
                module = sys.modules[module_name]

            else:
                clear_module = True

                try:
                    module = import_module(module_name)

                except Exception:
                    return [None][state]

            # iterate over module attributes
            for attribute_name in dir(module):
                if cursor_position == 1:

                    # skip non module attributes when in cursor position 1
                    attribute = getattr(module, attribute_name)

                    if not isinstance(attribute, ModuleType):
                        continue

                    raw_candidates.append(
                        [module_name, attribute_name],
                    )

                elif cursor_position == 2:
                    raw_candidates.append(
                        [attribute_name],
                    )

            # find submodules
            if os.path.basename(module.__file__) == '__init__.py':
                module_dir = os.path.dirname(module.__file__)

                for rel_path in os.listdir(module_dir):
                    abs_path = os.path.join(module_dir, rel_path)

                    if os.path.isdir(abs_path):
                        if rel_path == '__pycache__':
                            continue

                        init_module_path = os.path.exists(
                            os.path.join(abs_path, '__init__.py')
                        )

                        if not os.path.exists(init_module_path):
                            continue

                        if cursor_position == 1:
                            raw_candidates.append(
                                [module_name, rel_path],
                            )

                        elif cursor_position == 2:
                            raw_candidates.append(
                                [rel_path],
                            )

                    elif rel_path.endswith('.py'):
                        sub_module_name = rel_path[:-3]

                        if sub_module_name == '__init__':
                            continue

                        if cursor_position == 1:
                            raw_candidates.append(
                                [module_name, sub_module_name],
                            )

                        elif cursor_position == 2:
                            raw_candidates.append(
                                [sub_module_name],
                            )

            if clear_module:
                del sys.modules[module_name]

        # generate candidates
        candidates = []

        for raw_candidate in raw_candidates:
            if not raw_candidate[-1].startswith(part):
                continue

            # skip privat and protected values if not
            # explicitly requested
            if raw_candidate[-1].startswith('_') and not text.endswith('_'):
                continue

            candidates.append('.'.join(raw_candidate))

        candidates.sort()
        candidates.append(None)

        return candidates[state]

    def python_complete(self, text, state, line_buffer):
        cleaned_line_buffer = line_buffer.strip()

        # imports
        if(cleaned_line_buffer.startswith('from') or
           cleaned_line_buffer.startswith('import')):

            return self._complete_imports(text, state, line_buffer)

        return self.rlcompleter.complete(text, state)

    # command complete ########################################################
    def command_complete(self, text, state, line_buffer):
        # run custom completion
        if ' ' in line_buffer:
            command_name = line_buffer.split(' ', 1)[0]

            if(command_name and
               command_name in self.repl.command_runtime.commands):

                command = self.repl.command_runtime.commands[command_name]

                if hasattr(command, 'complete'):
                    return command.complete(text, state, line_buffer)

        # complete from command_runtime.commands
        candidates = []

        for name in sorted(self.repl.command_runtime.commands.keys()):
            if name.startswith(text):
                candidates.append(name)

        candidates.append(None)

        return candidates[state]

    # file complete ###########################################################
    def file_complete(self, text, state, line_buffer):
        path = os.path.normpath(text)

        if os.path.isdir(path) and path != '/':
            path += '/'

        candidates = []

        for candidate in glob(path + '*'):
            candidate = os.path.normpath(candidate)

            if os.path.isdir(candidate):
                candidate += '/'

            if candidate not in candidates:
                candidates.append(candidate)

        candidates.sort()
        candidates.append(None)

        return candidates[state]

    def complete(self, text, state, line_buffer):
        try:
            line_buffer = self.repl.aliases.resolve(line_buffer + '\n')

            # commands
            if line_buffer.startswith('%'):
                line_buffer = line_buffer[1:]

                return self.command_complete(
                    text=text,
                    state=state,
                    line_buffer=line_buffer,
                )

            # shell
            elif line_buffer.startswith('!'):
                return self.file_complete(
                    text=text,
                    state=state,
                    line_buffer=line_buffer,
                )

            # python
            return self.python_complete(text, state, line_buffer)

        except Exception as e:
            self.repl.write('\n')
            self.repl.write_exception(e, prefix='rlpython: ')
