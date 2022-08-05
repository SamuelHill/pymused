#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    validation.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
Validation/type checking functions
"""

# from typing import Literal  # this is a 3.8 feature
# Python 3.10, we can replace Union with the new union operator |
from typing import Any, Dict, List, Optional, Tuple, Union


# Type aliases...
Ratio = Tuple[int, int]  # out of alpha order for call order
OutputTypes = Union[int, float, Ratio]  # ^ ditto

CentsOptions = Union[float, int]
# NoteParse = (note_name, accidental_text, octave)
NoteParse = Tuple[str, Optional[str], Optional[int]]
# NoteValues = (note_value, accidental_values, octave)
NoteValues = Tuple[OutputTypes, Optional[List[OutputTypes]], Optional[int]]
OptionalFloatList = Optional[List[float]]
OptionalIntList = Optional[List[int]]
OptionalRatioList = Optional[List[Ratio]]
OptionalOutputList = Optional[List[OutputTypes]]
SimpleDict = Dict[str, int]
SortedAccidentals = Dict[str, List[OutputTypes]]
TuningStandard = Tuple[int, CentsOptions]
ValidDict = Dict[str, OutputTypes]

###############################################################################


# Not validating the variable_name string, this is an internal use function...
def validate(data_type: type, variable: Any, variable_name: str):
    if not isinstance(variable, data_type):
        type_name = data_type.__name__
        raise TypeError(f'{variable_name} must be of type {type_name}')

###############################################################################


def validate_int(variable: int, variable_name: str):
    validate(int, variable, variable_name)


def validate_float(variable: float, variable_name: str):
    validate(float, variable, variable_name)


def validate_bool(variable: bool, variable_name: str):
    validate(bool, variable, variable_name)


def validate_str(variable: str, variable_name: str):
    validate(str, variable, variable_name)

###############################################################################


def validate_ratio(ratio: Ratio, ratio_name: str):
    validate(tuple, ratio, ratio_name)
    _validate_ratio(ratio, f'{ratio_name} must be of type tuple(int, int) '
                    'where both ints are positive and non-zero')


def _validate_ratio(ratio: Ratio, error_message: str):
    all_pos_non_zero_ints = all([isinstance(i, int) and i > 0 for i in ratio])
    if len(ratio) != 2 or not all_pos_non_zero_ints:
        raise TypeError(f'{error_message}')


def validate_dict(dictionary: ValidDict, dict_name: str):
    validate(dict, dictionary, dict_name)
    valid_dict_text = 'must be a dict with values of the type int, float, or '\
                      'a "Ratio" (tuple(int, int) where both ints are > 0)'
    if not all([isinstance(key, str) for key in dictionary.keys()]):
        raise TypeError(f'{dict_name} must be a dict with str keys')
    for value in dictionary.values():
        if isinstance(value, tuple):
            _validate_ratio(value, f'{dict_name} {valid_dict_text}')
        elif not any([isinstance(value, int), isinstance(value, float)]):
            raise TypeError(f'{dict_name} {valid_dict_text}')


def dict_with_ints(dictionary: dict):
    return all([isinstance(val, int) for val in dictionary.values()])


def validate_simple_dict(dictionary: SimpleDict, dict_name: str):
    validate(dict, dictionary, dict_name)
    if not all([isinstance(key, str) for key in dictionary.keys()]):
        raise TypeError(f'{dict_name} must be a dict with str keys')
    if not dict_with_ints(dictionary):
        raise TypeError(f'{dict_name} must be a dict with int values')


###############################################################################

# THE ONLY VALIDATION FUNCTION THAT RETURNS ANYTHING
#  -> Literal['flat', 'sharp']
def validate_sharp_flat(sharp_flat: str) -> str:
    validate(str, sharp_flat, 'sharp_flat')
    sharp_flat = sharp_flat.lower()
    if sharp_flat not in ['sharp', 'flat']:
        raise ValueError('sharp_flat must have either the value "sharp" '
                         'or "flat" (capitalization doesn\'t matter)')
    return sharp_flat
