#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    scales.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
scales
"""

from intervals import Intervals, UP, DOWN
from core import validate_str
from twelve_tone import ChromaticMapNotation


class Scales(object):
    named_scales = {
        'major':                list('WWHWWWH'),
        'minor':                list('WHWWHWW'),  # natural minor
        'harmonic minor':       'W-H-W-W-H-3H-H'.split('-'),
        'harmonic major':       'W-W-H-W-H-3H-H'.split('-'),
        'melodic minor asc':    list('WHWWWWH'),
        # descending is same as natural minor (reversed order)
        'melodic minor desc':   list('WWHWWHW'),
        'ionian':               list('WWHWWWH'),  # same as major
        'dorian':               list('WHWWWHW'),
        'phrygian':             list('HWWWHWW'),
        'lydian':               list('WWWHWWH'),
        'mixolydian':           list('WWHWWHW'),
        'aeolian':              list('WHWWHWW'),  # same as minor
        'locrian':              list('HWWHWWW'),
        #######################################################################
        'double harmonic':      'H-3H-H-W-H-3H-H'.split('-'),
        # Hungarian minor is the dorian mode of the double harmonic
        'hungarian minor':      'W-H-3H-H-H-3H-H'.split('-'),
        'hungarian major':      '3H-H-W-H-W-H-W'.split('-'),
        # not sure which type... gypsy is not a great name for this
        'gypsy':                'W-H-3H-H-H-W-W'.split('-'),
        # Modes of harmonic minor
        'ukrainian dorian':     'W-H-3H-H-W-H-W'.split('-'),
        'phrygian dominant':    'H-3H-H-W-H-W-W'.split('-'),
        #######################################################################
        # jazz minor is the same as melodic minor asc
        'jazz minor':           list('WHWWWWH'),
        'blues':                'm3-W-H-A1-m3-W'.split('-'),
        'bebop':                'W-W-H-W-W-H-A1-H'.split('-'),
        # in A1-H in the major bebop scale, the A1 is played as an
        # ornamentation/pickup
        'major bebop':          'W-W-H-W-A1-H-W-H'.split('-'),
        'flamenco':             'H-3H-H-W-H-3H-H'.split('-'),
        'neapolitan minor':     'H-W-W-W-H-3H-H'.split('-'),
        'neapolitan major':     list('HWWWWWH'),
        #######################################################################
        'hirajoshi':            'M3-W-H-M3-H'.split('-'),
        'in':                   'H-M3-W-H-M3'.split('-'),
        'insen':                'H-M3-W-m3-W'.split('-'),
        'iwato':                'H-M3-H-M3-W'.split('-'),
        'yo':                   'm3-W-W-m3-W'.split('-'),
        #######################################################################
        'persian':              'H-3H-H-H-W-3H-H'.split('-'),
        'enigmatic':            'H-3H-W-W-W-H-H'.split('-'),
        'harmonics':            'm3-A1-H-W-W-m3'.split('-'),
        'acoustic':             list('WWWHWHW'),
        'augmented':            'm3-A1-m3-A1-m3-H'.split('-'),
        'half diminished':      list('WHWHWWW'),
        'super locrian':        list('HWHWWWW'),  # altered scale..
        'lydian augmented':     list('WWWWHWH'),
        'major locrian':        list('WWHHWWW'),
        #######################################################################
        # octatonic is any 8 note scale, but these are generated
        # when you alternate whole and half steps
        'octatonic whole':      'W-H-W-H-W-A1-W-H'.split('-'),
        'octatonic half':       'H-W-A1-W-H-W-H'.split('-'),
        'prometheus':           'W-W-W-m3-H-W'.split('-'),
        'tritone':              'H-3H-W-A1-m3-W'.split('-'),
        'two semitone tritone': 'H-A1-M3-H-H-M3'.split('-'),
        'whole tone':           list('WWWWWW')
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

    def named_scale(self, scale_name: str, tonic: str, direction: bool = UP,
                    mirrored: bool = False):
        validate_str(scale_name, 'scale_name')
        if scale_name.lower() not in self.named_scales:
            raise ValueError('scale_name is not in dictionary of known scales '
                             'and modes')
        scale = self._steps_to_interval(self.named_scales[scale_name])
        return self.intervals.stack_intervals(tonic, scale, False,  # from_root
                                              direction, mirrored)

    @staticmethod
    def _steps_to_interval(heptatonic: list):
        # steps only applies to heptatonic scales using each scale degree once.
        steps = {'W': 'M2', 'H': 'm2', '3H': 'A2'}
        # allow for mixed intervals, not limiting to heptatonic
        return [steps[step] if step in steps else step for step in heptatonic]

    ###########################################################################

    def chromatic_scale(self, tonic: str, sharp_flat: str,
                        direction: bool = UP, mirrored: bool = False):
        start = self.notation.string_to_value(tonic)
        notes = list(range(12))
        notes = notes[start:] + notes[:start]
        notes.append(start)
        notes = reversed(notes) if not direction else notes
        note_names = [self.notation.get_note_from_value(note, sharp_flat)
                      for note in notes]
        if mirrored:
            return self.intervals.mirror(note_names)
        return note_names

    ###########################################################################

    def major_scale(self, tonic: str, direction: bool = UP,
                    mirrored: bool = False):
        return self.named_scale('major', tonic, direction, mirrored)

    def minor_scale(self, tonic: str, direction: bool = UP,
                    mirrored: bool = False):
        return self.named_scale('minor', tonic, direction, mirrored)

    def harmonic_minor_scale(self, tonic: str, direction: bool = UP,
                             mirrored: bool = False):
        return self.named_scale('harmonic minor', tonic, direction, mirrored)

    # special case...
    def melodic_minor_scale(self, tonic: str):
        starting = self.named_scale('melodic minor asc', tonic)
        return starting + self.named_scale('melodic minor desc',
                                           tonic, DOWN)[1:]

    def ionian_mode(self, tonic: str, direction: bool = UP,
                    mirrored: bool = False):
        return self.major_scale(tonic, direction, mirrored)

    def dorian_mode(self, tonic: str, direction: bool = UP,
                    mirrored: bool = False):
        return self.named_scale('dorian', tonic, direction, mirrored)

    def phrygian_mode(self, tonic: str, direction: bool = UP,
                      mirrored: bool = False):
        return self.named_scale('phrygian', tonic, direction, mirrored)

    def lydian_mode(self, tonic: str, direction: bool = UP,
                    mirrored: bool = False):
        return self.named_scale('lydian', tonic, direction, mirrored)

    def mixolydian_mode(self, tonic: str, direction: bool = UP,
                        mirrored: bool = False):
        return self.named_scale('mixolydian', tonic, direction, mirrored)

    def aeolian_mode(self, tonic: str, direction: bool = UP,
                     mirrored: bool = False):
        return self.minor_scale(tonic, direction, mirrored)

    def locrian_mode(self, tonic: str, direction: bool = UP,
                     mirrored: bool = False):
        return self.named_scale('locrian', tonic, direction, mirrored)

###############################################################################


if __name__ == '__main__':
    scales = Scales.standard()
    print(' '.join(scales.major_scale('C', mirrored=True)))
    print(' '.join(scales.minor_scale('C', mirrored=True)))
    print(' '.join(scales.harmonic_minor_scale('C', mirrored=True)))
    print(' '.join(scales.melodic_minor_scale('C')))
    print()
    print(' '.join(scales.named_scale('blues', 'C')))
    print(' '.join(scales.named_scale('bebop', 'C')))
    print()
    print(' '.join(scales.chromatic_scale('D#', 'sharp', mirrored=True)))
    print(' '.join(scales.chromatic_scale('Ab', 'flat', mirrored=True)))
