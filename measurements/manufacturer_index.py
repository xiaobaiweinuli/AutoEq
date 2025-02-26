# -*- coding: utf-8 -*-

import os
import sys
import re
from rapidfuzz import fuzz
sys.path.insert(1, os.path.realpath(os.path.join(sys.path[0], os.pardir)))

DIR_PATH = os.path.abspath(os.path.join(__file__, os.pardir))


class ManufacturerIndex:
    def __init__(self):
        with open(os.path.join(DIR_PATH, 'manufacturers.tsv'), encoding='utf-8') as fh:
            manufacturers = fh.read().strip().split('\n')
        self.manufacturers = [m.strip().split('\t') for m in manufacturers]

    def write(self):
        manufacturers = sorted(self.manufacturers, key=lambda x: x[0].lower())
        with open(os.path.join(DIR_PATH, 'manufacturers.tsv'), 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(['\t'.join(manufacturer) for manufacturer in manufacturers]) + '\n')

    def find(self, name):
        matches = []
        for manufacturer in self.manufacturers:
            matches.extend(
                (manufacturer[0], variant)
                for variant in manufacturer
                if re.search(f'^{re.escape(variant)}', name, flags=re.IGNORECASE)
            )

        if not matches:
            return None, None

        # Select longest match
        true_manufacturer, match = sorted(matches, key=lambda x: len(x[1]), reverse=True)[0]
        return true_manufacturer, match

    def replace(self, name):
        manufacturer, match = self.find(name)
        if match is None:
            return name
        return re.sub(f'^{re.escape(match)}', manufacturer, name, flags=re.IGNORECASE)

    def model(self, name):
        manufacturer, match = self.find(name)
        if match is None:
            return None
        # Replace manufacturer with the match
        return re.sub(f'^{match}', '', name, flags=re.IGNORECASE).strip()

    def search(self, name, threshold=80):
        matches = []
        for manufacturer in self.manufacturers:
            for variant in manufacturer:
                # Search with false name
                ratio = fuzz.ratio(variant.lower(), name.lower())
                if ratio > threshold:
                    matches.append((manufacturer[0], ratio))
        return sorted(matches, key=lambda x: x[1], reverse=True)
