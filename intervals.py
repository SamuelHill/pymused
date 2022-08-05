#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    intervals.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
intervals
"""
from operator import add, sub
from core import get_keys_for_value, validate_int, validate_str, validate_bool
from twelve_tone import ChromaticMapNotation

UP = True
DOWN = False
OPS = {"+": add, "-": sub, "*": str.__mul__}


class Intervals(object):
    perfect_intervals = {1: 0, 4: 5, 5: 7}
    major_intervals = {2: 2, 3: 4, 6: 9, 7: 11}
    minor_intervals = {2: 1, 3: 3, 6: 8, 7: 10}
    scale_octave = 7

    def __init__(self, notation: ChromaticMapNotation):
        if not isinstance(notation, ChromaticMapNotation):
            raise TypeError('notation must be of type ChromaticMapNotation')
        self.notation = notation
        # NOTE: Relying on note names being in order in the dict, not sorting
        # Note names are needed to map scale degrees (1-7) to note names...
        self.note_names = list(self.notation.notes.keys())

    @classmethod
    def standard(cls):
        return cls(ChromaticMapNotation.standard())

    @classmethod
    def unicode(cls):
        return cls(ChromaticMapNotation.unicode())

    @classmethod
    def solfege(cls):
        return cls(ChromaticMapNotation.solfege())

    ###########################################################################

    @staticmethod
    def validate_interval(interval: str):
        validate_str(interval, 'interval')
        if not set(interval) <= frozenset('AdMmP1234567890'):
            raise ValueError('interval must be made up of a quality (P, M, m, '
                             'A, d) and an interval number (scale degrees)')
        letter_digit = False
        for char in interval:
            if not char.isdigit():
                if letter_digit:
                    raise ValueError('interval must be made of a quality '
                                     'designation followed by the interval '
                                     'number, i.e. letters then numbers')
            else:
                letter_digit = True
        if interval[0] == 'P' and interval.count('P') > 1:
            raise ValueError('interval can only have one P to designate that '
                             'it is perfect')

    @staticmethod
    def validate_interval_list(interval_list: list):
        if not isinstance(interval_list, list):
            raise TypeError('interval_list must be of type list')
        for interval in interval_list:
            try:
                Intervals.validate_interval(interval)
            except ValueError as value_except:
                raise ValueError(f'{interval} is not a valid interval') \
                      from value_except

    ###########################################################################

    def get_interval(self, note1: str, note2: str, octaves: int = 0,
                     direction: bool = UP) -> str:
        value1 = self.notation.string_to_value(note1)
        value2 = self.notation.string_to_value(note2)
        validate_int(octaves, 'octaves')
        value = ((value2 - value1) % 12) + (octaves * 12)
        interval_name = self._get_interval(note1, note2, value)
        if direction:
            return interval_name
        return self.get_inversion(interval_name)

    def _get_interval(self, note1: str, note2: str, value: int) -> str:
        validate_int(value, 'value')
        if value < 0:
            raise ValueError('value must be a positive int')
        if value < 12:
            return self._get_simple_interval_for_notes(note1, note2, value)
        # if value >= 12:  <-- this is implied
        octaves = int(value / 12)
        value = value - (octaves * 12)
        simple = self._get_simple_interval_for_notes(note1, note2, value)
        return simple[:-1] + str(int(simple[-1]) + (octaves * 7))

    def _get_simple_interval_for_notes(self, note1: str, note2: str,
                                       value: int) -> str:
        def expander(interval_val: int, qual: str) -> str:
            oper = '*' if value != interval_val else None
            return OPS[oper](qual, abs(value - interval_val)) if oper else qual
        interval_num = self._simple_interval_number(note1, note2)
        if interval_num in self.perfect_intervals:
            interval_value = self.perfect_intervals[interval_num]
            quality = 'P' if value == interval_value else \
                      'A' if value > interval_value else 'd'
            quality = expander(interval_value, quality)
        else:
            major_int_value = self.major_intervals[interval_num]
            minor_int_value = self.minor_intervals[interval_num]
            quality = 'A' if value > major_int_value else \
                      'M' if value == major_int_value else \
                      'm' if value == minor_int_value else 'd'
            quality = expander(major_int_value, quality) if quality == 'A' \
                else expander(minor_int_value, quality)
        return quality + str(interval_num)

    def _simple_interval_number(self, note1, note2):
        note1_name, _, _ = self.notation.process_note(note1)
        note2_name, _, _ = self.notation.process_note(note2)
        note1_value = self.note_names.index(note1_name) + 1
        note2_value = self.note_names.index(note2_name) + 1
        if note1_value == note2_value:
            return 1
        if note1_value < note2_value:
            return (note2_value - note1_value) + 1
        return 8 - (note1_value - note2_value)

    ###########################################################################

    def get_inversion(self, interval: str):
        self.validate_interval(interval)
        mods, scale_degree = self._split_interval(interval)
        octaves = int(scale_degree / 7)
        scale_degree = scale_degree - (octaves * 7)
        if scale_degree == 1 and octaves == 1:
            scale_degree = 8
        replacements = ('A', 'd') if mods[0] == 'A' else \
                       ('d', 'A') if mods[0] == 'd' else \
                       ('M', 'm') if mods[0] == 'M' else ('m', 'M')
        # NOTE: Octave gets stripped out, always invert to within one octave
        return mods.replace(*replacements) + str(9 - scale_degree)

    @staticmethod
    def _split_interval(interval: str):
        # NOTE: Don't know why I did the index search like this...
        number_index = sum([1 for char in interval if not char.isdigit()])
        return interval[:number_index], int(interval[number_index:])

    ###########################################################################

    def get_semitones(self, interval: str):
        self.validate_interval(interval)
        return self._get_value_for_interval(interval)

    def _get_value_for_interval(self, interval):
        mods, scale_degree = self._split_interval(interval)
        octaves = int(scale_degree / 7)
        scale_degree = scale_degree - (octaves * 7)
        if scale_degree in self.perfect_intervals:
            int_value = self.perfect_intervals[scale_degree]
        elif mods[0] == 'A' or mods[0] == 'M':
            int_value = self.major_intervals[scale_degree]
        elif mods[0] == 'm' or mods[0] == 'd':
            int_value = self.minor_intervals[scale_degree]
        oper = '+' if mods[0] == 'A' else '-' if mods[0] == 'd' else None
        int_value = OPS[oper](int_value, len(mods)) if oper else int_value
        return int_value + (octaves * 12)

    def get_note_by_interval(self, note: str, interval: str,
                             direction: bool = UP):
        validate_bool(direction, 'direction')
        self.validate_interval(interval)
        _, scale_degree = self._split_interval(interval)  # 8 for octave...
        interval_value = self._get_value_for_interval(interval)  # semitones
        # shrink interval_value down to be within one octave...
        interval_value = interval_value - (int(scale_degree / 7) * 12)
        # get scale degree from the list of 'in order' note names...
        note_name, _, _ = self.notation.process_note(note)
        note_position = self.note_names.index(note_name)
        new_note_position = OPS['+' if direction else '-'](note_position,
                                                           (scale_degree - 1))
        new_note_letter = self.note_names[new_note_position % 7]
        if direction:  # Up...
            current_interval = (self.notation.notes[new_note_letter]
                                - self.notation.string_to_value(note)) % 12
            adjust = interval_value - current_interval
        else:
            current_interval = (self.notation.string_to_value(note)
                                - self.notation.notes[new_note_letter]) % 12
            adjust = current_interval - interval_value
        if adjust != 0:
            accidental = get_keys_for_value(-1 if adjust < 0 else 1,
                                            self.notation.accidentals)[0]
            return new_note_letter + (accidental * abs(adjust))
        return new_note_letter

    ###########################################################################

    # Shorter variable names than normal for easier one line statements
    def enharmonic_intervals(self, int1_note1: str, int1_note2: str,
                             int2_note1: str, int2_note2: str,
                             int1_oct: int = 0, int1_direct: bool = UP,
                             int2_oct: int = 0, int2_direct: bool = UP):
        int1 = self.get_interval(int1_note1, int1_note2, int1_oct, int1_direct)
        int2 = self.get_interval(int2_note1, int2_note2, int2_oct, int2_direct)
        semitone_equal = self.get_semitones(int1) == self.get_semitones(int2)
        enharmonics1 = self.notation.enharmonics(int1_note1, int1_note2)
        enharmonics2 = self.notation.enharmonics(int2_note1, int2_note2)
        if all((semitone_equal, enharmonics1, enharmonics2)):
            return True
        return False

    ###########################################################################

    def stack_intervals(self, tonic: str, interval_list: list,
                        from_root: bool = False,
                        direction: bool = UP, mirrored: bool = False):
        self.notation.validate_note(tonic)
        self.validate_interval_list(interval_list)
        validate_bool(mirrored, 'mirrored')
        notes = [tonic]
        for interval in interval_list:
            notes.append(self.get_note_by_interval(tonic if from_root else
                                                   notes[-1], interval,
                                                   direction))
        return self.mirror(notes) if mirrored else notes

    @staticmethod
    def mirror(note_list: list):
        return note_list[:-1] + list(reversed(note_list))

    # TODO: add an identify interval stack function so a list of notes can be
    # passed in and the intervals between each note can be returned OR compared
    # against a list of intervals to be passed in also

###############################################################################


if __name__ == '__main__':
    intervals = Intervals.standard()
    print(intervals.get_interval('C', 'A'))
    print(intervals.get_interval('C', 'A', direction=DOWN))
    print(intervals.get_inversion('M6'))
    print()
    print(intervals.get_note_by_interval('C', 'M6'))
    print(intervals.get_note_by_interval('C', 'm3', direction=DOWN))
    print(intervals.get_note_by_interval('C', 'P1'))
    print()
    print(intervals.get_interval('D', 'D'))
    print(intervals.get_interval('D', 'D', octaves=1))
    print()
    print(intervals.get_semitones('m3'))
    print(intervals.get_semitones('A1'))
