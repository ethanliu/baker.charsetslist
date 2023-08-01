#!/usr/bin/env python
#
# version: 0.0.1
# autor: Ethan Liu
#
# convert McBopomofo BPMFMappings.txt to csv

import argparse
import importlib
import sys, os
import csv
# import sqlite3
# import multiprocessing
import pinyin as tp
from tqdm import tqdm

uu = importlib.import_module("lib.util")

# _dir_ = uu.dir(__file__)
# workers = 2 * multiprocessing.cpu_count()
# print(f"num of workers: \(workers)")

def parse(inputPath, outputPath):
    filename = os.path.basename(inputPath)
    contents = ""
    # _dir_ = uu.dir(__file__)
    # pool = multiprocessing.Pool(workers)
    with open(inputPath) as fp:
        reader = csv.reader(fp, delimiter = "\t")
        for chunk in uu.chunks(reader, max = 0):
            for row in tqdm(chunk, desc = f"{filename}[]", unit = 'MB', unit_scale = True, ascii = True):
                phrase = uu.trim(row[0] or '')
                if not phrase:
                    continue

                weight = (row[1:2] or ('0', ''))[0]
                # pinyin = translate(phrase)
                pinyin = tp.get(phrase, format = "strip", delimiter = "")

                if pinyin == phrase:
                    pinyin = ''

                contents += f"{phrase}\t{weight}\t{pinyin}\n"

    with open(outputPath, 'w') as fp:
        fp.write(contents)
        fp.close()

def main():
    argParser = argparse.ArgumentParser(description='McBopomofo tookit')
    argParser.add_argument('-i', '--input', help='Original csv file path')
    argParser.add_argument('-o', '--output', default='', help='Lexicon format csv file path')

    args = argParser.parse_args()
    # print(args, len(sys.argv))

    if not os.path.exists(args.input):
        sys.exit(f"File not found: {args.input}")

    parse(args.input, args.output)

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
