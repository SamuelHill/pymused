#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename:    utils.py
# @Author:      Samuel Hill
# @Email:       whatinthesamhill@protonmail.com

"""
Misc. utility functions
"""

from heapq import nsmallest
from itertools import combinations_with_replacement, permutations
from math import log  # for calculating cents
# using itemgetter to sort dicts based on their values, (1, 0)
from operator import itemgetter, truediv
from .validation import OutputTypes, Ratio, validate_int, validate_ratio


def get_keys_for_value(value: OutputTypes, dictionary: dict) -> list:
    """Get a list of the associated key(s) for the given value within the
    given dictionary. Empty list if none found.
    """
    # NOTE: Not doing any validation on the args because this is so generic
    # that given any dictionary and value the function will already 'safely'
    # return an empty list if there were no value matches.
    # NOTE: Relying on dictionaries having a 'static' order,
    # i.e. lists based on keys or valuse etc can be indexed identically.
    indicies = [i for i, (_, v) in enumerate(dictionary.items()) if v == value]
    # "The objects returned by dict.keys() ... are view objects. They provide a
    # dynamic view on the dictionary’s entries..."
    # https://docs.python.org/3.10/library/stdtypes.html#dict-views
    # Basically, keys returns something like a list but not really a list.
    return [list(dictionary.keys())[index] for index in indicies]


def sort_dict_by_value(dictionary: dict) -> dict:
    """Sorts a dict based on its values, accounts for ratios of ints"""
    def _fancy_itemgetter(dict_item):
        value, note_name = itemgetter(1, 0)(dict_item)
        if isinstance(value, (tuple)):
            return (truediv(*value), note_name)
        return value, note_name
    return dict(sorted(dictionary.items(), key=_fancy_itemgetter))


###############################################################################

def wrap_octave(value: int, divisions: int) -> int:
    """Takes a (potentially negative) value and wraps it up to be within the
    number of divisions (i.e. one octave in some EDO system)
    """
    validate_int(value, 'value')
    validate_int(divisions, 'divisions')
    return (value + divisions) % divisions


###############################################################################

# Vector/Fractional math references:
# https://kylegann.com/tuning.html
# http://tonalsoft.com/enc/v/vector.aspx
#     - no monzo notation yet...
# http://marsbat.space/pdfs/notation.pdf
#     - or HEWM/alternatives
def ratio_to_cents(ratio: Ratio) -> float:
    """Converts a Ratio (tuple(int,int)) into it's cents value based on the
    formula:
        ` log(a/b) / log(2) = X cents / 1200 `
    where a and b are the first and second ints in the ratio respectively.
    """
    validate_ratio(ratio, 'ratio')
    return 1200 * log(truediv(*ratio), 2)


def compare_ratios(ratio1: Ratio, ratio2: Ratio) -> bool:
    """Checks if two ratios are equivalent by limiting each to be within one
    octave (1.0 -> 2.0), and testing for equivalence of these limited ratios
    """
    validate_ratio(ratio1, 'ratio1')
    validate_ratio(ratio2, 'ratio2')
    return limit_ratio(ratio1) == limit_ratio(ratio2)


def limit_ratio(ratio: Ratio):
    """Transform a ratio to be within one octave (1 >= ratio <= 2)"""
    validate_ratio(ratio, 'ratio')
    simple_ratio = simplify_ratio(ratio)
    args = (simple_ratio, (2, 1))
    ratio_value = truediv(*simple_ratio)
    if ratio_value < 1.0:
        return limit_ratio(ratio_times(*args))
    if ratio_value > 2.0:
        return limit_ratio(ratio_divid(*args))
    return simple_ratio


def simplify_ratio(ratio: Ratio) -> Ratio:
    """Divids both terms in the ratio by their gcd"""
    # pylint: disable=invalid-name
    def _gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a
    return tuple(i // _gcd(*ratio) for i in ratio)


def ratio_times(ratio1: Ratio, ratio2: Ratio) -> Ratio:
    """fractional multiplication with tuples of ints as the ratios"""
    validate_ratio(ratio1, 'ratio1')
    validate_ratio(ratio2, 'ratio2')
    return (ratio1[0] * ratio2[0], ratio1[1] * ratio2[1])


def ratio_divid(ratio1: Ratio, ratio2: Ratio) -> Ratio:
    """fractional division with tuples of ints as the ratios"""
    # ratio_divid == subtraction or finding the difference between two notes:
    # pythagorean "perfect 5th" has the ratio 3:2, "perfect 4th" has the ratio
    # 4:3, the difference between them is the pythagorean "whole tone" with
    # ratio 9:8, 3/2 ÷ 4/3 == 3/2 * 3/4 == 9/8
    validate_ratio(ratio1, 'ratio1')
    validate_ratio(ratio2, 'ratio2')
    return (ratio1[0] * ratio2[1], ratio1[1] * ratio2[0])

###############################################################################


def _in_octave_range(ratio: tuple):
    return ratio[0] >= ratio[1] and ratio[0] < ratio[1] * 2


# ... ratio_filter=_simple_in_octave_range
# ... ratio_filter=lambda r: _simple_in_octave_range(r,257)
def _simple_in_octave_range(ratio: tuple, cut_off: int = 16):
    return all((_in_octave_range(ratio),
                ratio[0] < cut_off, ratio[1] < cut_off))


PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
# You shouldn't really need past 47 to create the harmonics you want...


def prime_limited_ratios(power_limit: int = 3, num_primes: int = 3,
                         ratio_filter=_in_octave_range):
    primes = PRIMES[:num_primes]  # allow for any int, - or > len...
    # NOTE: Nothing happens if num_primes is negative with abs() > len(PRIMES)
    valid_ratios = set()
    for powers in set(power_perm for combo in
                      combinations_with_replacement(range(-power_limit,
                                                          power_limit + 1),
                                                    len(primes))
                      for power_perm in permutations(combo)):
        new_ratio = [1, 1]  # tuples can't do assignment, but lists can
        for prime, power in zip(primes, powers):
            new_ratio[0 if power > 0 else 1] *= prime ** abs(power)
        if ratio_filter(new_ratio):
            valid_ratios.add((*new_ratio,))  # faster than tuple(...)
    return sorted(list(valid_ratios), key=lambda r: truediv(*r))


def make_cent_ratio_dict(power_limit: int = 3, num_primes: int = 3,
                         _filter=_in_octave_range):
    return {ratio_to_cents(r): r for r in
            prime_limited_ratios(power_limit, num_primes,
                                 ratio_filter=_filter)}


def closest_k(k: int, target: float, cent_ratio_dict: dict):
    return nsmallest(k, cent_ratio_dict.items(),
                     key=lambda v: abs(v[0] - target))

###############################################################################
# def get_prime_factors(value: int):
#     # Simplified from a comment in:
#     # https://paulrohan.medium.com/prime-factorization-of-a-number-in-python
#     # -and-why-we-check-upto-the-square-root-of-the-number-111de56541f
#     prime_factors = []
#     for i in range(2, int(value**0.5) + 3):
#         while value % i == 0:
#             prime_factors.append(i)
#             value = value / i
#     if value > 1:
#         prime_factors.append(int(value))
#     return prime_factors
###############################################################################


if __name__ == '__main__':
    pass
