from rlpython.utils.strings import color


def write_attribute_table(rows, write, header_fg=None):
    header_length = max([len(row[0]) for row in rows]) + 1

    for row in rows:
        header = row[0].rjust(header_length)

        if header_fg is not None:
            header = color(header, fg=header_fg)

        write('{}: {}\n'.format(header, row[1]))
