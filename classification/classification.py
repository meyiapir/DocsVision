from config import DOC_TYPES_DICT
import csv


class Classificator:
    def __init__(self):
        pass

    def find_by_name_frequency(self, text):
        counts = []
        r = {}
        for i, document_type in enumerate(DOC_TYPES_DICT):
            count = text.lower().count(f'{DOC_TYPES_DICT[document_type].lower()} ')
            r.update({tuple(DOC_TYPES_DICT.keys())[i]: count})
            counts.append(count)

        return list(DOC_TYPES_DICT.keys())[counts.index(max(counts))]




classificator = Classificator()

total, right = 0, 0

data = []
with open('files/sample.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        if classificator.find_by_name_frequency(row[1]) == row[0]:
            right += 1
        total += 1

print((right/total)*100)
