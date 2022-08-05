#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    just_intonation.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

from general_theory import JustIntonation, JustNotation
from .chromatic_map import ChromaticMapNotation

# Ideas for JustIntonation accidentals:
#   - http://marsbat.space/pdfs/notation.pdf
#   - http://tonalsoft.com/enc/h/hewm.aspx
HEWM = {'#': (2187, 2048), '^': (33, 32), '>': (64, 63), '+': (81, 80),
        'b': (2048, 2187), 'v': (32, 33), '<': (63, 64), '-': (80, 81)}


class PtolemyCDiatonic(JustIntonation):
    notes = {'C': (1, 1), 'D': (9, 8), 'E': (5, 4), 'F': (4, 3),
             'G': (3, 2), 'A': (5, 3), 'B': (15, 8)}

    def __init__(self):
        super().__init__('Ptolemy C')
        self.from_note_dict(self.notes)

    def tune(self, name: str, root: int = 256, octave: int = 0):
        return self.tune_interval(name, root, octave)


class PtolemyHEWM(JustIntonation):
    # notes = JustNotation(PtolemyCDiatonic.notes.copy(), HEWM).make_tone_row()
    # ^ gives warning, wait til init to show warning
    def __init__(self):
        ptolemy_notation = JustNotation(PtolemyCDiatonic.notes.copy(), HEWM)
        self.notes = ptolemy_notation.make_tone_row()
        super().__init__('Ptolemy HEWM')
        self.from_note_dict(self.notes)

    def tune(self, name: str, root: int = 256, octave: int = 0) -> float:
        return self.tune_interval(name, root, octave)


class PtolemyCChromatic(JustIntonation):
    notes = {'C': (1, 1), 'C#': (16, 15), 'D': (9, 8), 'Eb': (6, 5),
             'E': (5, 4), 'F': (4, 3), 'F#': (45, 32), 'G': (3, 2),
             'Ab': (8, 5), 'A': (5, 3), 'Bb': (9, 5), 'B': (15, 8)}

    def __init__(self):
        super().__init__('Ptolemy 12 C')
        self.from_note_dict(self.notes)

    def tune(self, name: str, root: int = 256, octave: int = 0):
        return self.tune_interval(name, root, octave)


class PtolemyChromatic(JustIntonation):
    notes = PtolemyCChromatic.notes.copy()

    def __init__(self):
        super().__init__('Ptolemy 12 general')
        self.notation = ChromaticMapNotation.standard()
        self.offset = 0
        self.from_note_dict(self.notes)

    def tune(self, name: str, root: int = 256, octave: int = 0) -> float:
        return self.tune_interval(self._enharmonic_name(name), root, octave)

    def _enharmonic_name(self, name: str) -> str:
        position = self.notation.string_to_value(name)
        return list(self.notes.keys())[position + self.offset]

    def transpose(self, new_key: str, sharp_flat: str):
        # NOTE: doesn't shift root for tuning.
        new_notes, offset = self._transpose(new_key, sharp_flat)
        self.offset = offset
        self.pitch_classes = []
        self.from_note_dict(new_notes)

    def _transpose(self, new_key: str, sharp_flat: str):
        position = self.notation.string_to_value(new_key)
        pos_list = list(range(12))[position:] + list(range(12))[:position]
        new_keys = [self.notation.get_note_from_value(pos, sharp_flat)
                    for pos in pos_list]
        return dict(zip(new_keys, self.notes.values())), position


class PythagoreanCTuning(JustIntonation):
    # TODO - generate these ratios... Then how to name?
    notes = {'C': (1, 1), 'Db': (256, 243), 'D': (9, 8), 'Eb': (32, 27),
             # F# and Gb are enharmonic in 12EDO, not here - no enharmonics
             'E': (81, 64), 'F': (4, 3), 'F#': (729, 512), 'Gb': (1024, 729),
             'G': (3, 2), 'Ab': (128, 81), 'A': (27, 16), 'Bb': (16, 9),
             'B': (243, 128)}

    def __init__(self):
        super().__init__('Pythagorean C')
        self.from_note_dict(self.notes)

    def tune(self, name: str, root: int = 256, octave: int = 0):
        return self.tune_interval(name, root, octave)
