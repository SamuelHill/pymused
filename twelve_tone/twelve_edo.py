#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    twelve_edo.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

from general_theory import EqualTemperment
from .chromatic_map import ChromaticMapNotation


class EqualDivisionsOctave12(EqualTemperment):
    def __init__(self, name: str = '12EDO'):
        super().__init__(name, 12)


class MidiStandard(EqualDivisionsOctave12):
    def __init__(self):
        super().__init__('Midi')
        # TODO: add ALL representations in ChromaticMapNotation for more
        # alt_names, giving us translation auto-magically...
        self.from_note_dict(ChromaticMapNotation.standard().make_tone_row())
        self.from_note_dict(ChromaticMapNotation.unicode().make_tone_row())
        self.from_note_dict(ChromaticMapNotation.solfege().make_tone_row())
        self.from_note_dict(ChromaticMapNotation.s_unicode().make_tone_row())
        # 69 = A4 (in scientific pitch notation), midi standard defines 0 as a
        # C one full octave below what the ASPN considers C0. This means that
        # A (9 semitones up from C) needs 5 octaves in midi (5 * 12 = 60) to
        # equal A4. This discrepancy is addressed in scientific_octaves(...).
        # For more see: https://en.wikipedia.org/wiki/Scientific_pitch_notation
        self.tuning_standard = (69, 440)

    def tune(self, name: str, octave: int = 5):
        return self.tune_standard(name, self.tuning_standard, octave)

    def scientific_octaves(self, name: str, octave: int):
        return self.tune(name, octave + 1)
