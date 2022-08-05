#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    chords.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
chords
"""

from intervals import Intervals, UP
from core import validate_str
from twelve_tone import ChromaticMapNotation


class Chords(object):
    # default to stacked interval notation, can process from root
    named_chords = {
        'major': ('M3', 'm3'),
        'minor': ('m3', 'M3'),
    }

    def __init__(self, notation: ChromaticMapNotation):
        if not isinstance(notation, ChromaticMapNotation):
            raise TypeError('notation must be of type ChromaticMapNotation')
        self.notation = notation
        self.intervals = Intervals(notation)

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

    def named_chord(self, chord_name: str, tonic: str,
                    direction: bool = UP, mirrored: bool = False):
        validate_str(chord_name, 'chord_name')
        if chord_name.lower() not in self.named_chords:
            raise ValueError('chord_name is not in dictionary of known chords')
        return self.chord_stacked(tonic, self.named_chords[chord_name],
                                  direction, mirrored)

    def chord_stacked(self, tonic: str, interval_list: list,
                      direction: bool = UP, mirrored: bool = False):
        return self.intervals.stack_intervals(tonic, interval_list, False,
                                              direction, mirrored)

    # UNUSED
    def chord_from_root(self, tonic: str, interval_list: list,
                        direction: bool = UP, mirrored: bool = False):
        return self.intervals.stack_intervals(tonic, interval_list, True,
                                              direction, mirrored)

    ###########################################################################

    def major(self, tonic: str, direction: bool = UP, mirrored: bool = False):
        return self.named_chord('major', tonic, direction, mirrored)

    def minor(self, tonic: str, direction: bool = UP, mirrored: bool = False):
        return self.named_chord('minor', tonic, direction, mirrored)

###############################################################################


if __name__ == '__main__':
    pass
