import csv

file_path = 'Short_CSV.csv'
middle_column_values = []

with open(file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        # Assuming each row has at least 3 columns
        middle_column_values.append(int(row[1]))

print(middle_column_values)