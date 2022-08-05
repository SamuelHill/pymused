#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    circle_of_fifths.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
Circle of fifths and key signature helpers
"""

from typing import Optional, Dict
from core import get_keys_for_value, validate_int, validate_str, SimpleDict
from twelve_tone import ChromaticMapNotation, ALPHABET, ACCIDENTALS, \
                        SOLFEGE, UNICODE_ACC

ALPHA_TO_SOLFEGE = list(zip(ALPHABET.keys(), [s.upper() for s in SOLFEGE]))
ACCIDENTAL_TO_UNI = list(zip(ACCIDENTALS.keys(), UNICODE_ACC.keys()))


def _fancy_replace(key: str, use_reversed: bool, upper_lower: bool,
                   zip_list: list) -> str:
    alpha_change = 'upper' if upper_lower else 'lower'
    for curr, replacement in zip_list:
        curr_name = getattr(curr, alpha_change)()
        if curr_name in key:
            new_name = getattr(replacement, alpha_change)()
            if use_reversed:
                # Only replace one accidental off the back, solves the b vs ♭
                # problem but is limited to this implementation (no doubles)
                rev = ''.join(reversed(key)).replace(curr_name, new_name, 1)
                return ''.join(reversed(rev))
            return key.replace(curr_name, new_name, 1)
    return key


DEFAULT_FIFTHS = {'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'Cb': -7,
                  'F#': 6, 'Gb': -6, 'C#': 7, 'Db': -5, 'Ab': -4, 'Eb': -3,
                  'Bb': -2, 'F': -1}
DEFAULT_MINORS = {'a': 0, 'e': 1, 'b': 2, 'f#': 3, 'c#': 4, 'g#': 5, 'ab': -7,
                  'd#': 6, 'eb': -6, 'a#': 7, 'bb': -5, 'f': -4, 'c': -3,
                  'g': -2, 'd': -1}
UNICODE_FIFTHS = {_fancy_replace(key, True, True, ACCIDENTAL_TO_UNI): value
                  for key, value in DEFAULT_FIFTHS.items()}
UNICODE_MINORS = {_fancy_replace(key, True, False, ACCIDENTAL_TO_UNI): value
                  for key, value in DEFAULT_MINORS.items()}
SOLFEGE_FIFTHS = {_fancy_replace(key, False, True, ALPHA_TO_SOLFEGE): value
                  for key, value in DEFAULT_FIFTHS.items()}
SOLFEGE_MINORS = {_fancy_replace(key, False, False, ALPHA_TO_SOLFEGE): value
                  for key, value in DEFAULT_MINORS.items()}
U_SOLFEGE_FIFTHS = {_fancy_replace(key, True, True, ACCIDENTAL_TO_UNI): value
                    for key, value in SOLFEGE_FIFTHS.items()}
U_SOLFEGE_MINORS = {_fancy_replace(key, True, False, ACCIDENTAL_TO_UNI): value
                    for key, value in SOLFEGE_MINORS.items()}
###############################################################################
ORDER_OF_FLATS = ['B', 'E', 'A', 'D', 'G', 'C', 'F']

S_ORDER_OF_FLATS = [_fancy_replace(key, False, True, ALPHA_TO_SOLFEGE)
                    for key in ORDER_OF_FLATS]
###############################################################################


class CircleOfFifths(object):
    # pylint: disable=too-many-arguments, dangerous-default-value
    def __init__(self, notation: ChromaticMapNotation,
                 fifths: SimpleDict = DEFAULT_FIFTHS,
                 minors: SimpleDict = DEFAULT_MINORS,
                 order_of_flats: list = ORDER_OF_FLATS,
                 upper_lower: bool = True):
        if not isinstance(notation, ChromaticMapNotation):
            raise TypeError('notation must be of type ChromaticMapNotation')
        self.notation = notation
        self.fifths = fifths
        self.minors = minors
        self.order_of_flats = order_of_flats
        self.order_of_sharps = order_of_flats[::-1]
        self.alpha_change = 'upper' if upper_lower else 'lower'
        self.using_unicode = False
        self.current_key_name = None

    ###########################################################################

    @classmethod
    def standard(cls):
        return cls(ChromaticMapNotation.standard())

    @classmethod
    def unicode(cls):
        temp = cls(ChromaticMapNotation.unicode(),
                   UNICODE_FIFTHS, UNICODE_MINORS)
        temp.using_unicode = True
        return temp

    @classmethod
    def solfege(cls):
        return cls(ChromaticMapNotation.solfege(),
                   SOLFEGE_FIFTHS, SOLFEGE_MINORS, S_ORDER_OF_FLATS, False)

    @classmethod
    def s_unicode(cls):
        temp = cls(ChromaticMapNotation.s_unicode(),
                   U_SOLFEGE_FIFTHS, U_SOLFEGE_MINORS, S_ORDER_OF_FLATS, False)
        temp.using_unicode = True
        return temp

    ###########################################################################

    def set_current_key_name(self, new_key_name: str):
        major_check = new_key_name in self.fifths.keys()
        minor_check = new_key_name in self.minors.keys()
        if not any((major_check, minor_check)):
            raise KeyError('key_name not in circle of fifths')
        self.current_key_name = new_key_name

    ###########################################################################

    def _get_upper_lower(self, note_name: str):
        if note_name[-1] == 'b':
            return getattr(note_name[:-1], self.alpha_change)() + 'b'
        return getattr(note_name, self.alpha_change)()

    ###########################################################################

    def parallel(self, key_name: Optional[str] = None):
        if self.current_key_name and not key_name:
            key_name = self.current_key_name
        if key_name in self.fifths.keys():
            return self._get_parallel(key_name, self.minors)
        if key_name in self.minors.keys():
            return self._get_parallel(key_name, self.fifths)
        raise KeyError('key_name not in circle of fifths')

    def _get_parallel(self, key_name: str, major_minor: Dict):
        tonic = self._get_tonic_value(key_name)
        parallels = []
        for key in major_minor:
            if tonic == self._get_tonic_value(key):
                parallels.append(key)
        return parallels[0]

    def _get_tonic_value(self, tonic: str):
        note_name, accidentals, _ = self.notation.process_note(tonic)
        new_name = self._get_upper_lower(note_name)
        note_name = (new_name + accidentals) if accidentals else new_name
        return self.notation.string_to_value(note_name)

    ###########################################################################

    def relative(self, key_name: Optional[str] = None):
        if self.current_key_name and not key_name:
            key_name = self.current_key_name
        if key_name in self.fifths.keys():
            return self._get_key_name_by_num(self.fifths[key_name],
                                             self.minors)
        if key_name in self.minors.keys():
            return self._get_key_name_by_num(self.minors[key_name],
                                             self.fifths)
        raise KeyError('key_name not in circle of fifths')

    def _get_key_name_by_num(self, num_accidentals: int, major_minor: Dict):
        validate_int(num_accidentals, 'num_accidentals')
        if abs(num_accidentals) > 7:
            raise ValueError('No key signatures with more than 7 accidentals')
        return get_keys_for_value(num_accidentals, major_minor)[0]

    ###########################################################################

    def notes_in_key(self, key_name: Optional[str] = None):
        if self.current_key_name and not key_name:
            key_name = self.current_key_name
        accidental, accidentals = self._get_accidentals(key_name)
        notes = list(set(self.order_of_flats) - set(accidentals))
        accidentals = [note + accidental for note in accidentals]
        notes = sorted(notes + accidentals, key=self._get_tonic_value)
        notes = [self._get_upper_lower(note) for note in notes]
        note_index = notes.index(self._get_upper_lower(key_name))
        return notes[note_index:] + notes[:note_index]

    def note_in_key(self, note_name: str, key_name: Optional[str] = None):
        # note_name should be in standard upper_lower for the given notation...
        if self.current_key_name and not key_name:
            key_name = self.current_key_name
        validate_str(note_name, 'note_name')
        return note_name in self.notes_in_key(key_name)

    def get_key_signature(self, key_name: Optional[str] = None):
        if self.current_key_name and not key_name:
            key_name = self.current_key_name
        validate_str(key_name, 'key_name')
        accidental, accidentals = self._get_accidentals(key_name)
        notes = [note + accidental for note in accidentals]
        return [self._get_upper_lower(note) for note in notes]

    def _get_accidentals(self, key_name: str):
        key_value = self._get_key_signature_value(key_name)
        if self.using_unicode:
            accidental = '♯' if key_value >= 0 else '♭'
        accidental = '#' if key_value >= 0 else 'b'
        accidentals = self._get_key_signature_by_value(key_value)
        return accidental, accidentals

    def _get_key_signature_value(self, key_name: str):
        if key_name[0].islower():
            if key_name not in self.minors.keys():
                raise KeyError('key_name not in circle of fifths')
            return self.minors[key_name]
        if key_name not in self.fifths.keys():
            raise KeyError('key_name not in circle of fifths')
        return self.fifths[key_name]

    def _get_key_signature_by_value(self, num_accidentals: int):
        if num_accidentals == 0:
            return []
        if num_accidentals > 0:
            return self.order_of_sharps[:num_accidentals]
        return self.order_of_flats[:abs(num_accidentals)]

###############################################################################


if __name__ == '__main__':
    pass
