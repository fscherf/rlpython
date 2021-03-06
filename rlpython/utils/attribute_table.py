from rlpython.utils.color import color


class AttributeTable:
    def __init__(self):
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def __iter__(self):
        header_length = max([len(row[0]) for row in self.rows]) + 1

        for row in self.rows:
            line = '{}: {}'.format(
                color(row[0].rjust(header_length), color='red'),
                row[1],
            )

            yield line
