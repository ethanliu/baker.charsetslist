#!/usr/bin/env python
#
# version: 0.1.0
# autor: Ethan Liu
#
# convert lexicon csv to sqlite db

import argparse
import importlib
import sys, os
import csv
import sqlite3
from tqdm import tqdm

uu = importlib.import_module("lib.util")

def performImport(cursor, inputPath):
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("BEGIN TRANSACTION")

    filename = os.path.basename(inputPath)

    with open(inputPath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = '\t', quotechar = None)
        for chunk in uu.chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                phrase = (row[0] or '').strip()
                weight = row[1] or 0
                pinyin = uu.stripAccents(row[2] or '').replace('，', '').strip()

                if not phrase or len(phrase) < 2:
                    continue

                query = "INSERT OR IGNORE INTO lexicon (phrase, weight, pinyin, category_id) VALUES (:phrase, :weight, :pinyin, 0)"
                args = {'phrase': phrase, 'weight': weight, 'pinyin': pinyin}
                cursor.execute(query, args)

    cursor.execute("COMMIT TRANSACTION")
    cursor.execute('VACUUM')

def main():
    argParser = argparse.ArgumentParser(description='Convert lexicon csv to sqlite db file')
    argParser.add_argument('-i', '--input', type = str, required = True, help='The lexicon csv file path')
    argParser.add_argument('-o', '--output', type = str, required = True, help='The sqlite file path')
    # argParser.add_argument('--readme', type = str, help='The readme file path')

    args = argParser.parse_args()
    # print(args, len(sys.argv))
    # sys.exit(0)

    if not args.input or not os.path.exists(args.input):
        print(f"Input file missing or not found: {args.input}")
        sys.exit(0)

    if not args.output:
        print(f"Output file path missing")
        sys.exit(0)

    if os.path.exists(args.output):
        # print(f"Remove existing file: {args.output}")
        os.remove(args.output)


    db = sqlite3.connect(args.output)
    cursor = db.cursor()

    # cursor.execute("CREATE TABLE pinyin (`pinyin` CHAR(255) UNIQUE NOT NULL)")
    cursor.execute("CREATE TABLE `lexicon` (`phrase` CHAR(255) NOT NULL, `pinyin` CHAR(255) DEFAULT NULL, `weight` INTEGER DEFAULT 0, `category_id` INTEGER DEFAULT 0, UNIQUE(`phrase`, `pinyin`))")

    performImport(cursor, args.input)
    db.commit()

    # if args.readme:
    #     if not os.path.exists(args.readme):
    #         print(f"File not found: {args.readme}")
    #         sys.exit(0)

    db.close()

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupt by user")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    # except BaseException as err:
