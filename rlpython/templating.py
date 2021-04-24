EXPR_START = '{{'
EXPR_STOP = '}}'
EXPR_START_LEN = len(EXPR_START)
EXPR_STOP_LEN = len(EXPR_STOP)


class TemplatingEngine:
    def __init__(self, repl):
        self.repl = repl

    def split(self, string):
        strings = []

        cursor = 0
        recording = False

        while cursor <= len(string):
            if recording:

                # searching for EXPR_STOP
                if string[cursor:cursor+EXPR_STOP_LEN].startswith(EXPR_STOP):
                    strings.append(
                        (True, string[EXPR_START_LEN:cursor],)
                    )

                    string = string[cursor+EXPR_STOP_LEN:]
                    cursor = 0
                    recording = False

                    continue

            else:

                # searching for EXPR_START
                if string[cursor:].startswith(EXPR_START):
                    recording = True

                    if cursor > 0:
                        strings.append(
                            (False, string[:cursor],)
                        )

                        string = string[cursor:]
                        cursor = 0

                    continue

            cursor += 1

        if not len(string) == 0:
            strings.append(
                (False, string,)
            )

        return strings

    def render(self, template):
        output = ''
        parts = self.split(template)

        for is_expression, string in parts:
            if is_expression:
                resolved_expression = self.repl.python_runtime.eval(
                    string,
                    safe=False,
                )

                if resolved_expression is None:
                    continue

                string = str(resolved_expression)

            output += string

        return output

    def is_template(self, string):
        return EXPR_START in string
