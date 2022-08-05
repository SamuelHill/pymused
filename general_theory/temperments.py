#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    temperments.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
Definitions of structures for representing pitch classes and various
tuning systems
"""

from typing import Union
from core import CentsOptions, compare_ratios, Ratio, ratio_to_cents, \
                 TuningStandard, validate_dict, validate_int, validate_ratio, \
                 validate_str, ValidDict


class PitchClass(object):
    def __init__(self, name: str, cents: CentsOptions):
        validate_str(name, 'name')
        if not isinstance(cents, (float, int)):
            raise TypeError('cents must be of type float or int')
        self.name = [name]
        self.cents = float(cents)  # above root...

    def alt_name(self, new_name: str):
        validate_str(new_name, 'new_name')
        self.name.append(new_name)

    def tune_interval(self, root: CentsOptions, octave: int) -> float:
        if not isinstance(root, (float, int)):
            raise TypeError('root must be of type float or int')
        validate_int(octave, 'octave')
        return pow(2, octave) * (root * pow(2, (self.cents / 1200)))


class EqualPitchClass(PitchClass):
    def __init__(self, name: str, division: int, num_divisions: int):
        validate_int(division, 'division')
        self.division = division
        validate_int(num_divisions, 'num_divisions')
        self.divisions = num_divisions
        super().__init__(name, division * (1200 / num_divisions))

    def tune_standard(self, standard: TuningStandard, octave: int) -> float:
        if not isinstance(standard, tuple):
            raise TypeError('standard must be of type tuple(int, int|float)')
        note_standard = isinstance(standard[0], int)
        frequency = isinstance(standard[1], (float, int))
        if not (note_standard and frequency):
            raise TypeError('standard must be of type tuple(int, int|float)')
        octave = octave * self.divisions if octave else 0
        note = self.division + octave
        return pow(2, (note - standard[0]) / 12) * standard[1]


class JustPitchClass(PitchClass):
    def __init__(self, name: str, ratio: Ratio):
        validate_ratio(ratio, 'ratio')
        self.ratio = ratio
        super().__init__(name, ratio_to_cents(self.ratio))


###############################################################################

class TuningSystem(object):
    def __init__(self, name: str):
        validate_str(name, 'name')
        self.name = name
        self.pitch_classes = []

    def from_note_dict(self, notes: ValidDict):
        validate_dict(notes, 'notes')
        for name, interval in notes.items():
            self.new_pitch_class(name, interval)

    def new_pitch_class(self, name: str, interval: CentsOptions):
        self.add_pitch_class(PitchClass(name, interval))

    def add_pitch_class(self, pitch_class: PitchClass):
        if isinstance(pitch_class, PitchClass):
            raise TypeError('pitch_class must be of type PitchClass or it\'s '
                            'subclasses')
        if self.get_pitch_class(pitch_class.name):
            raise ValueError('The value in pitch_class.name is already taken '
                             'in the pitch class list')
        added_alt = self._add_alt_name(pitch_class)
        if not added_alt:
            self.pitch_classes.append(pitch_class)
        self.pitch_classes.sort(key=lambda x: x.cents)

    def get_pitch_class(self, name: str) -> Union[bool, PitchClass]:
        validate_str(name, 'name')
        for pitch_class in self.pitch_classes:
            for pitch_name in pitch_class.name:
                if name == pitch_name:
                    return pitch_class
        return False

    def tune_interval(self, name: str, root: CentsOptions,
                      octave: int) -> float:
        pitch_class = self.get_pitch_class(name)
        if not pitch_class:
            raise ValueError('name not found in pitch_classes')
        return pitch_class.tune_interval(root, octave)

    def _add_alt_name(self, new_pitch_class: PitchClass) -> bool:
        if not isinstance(new_pitch_class, PitchClass):
            raise TypeError('new_pitch_class must be of type PitchClass')
        for index, pitch_class in enumerate(self.pitch_classes):
            if self._same_pitch_class(new_pitch_class, pitch_class):
                self.pitch_classes[index].alt_name(new_pitch_class.name)
                return True
        return False

    def _same_pitch_class(self, pitch1: PitchClass,
                          pitch2: PitchClass) -> bool:
        if self._same_type(pitch1, pitch2, JustPitchClass):
            return compare_ratios(pitch1.ratio, pitch2.ratio)
        if self._same_type(pitch1, pitch2, EqualPitchClass):
            return pitch1.division == pitch2.division
        return pitch1.cents == pitch2.cents

    @staticmethod
    def _same_type(pitch1: PitchClass, pitch2: PitchClass,
                   pitch_class: type) -> bool:
        pitch1_is_type = isinstance(pitch1, pitch_class)
        return pitch1_is_type and isinstance(pitch2, pitch_class)


class JustIntonation(TuningSystem):
    def new_pitch_class(self, name: str, interval: Ratio):
        self.add_pitch_class(JustPitchClass(name, interval))


# for Wendy Carlos
class GeneralTemperment(TuningSystem):
    def __init__(self, name: str, step_size: CentsOptions):
        if not isinstance(step_size, (float, int)):
            raise TypeError('step_size must be of type float or int')
        self.step_size = step_size
        super().__init__(name)

    def new_pitch_class(self, name: str, interval: CentsOptions):
        new_cents = interval * self.step_size
        self.add_pitch_class(PitchClass(name, new_cents))


class EqualTemperment(GeneralTemperment):
    def __init__(self, name: str, divisions: int):
        validate_int(divisions, 'divisions')
        self.divisions = divisions
        super().__init__(name, 1200 / divisions)

    def new_pitch_class(self, name: str, interval: int) -> None:
        new_cents = interval * self.step_size
        self.add_pitch_class(EqualPitchClass(name, interval, new_cents))

    def tune_standard(self, name: str, standard: TuningStandard,
                      octave: int) -> float:
        pitch_class = self.get_pitch_class(name)
        if not pitch_class:
            raise ValueError('name not found in pitch_classes')
        return pitch_class.tune_standard(standard, octave)


###############################################################################

if __name__ == '__main__':
    pass
