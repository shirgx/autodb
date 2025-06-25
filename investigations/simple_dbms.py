import struct

class SimpleDB:
    def __init__(self, directory="./simple_db"):
        self.dir = directory

        self.tables = {}

    def create_table(self, table_name, columns):

        fmt_parts = []
        for (name, col_type, length) in columns:
            if col_type == 'INT':
                fmt_parts.append('I')         
            elif col_type == 'STR':
                fmt_parts.append(f'{length}s')  
        fmt = "".join(fmt_parts)

        self.tables[table_name] = {"columns": columns, "fmt": fmt, "index": {}}

        open(f"{self.dir}/{table_name}.dat", "wb").close()
        with open(f"{self.dir}/{table_name}.sch", "w") as sch:
            sch.write(str(columns))

    def insert(self, table_name, values):

        table = self.tables[table_name]
        fmt = table["fmt"]
        data_file = f"{self.dir}/{table_name}.dat"

        packed = struct.pack(fmt, *values)
        with open(data_file, "ab") as f:
            pos = f.tell()            
            f.write(packed)

        first_col = table["columns"][0]
        if first_col[1] == 'INT':     
            key = values[0]
            table["index"][key] = pos

    def select_where(self, table_name, col_name, value):

        table = self.tables[table_name]
        columns = table["columns"]
        fmt = table["fmt"]
        data_file = f"{self.dir}/{table_name}.dat"

        col_index = next(i for i, col in enumerate(columns) if col[0] == col_name)
        results = []

        if columns[col_index][1] == 'INT' and col_index == 0 and value in table["index"]:
            pos = table["index"][value]
            with open(data_file, "rb") as f:
                f.seek(pos)
                record_bytes = f.read(struct.calcsize(fmt))
                if record_bytes:
                    record = struct.unpack(fmt, record_bytes)
                    results.append(record)
        else:

            with open(data_file, "rb") as f:
                record_size = struct.calcsize(fmt)
                while True:
                    record_bytes = f.read(record_size)
                    if not record_bytes:
                        break
                    record = struct.unpack(fmt, record_bytes)
                    if record[col_index] == value:
                        results.append(record)
        return results

    