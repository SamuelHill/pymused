#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    chromatic_map.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

from typing import Optional
from core import SimpleDict
from general_theory import EDONotation

###############################################################################
#                                  Standard:                                  #
###############################################################################
ALPHABET = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
ACCIDENTALS = {'#': 1, 'b': -1, 'n': 0}
UNICODE_ACC = {'♯': 1, '♭': -1, '♮': 0}

###############################################################################
#                                Other regions:                               #
###############################################################################
SOLFEGE = {'do': 0, 're': 2, 'mi': 4, 'fa': 5, 'sol': 7, 'la': 9, 'ti': 11}
NEO_LATIN = {'do': 0, 're': 2, 'mi': 4, 'fa': 5, 'sol': 7, 'la': 9, 'si': 11}
###############################################################################
GERMAN_ALPHABET = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9,
                   'B': 10, 'H': 11}  # H flat is B, ChromaticMap doesn't
# distinguish here... Needs special case to not use B flat, B sharp or H flat
# TODO: add alpha-accidental pairs to ignore? only for tone row, to much extra
# work to add that condition to general notation for now
###############################################################################
# Enharmonics included, no 'accidentals': (could rewrite both with accidentals)
DUTCH = {'C': 0, 'Cis': 1, 'Des': 1, 'D': 2, 'Dis': 3, 'Es': 3, 'E': 4,
         'F': 5, 'Fis': 6, 'Ges': 6, 'G': 7, 'Gis': 8, 'As': 8, 'A': 9,
         'Ais': 10, 'Bes': 10, 'B': 11}
JAPANESE = {'ハ': 0, '嬰ハ': 1, '変ニ': 1, 'ニ': 2, '嬰ニ': 3,
            '変ホ': 3, 'ホ': 4, 'ヘ': 5, '嬰へ': 6, '変ト': 6,
            'ト': 7, '嬰ト': 8, '変イ': 8, 'イ': 9, '嬰イ': 10,
            '変ロ': 10, 'ロ': 11}
###############################################################################
# Naturally has no enharmonics:
HINDUSTANI = {'सा': 0, 'रे॒': 1, 'रे': 2, 'ग॒': 3,
              'ग': 4, 'म': 5, 'म॑': 6, 'प': 7,
              'ध॒': 8, 'ध': 9, 'नि॒': 10, 'नि': 11}
BENGALI = {'সা': 0, 'ঋ': 1, 'রে': 2, 'জ্ঞ': 3,
           'গ': 4, 'ম': 5, 'হ্ম': 6, 'প': 7,
           'দ': 8, 'ধ': 9, 'ণ': 10, 'নি': 11}
###############################################################################


class ChromaticMapNotation(EDONotation):
    def __init__(self, notes: SimpleDict, accidentals: Optional[SimpleDict],
                 use_octaves: bool = True):
        super().__init__(notes, accidentals, use_octaves, 12)
        # NOTE: using default value for; simple_accidental: bool = False

    @classmethod
    def standard(cls):
        return cls(ALPHABET, ACCIDENTALS)

    @classmethod
    def unicode(cls):
        return cls(ALPHABET, UNICODE_ACC)

    @classmethod
    def solfege(cls):  # fixed do, not movable - can always add offsets...
        return cls(SOLFEGE, ACCIDENTALS)

    @classmethod
    def s_unicode(cls):
        return cls(SOLFEGE, UNICODE_ACC)

    ###########################################################################

    @classmethod
    def custom(cls, notes: SimpleDict, use_octaves: bool = True):
        return cls(notes, None, use_octaves)

    @classmethod
    def custom_alpha(cls, notes: SimpleDict, use_octaves: bool = True):
        return cls(notes, ACCIDENTALS, use_octaves)

    @classmethod
    def custom_unicode(cls, notes: SimpleDict, use_octaves: bool = True):
        return cls(notes, UNICODE_ACC, use_octaves)

###############################################################################


if __name__ == '__main__':
    piano = ChromaticMapNotation.standard()
    print(' '.join([piano.get_note_from_value(i, 'sharp')
                    for i in range(12)] +
                   [piano.get_note_from_value(i, 'flat')
                    for i in range(12, -1, -1)]))
