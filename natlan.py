#!/usr/bin/env python3

from __future__ import annotations

import numpy as np
import sounddevice as sd

from fractions import Fraction
from math import ceil, floor, isclose
from numbers import Rational

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections.abc import Sequence
    from numbers import Real
    from typing import Literal


FREQ = 48000


def silence(sample_duration: Real) -> np.ndarray:

    return np.zeros(round(sample_duration * FREQ), dtype=np.float32)


def sinewave(sample_duration: Real, frequency: Real) -> np.ndarray:

    return np.sin(np.linspace(0.0, 2 * np.pi * sample_duration * frequency, num = round(sample_duration * FREQ), endpoint=False, dtype=np.float32))


def envelope(sample_duration: Real, on_duration: Real = 0.2, attack_time: Real = 0.05, decay_time: Real = 0.4, sustain_level: Real = 0.5, release_time: Real = 0.4) -> np.ndarray:

    if on_duration <= 0:
        return silence(sample_duration)

    if on_duration <= attack_time:
        return schedule(sample_duration, [
            ('linear', on_duration, last_level := on_duration / attack_time),
            ('linear', on_duration + release_time * (last_level / sustain_level), 0),
        ])

    t_sustain = attack_time + decay_time
    if on_duration <= t_sustain:
        return schedule(sample_duration, [
            ('linear', attack_time, 1),
            ('linear', on_duration, last_level := 1 - (1 - sustain_level) * (on_duration - attack_time) / decay_time),
            ('linear', on_duration + release_time * (last_level / sustain_level), 0),
        ])

    return schedule(sample_duration, [
        ('linear', attack_time, 1),
        ('linear', t_sustain, sustain_level),
        ('linear', on_duration, sustain_level),
        ('linear', on_duration + release_time, 0),
    ])


def schedule(sample_duration: Real, sched: Sequence[tuple[Literal['ramp', 'lin', 'linear'], Real, Real]], start_level: Real = 0) -> np.ndarray:

    result = np.empty(round(sample_duration * FREQ), dtype=np.float32)

    t1, left, i1 = 0, 0, 0
    level = start_level
    for typ, t2, new_level in sched:
        if i1 >= len(result):
            break

        right = t2 * FREQ

        if t2 == t1 or not isinstance(t1, Rational) and not isinstance(t2, Rational) and abs(t2 - t1) < 0.0005:
            level = new_level
            left = right
            continue

        assert t2 > t1

        i2 = min(ceil(right), len(result))
        if i2 <= i1:
            level = new_level
            left, t1 = right, t2
            continue

        match typ:
            case 'ramp' | 'lin' | 'linear':
                result[i1:i2] = np.linspace(
                    (i1 - left) / (right - left) * (new_level - level) + level,
                    (i2 - left) / (right - left) * (new_level - level) + level,
                    num=i2 - i1, endpoint=False, dtype=np.float32
                )
            case _:
                raise NotImplementedError(f"Unknown curve type {typ!r}")

        level = new_level
        left, t1, i1 = right, t2, i2

    if i1 < len(result):
        result[i1:] = new_level

    return result


def main() -> None:

    song = silence(5 * 60)

    note = 0.5 * sinewave(4.0, 440.0) * envelope(4.0)
    sd.play(note)

    from time import sleep
    sleep(5)


if __name__ == '__main__':
    main()
