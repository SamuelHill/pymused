#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    notation.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
General notation interpreter for musical systems. Allows generic definition
of notes and accidentals with accociated values (pitch class, tuning ratio)
"""

import re
from typing import Optional, Union
from warnings import warn
from core import dict_with_ints, NoteParse, NoteValues, OptionalFloatList, \
                 OptionalIntList, OptionalRatioList, OptionalOutputList, \
                 OutputTypes, Ratio, ratio_times, ratio_to_cents, \
                 SortedAccidentals, validate_bool, validate_dict, \
                 validate_int, validate_str, ValidDict, wrap_octave, \
                 simplify_ratio, ratio_divid, validate_sharp_flat, \
                 get_keys_for_value, SimpleDict, validate_simple_dict, \
                 limit_ratio, sort_dict_by_value


class GeneralNotation(object):
    def __init__(self, notes: ValidDict,
                 accidentals: Optional[ValidDict] = None,
                 use_octaves: bool = True, divisions: Optional[int] = None,
                 simple_accidental: bool = False):
        validate_dict(notes, 'notes')
        self.notes = sort_dict_by_value(notes)
        #######################################################################
        if accidentals:
            validate_dict(accidentals, 'accidentals')
            accidents_int = dict_with_ints(accidentals)
        self.accidentals = sort_dict_by_value(accidentals)
        self.sorted_accidentals = None
        if self.accidentals:
            self.sorted_accidentals = self._sort_accidentals()
        # For validating that a note can't have multiple types of accidentals
        validate_bool(simple_accidental, 'simple_accidental')
        self.simple_accidental = simple_accidental
        #######################################################################
        validate_bool(use_octaves, 'use_octaves')
        self.use_octaves = use_octaves
        # EDO divisions (int based pitch classes) use for getting note values
        if (dict_with_ints(notes) or accidents_int) and divisions:
            validate_int(divisions, 'divisions')
        self.divisions = divisions
        #######################################################################
        # Regex building for note validation, first the character set...
        # valid_notes = list(self.notes.keys())
        note_names = [(note.upper(), note.title(), note.lower())
                      for note in self.notes.keys()]
        flat_names = [name for options in note_names for name in options]
        valid_notes = list(dict.fromkeys(flat_names))  # removing duplicates
        valid_accidental = list()
        if self.accidentals:
            valid_accidental = list(self.accidentals.keys())
        # When using octaves, not looking more than 20 octaves either direction
        if '-' not in self.accidentals.keys() and self.use_octaves:
            octaves = list([str(x) for x in range(-20, 21)])
        elif self.use_octaves:
            octaves = list([str(x) for x in range(21)])
        octaves = octaves if self.use_octaves else list()
        self.valid_chars = frozenset(valid_notes + valid_accidental + octaves)
        #######################################################################
        # And then we build the regex parser
        note_groups = '|'.join([f'({note})' for note in valid_notes])
        # We re.escape(key) in case an accidental is a special symbol
        accident_reg = f'({"|".join(map(re.escape, accidentals.keys()))})*' \
            if accidentals else ''
        negative_octaves = '-' not in self.accidentals.keys()
        if self.use_octaves and not negative_octaves:
            warn('Octaves can\'t be negative when the \'-\' character is also '
                 'being used as an accidental')
        octaves_reg = '(-?\\d*)' if self.use_octaves and negative_octaves \
            else '(\\d*)' if self.use_octaves else ''
        regex = f'({note_groups}){accident_reg}{octaves_reg}'
        self.note_parser = re.compile(f'({regex})')

    ###########################################################################
    # Tuning systems need all notes in tone row, i.e. nominals for each pitch
    # class within one octave.
    def make_tone_row(self):
        all_notes = [note + acc for acc in list(self.accidentals.keys())
                     for note in list(self.notes.keys())]
        all_notes += list(self.notes.keys())
        new_dict = dict((new_note, self.string_to_value(new_note))
                        for new_note in all_notes)
        return sort_dict_by_value(new_dict)

    ###########################################################################

    def enharmonics(self, note1: str, note2: str) -> bool:
        return self.string_to_value(note1) == self.string_to_value(note2)

    def string_to_value(self, note: str) -> OutputTypes:
        value, accidentals, octave = self.string_to_values(note)
        # NOTE: Behavior of naturals is not what you might expect - naturals
        # should negate prior accidentals - whereas now naturals are just 0
        # and get added on like any other accidental.
        notes_type = self._get_same_type(value, accidentals)
        if notes_type is int:
            return self._int_process(value, accidentals, octave)
        if notes_type is float:
            return self._float_process(value, accidentals, octave)
        if notes_type is tuple:
            return self._tuple_process(value, accidentals, octave)
        return self._cents_process(value, accidentals, octave)

    @staticmethod
    def _get_same_type(value: OutputTypes,
                       accidentals: OptionalOutputList) -> Union[type, bool]:
        if accidentals:
            if all([isinstance(acc, type(value)) for acc in accidentals]):
                return type(value)
            return False
        return type(value)

    def _int_process(self, value: int, accidentals: OptionalIntList,
                     octave: Optional[int]) -> int:
        accidentals = sum(accidentals) if accidentals else 0
        if self.use_octaves and self.divisions:
            octave_mod = octave * self.divisions if octave else 0
            return value + accidentals + octave_mod
        if self.divisions:
            return wrap_octave(value + accidentals, self.divisions)
        return value + accidentals

    def _float_process(self, value: float,
                       accidentals: OptionalFloatList,
                       octave: Optional[int]) -> float:
        accidentals = sum(accidentals) if accidentals else 0.0
        if self.use_octaves:
            octave_mod = octave * 1200.0 if octave else 0.0
            return value + accidentals + octave_mod
        return value + accidentals

    @staticmethod
    def _tuple_process(value: Ratio,
                       accidentals: OptionalRatioList,
                       octave: Optional[int]) -> Ratio:
        new_ratio = simplify_ratio(value)
        if accidentals:
            for mod in accidentals:
                new_ratio = simplify_ratio(ratio_times(new_ratio, mod))
        if octave:
            args = (new_ratio, (2**abs(octave), 1))
            if octave < 0:
                new_ratio = simplify_ratio(ratio_divid(*args))
            else:
                new_ratio = simplify_ratio(ratio_times(*args))
        return new_ratio

    def _cents_process(self, value: OutputTypes,
                       accidentals: OptionalOutputList,
                       octave: Optional[int]) -> float:
        mods = sum(self._get_cents(acc)
                   for acc in accidentals) if accidentals else 0.0
        octave_mod = octave * 1200.0 if (self.use_octaves and octave) else 0.0
        return self._get_cents(value) + mods + octave_mod

    def _get_cents(self, value: OutputTypes) -> float:
        if isinstance(value, tuple):
            return ratio_to_cents(value)
        if isinstance(value, int):
            return value * (1200 / self.divisions)
        return value

    ###########################################################################

    def string_to_values(self, note: str) -> NoteValues:
        note_name, accidental_text, octave = self.process_note(note)
        note_value = self.notes[note_name]
        accidental_values = self._convert_accidentals(accidental_text)
        return (note_value, accidental_values, octave)

    def process_note(self, note: str) -> NoteParse:
        validate_str(note, 'note')
        note_string = self.validate_note(note)
        octave, note_string = self._get_octave(note_string)
        octave = int(octave) if octave else octave
        note_name = ''
        for name in self.notes:
            # NOTE: The options below are in place to allow different styles of
            # naming to still return the canonical note name. Ex: major and
            # minor key names often are differentiated by upper and lower case,
            # and in the case of solfege or some other systems title case may
            # be more appropriate.
            for option in (name.upper(), name.title(), name.lower()):
                # NOTE: Getting the longer name for any note lists that include
                # accidentals. If a system has note names that can be confused
                # with it's accidentals, or with other note names, this current
                # system won't work. (e.g. tonic and supertonic as note names,
                # lowercase 'b' as a note name and as the flat sign)
                if option in note_string and len(option) > len(note_name):
                    note_name = name
        accidental_text = note_string[len(note_name):]
        accidental_text = None if accidental_text == '' else accidental_text
        return (note_name, accidental_text, octave)

    def _get_octave(self, string: str):
        octave = None
        while string[-1].isdigit():
            octave, string = self._octave_digits(string, octave)
        if '-' not in self.accidentals.keys() and string[-1] == '-':
            octave, string = string[-1] + octave, string[:-1]
        return octave, string

    def _octave_digits(self, string: str, octave: Optional[str]):
        if string[-1].isdigit() and self.use_octaves:
            octave = string[-1] + (octave if octave else '')
            return octave, string[:-1]
        return octave, string

    def _convert_accidentals(self, accidental_text:
                             Optional[str]) -> OptionalOutputList:
        if not self.accidentals or not accidental_text:
            return None
        # NOTE: Assumes that an accidental is only one character...
        return [self.accidentals[accidental] for accidental in accidental_text]

    ###########################################################################

    def validate_note(self, note: str) -> str:
        note_string = ''.join(note.split())
        self._is_valid_note_string(note_string)
        if self.simple_accidental and self.sorted_accidentals:
            self._limit_accidentals(note_string)
        return self._parse_note(note_string)

    def _is_valid_note_string(self, note_string: str):
        valid_note_set = self.valid_chars
        non_single_letter = any([val for val in self.valid_chars
                                 if len(val) > 1 and not
                                 val.strip('-').isnumeric()])
        if non_single_letter:
            valid_note_set = set(char for valid in
                                 [val for val in self.valid_chars
                                  if val in note_string]
                                 for char in valid)
        if not set(note_string) <= valid_note_set:
            raise ValueError('note_string must be made up of a valid note '
                             'name (letter, symbol, word, etc.), optional '
                             'accidentals, and optional octave indicator')

    def _limit_accidentals(self, note_string: str) -> None:
        has_sharps = self._accidental_in_string(note_string, 'sharp')
        has_flats = self._accidental_in_string(note_string, 'flat')
        has_naturals = self._accidental_in_string(note_string, 'natural')
        if sum([has_sharps, has_flats, has_naturals]) > 1:
            raise ValueError('Notes may only have one type of accidental')

    def _accidental_in_string(self, note: str, group: str) -> bool:
        return any([acc in note for acc in self.sorted_accidentals[group]])

    def _parse_note(self, note_string: str) -> str:
        parse = self.note_parser.match(note_string)
        if not parse:
            raise ValueError('Notes must be of the form <valid note name>, '
                             'optionally followed by any number of'
                             '<accidental>s, optionally followed by an octave '
                             'number (0-9)')
        return parse.group()

    ###########################################################################

    def try_note_from_value(self, value: OutputTypes, sharp_flat: str) -> str:
        if not isinstance(value, (int, float, tuple)):
            raise TypeError('value must be of type OutputTypes')
        sharp_flat = validate_sharp_flat(sharp_flat)
        nominals = get_keys_for_value(value, self.notes)
        if nominals:
            return nominals[0]
        for accidental in self.sorted_accidentals[sharp_flat]:
            adjust = self.accidentals[accidental]
            if isinstance(adjust, type(value)):
                if isinstance(value, (int, float)):
                    new_value = value - adjust
                else:
                    new_value = simplify_ratio(ratio_divid(value, adjust))
            else:
                new_value = self._get_cents(value) - self._get_cents(adjust)
            nominals = get_keys_for_value(new_value, self.notes)
            if nominals:
                return nominals[0] + accidental
        return False

    def _sort_accidentals(self) -> SortedAccidentals:
        # filter naturals out into their own group to not polute sharps and
        # flats, also separate sharps and flats for situational usage
        sorted_accidentals = {'sharp': [], 'flat': [], 'natural': []}
        for accidental, value in self.accidentals.items():
            if isinstance(value, (int, float)):
                if value > 0:
                    sorted_accidentals['sharp'].append(accidental)
                elif value < 0:
                    sorted_accidentals['flat'].append(accidental)
                elif value == 0:  # else...
                    sorted_accidentals['natural'].append(accidental)
            else:
                if value[0] > value[1]:
                    sorted_accidentals['sharp'].append(accidental)
                elif value[0] < value[1]:
                    sorted_accidentals['flat'].append(accidental)
                elif value[0] == value[1]:
                    sorted_accidentals['natural'].append(accidental)
        return sorted_accidentals


###############################################################################
class EDONotation(GeneralNotation):
    def __init__(self, notes: SimpleDict, accidentals: Optional[SimpleDict],
                 use_octaves: bool = True, num_divisions: int = 12,
                 simple_accidental: bool = False):
        validate_simple_dict(notes, 'notes')
        super().__init__(notes, accidentals, use_octaves,
                         num_divisions, simple_accidental)

    def simplify(self, note: str, sharp_flat: str) -> str:
        value, mods, octave = self.string_to_values(note)
        octave = str(octave) if octave else ''
        nominal_value = wrap_octave(value + sum(mods), self.divisions)
        return self.get_note_from_value(nominal_value, sharp_flat) + octave

    def get_note_from_value(self, value: int, sharp_flat: str) -> str:
        validate_int(value, 'value')
        octaves = int(value / self.divisions)
        new_value = value - (octaves * self.divisions)
        note = self.try_note_from_value(new_value, sharp_flat)
        if self.use_octaves:
            return note + str(octaves)
        return note

    ###########################################################################

    def translate_values(self, values: list, sharp_flat: str) -> str:
        return list(self.get_note_from_value(value, sharp_flat)
                    for value in values)

    def translate_notation(self, notes: list, other_notation,  # : EDONotation
                           sharp_flat: str) -> str:
        return self.translate_values(list(other_notation.string_to_value(note)
                                          for note in notes), sharp_flat)

    def transpose(self, notes: list, transpose_by: int,
                  sharp_flat: str) -> str:
        transposed = list(self.string_to_value(note) + transpose_by
                          for note in notes)
        return self.translate_values(transposed, sharp_flat)

    ###########################################################################

    def make_tone_row(self) -> SimpleDict:
        alphabet = self.notes.copy()
        if self.accidentals:
            spaces = list(range(self.divisions))
            for note in self.notes:
                spaces.remove(self.notes[note])
            for space in spaces:
                try_flat = self._apply_accidental(space, 'flat')
                if try_flat:
                    alphabet[try_flat] = space
                try_sharp = self._apply_accidental(space, 'sharp')
                if try_sharp:
                    alphabet[try_sharp] = space
            return sort_dict_by_value(alphabet)
        return alphabet

    def _apply_accidental(self, space: int, sharp_flat: str) -> str:
        # TODO: check [0]
        for accidental in self.sorted_accidentals[sharp_flat][0]:
            adjust = self.accidentals[accidental]
            new_note_value = wrap_octave(space + adjust, self.divisions)
            notes = get_keys_for_value(new_note_value, self.notes)
            if notes:
                return notes[0] + accidental


###############################################################################
class JustNotation(GeneralNotation):
    def __init__(self, notes: ValidDict, accidentals: Optional[ValidDict],
                 use_octaves: bool = True, limit_notes_to_octave: bool = True):
        if limit_notes_to_octave:
            notes = dict((k, limit_ratio(v)) for k, v in notes.items())
        super().__init__(notes, accidentals, use_octaves, None, False)
        self.limit_to_octave = limit_notes_to_octave

    def make_tone_row(self):
        new_dict = super().make_tone_row()
        if self.limit_to_octave:
            new_dict = dict((k, limit_ratio(v)) for k, v in new_dict.items())
        return sort_dict_by_value(new_dict)


###############################################################################

if __name__ == '__main__':
    pass
