COLOR_CODES = {
    'black': '30',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'magenta': '35',
    'cyan': '36',
    'white': '37',
}

STYLE_CODES = {
    'normal': '0',
    'bright': '1',
    'underlined': '2',
    'negative': '3',
}


def color(string, fg='', bg='', style='normal', reset=True):
    if fg:
        fg = COLOR_CODES[fg]

    if style:
        style = STYLE_CODES[style]

    string = '\001\033[{};{}m\002{}'.format(style, fg, string)

    if reset:
        string += '\001\033[0m\002'

    return string


def get_length(string):
    length = 0
    quoted = False

    for character in string:
        if character == '\001':
            quoted = True

        elif character == '\002':
            quoted = False

        elif not quoted:
            length += 1

    return length
