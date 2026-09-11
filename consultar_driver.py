import pyodbc

print("Driver ODBC instaladas nesta máquina:")
for driver in pyodbc.drivers():
    print(f"-{driver}")