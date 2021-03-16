from copy import deepcopy

from rlpython.utils.strings import get_length


def write_table(rows, write):
    rows = deepcopy(rows)

    # find column widths
    column_widths = [[] for i in range(len(rows[0]))]

    for row_index, row in enumerate(rows):
        for column_index, column in enumerate(row):
            lines = str(column).strip().splitlines()
            rows[row_index][column_index] = lines

            column_widths[column_index].append(
                max([get_length(line) for line in lines])
            )

    for index, column_width in enumerate(column_widths):
        column_widths[index] = max(column_widths[index])

    # write table out
    def write_divider():
        for column_width in column_widths:
            write('+')
            write('-' * (column_width + 2))

        write('+\n')

    def write_empty_row():
        for column_width in column_widths:
            write('|')
            write(' ' * (column_width + 2))

        write('|\n')

    def write_row(row):
        lines = max([len(i) for i in row])

        if lines > 1:
            write_empty_row()

        for line_index in range(lines):
            write('| ')

            for column_index, column in enumerate(row):
                if line_index < len(column):
                    line = column[line_index]

                else:
                    line = ''

                write(line.ljust(column_widths[column_index]))
                write(' | ')

            write('\n')

        if lines > 1 and row is not rows[-1]:
            write_empty_row()

    write_divider()
    write_row(rows[0])
    write_divider()

    for row in rows[1:]:
        write_row(row)

    write_divider()
