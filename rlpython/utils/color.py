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


def color(string, color, style='normal', reset=True):
    string = '\001\033[{};{}m\002{}'.format(
        STYLE_CODES[style],
        COLOR_CODES[color],
        string,
    )

    if reset:
        string += '\001\033[0m\002'

    return string
