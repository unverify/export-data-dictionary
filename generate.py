from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet, convert_cell_args


class MyWorksheet(Worksheet):
    """
    Subclass of the XlsxWriter Worksheet class to override the default
    write_string() method.
    """

    def excel_string_width(self, str):
        """
        Calculate the length of the string in Excel character units. This is only
        an example and won't give accurate results. It will need to be replaced
        by something more rigorous.

        """
        string_width = len(str)
        return string_width * 1.1

    @convert_cell_args
    def write_string(self, row, col, string, cell_format=None):
        # Overridden write_string() method to store the maximum string width
        # seen in each column.

        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Set the min width for the cell. In some cases this might be the
        # default width of 8.43. In this case we use 0 and adjust for all
        # string widths.
        min_width = 0

        # Check if it the string is the largest we have seen for this column.
        string_width = self.excel_string_width(string)
        if string_width > min_width:
            max_width = self.max_column_widths.get(col, min_width)
            if string_width > max_width:
                self.max_column_widths[col] = string_width

        # Now call the parent version of write_string() as usual.
        return super().write_string(row, col, string, cell_format)


class ExportDataDictionary(Workbook):

    def __init__(self, filename: str):
        super().__init__(filename)
        self._worksheet: Worksheet = None
        self._bold = self.add_format({'bold': 1})
        self._row = 0
        self._col = 0

    def add_worksheet(self, name=None):
        # Overwrite add_worksheet() to create a MyWorksheet object.
        # Also add an Worksheet attribute to store the column widths.
        worksheet = super().add_worksheet(name, MyWorksheet)
        worksheet.max_column_widths = {}
        return worksheet

    def close(self):
        # We apply the stored column widths for each worksheet when we close
        # the workbook. This will override any other set_column() values that
        # may have been applied. This could be handled in the application code
        # below, instead.
        for worksheet in self.worksheets():
            for column, width in worksheet.max_column_widths.items():
                worksheet.set_column(column, column, width)
        return super().close()

    def write_header(self, table_header: list):
        for index, header_name in enumerate(table_header):
            self._worksheet.write_string(self._row, self._col + index, header_name, self._bold)
        self._row += 1

    def create_table(self, table_name: str, schema: list):
        self._worksheet.write_string(self._row, self._col, 'Table:', self._bold)
        self._worksheet.write_string(self._row, self._col+1, table_name, self._bold)
        self._row += 1
        self._worksheet.write_string(self._row, self._col, 'Description:', self._bold)
        self._row += 1
        self.write_header(['COLUMN_ID', 'COLUMN_NAME', 'DESCRIPTION', 'DATA_TYPE', 'DATA_LENGTH', 'NULLABLE', 'Key Type'])
        for index, column in enumerate(schema):
            self._worksheet.write_string(self._row, self._col, str(index + 1))
            self._worksheet.write_string(self._row, self._col + 1, column['column_name'])
            self._worksheet.write_string(self._row, self._col + 2, column['column_comment'])
            self._worksheet.write_string(self._row, self._col + 3, column['column_type'])
            self._worksheet.write_string(self._row, self._col + 4, column['column_type'])
            self._worksheet.write_string(self._row, self._col + 5, column['is_nullable'])
            self._worksheet.write_string(self._row, self._col + 6, column['extra'])
            self._row += 1
        self._row += 2

    def generate_xlsx_simple(self, data: dict):
        self._worksheet: Worksheet = self.add_worksheet(name='Data Dictionary')
        for table_name, schema in data.items():
            print(f'Generating {table_name}...')
            self.create_table(table_name, schema)
        self.close()

    def generate_xlsx(self, data: dict):
        next_app = ''
        for table_name, schema in data.items():
            table_name_raw = table_name.split('_')
            app_name = table_name_raw[0]
            if next_app != app_name:
                self._worksheet: Worksheet = self.add_worksheet(name=app_name)
                self._row = 0
                self._col = 0
                next_app = app_name
            print(f'Generating app_name={app_name} {table_name}...')
            self.create_table(table_name, schema)
        self.close()
