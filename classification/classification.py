from config import DOC_TYPES_DICT
import csv
from time import time


class Classificator:
    def __init__(self):
        pass

    def find_by_name_frequency(self, text):
        t1 = time()
        r = []

        for i, document_type in enumerate(DOC_TYPES_DICT):
            count = text.lower().count(f'{DOC_TYPES_DICT[document_type].lower()} ')
            r.append((tuple(DOC_TYPES_DICT.keys())[i], count))

        r.sort(reverse=True, key=lambda x: x[1])
        counts = list(map(lambda x: x[1], r))
        score = (counts[0] - counts[1])/(counts[0] or 1) if counts[0] else 0

        if score >= 0.35:
            return r[0][0]
        else:
            return None




classificator = Classificator()

total, right, not_found = 0, 0, 0

data = []
with open('files/sample.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        res = classificator.find_by_name_frequency(row[1])
        print(res)
        if res:
            if res == row[0]:
                right += 1
            total += 1
        else:
            not_found += 1

print((right/total)*100)

print(not_found)