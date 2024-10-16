#!/usr/bin/env python3

from __future__ import annotations

import sys

import numpy as np
import portion as P


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal
    from collections.abc import Sequence


class Stack:

    _stack: list

    def __init__(self) -> None:
        self._stack = []

    def __len__(self) -> int:
        return len(self._stack)

    def push(self, u32_value: int) -> None:
        self._stack.append(u32_value & 0xFFFFFFFF)

    def pop(self) -> int:
        return self._stack.pop()


class _Mem:

    def __init__(self, size: int, endianness: Literal['big', 'little']) -> None:

        assert size > 0, "size must be positive"
        assert size & (size - 1) == 0, "size must be a power of 2"
        assert endianness in ('big', 'little'), "endianness must be 'big' or 'little'"

        self._size = size
        self._mask = size - 1
        self._endianness = sys.intern(endianness)

    def __len__(self) -> int:
        return self._size

    def read8(self, address: int) -> int:
        raise NotImplementedError

    def write8(self, address: int, value: int) -> None:
        raise NotImplementedError

    def read32(self, address: int) -> int:
        return int.from_bytes(bytes([self.read8(address + i) for i in range(4)]), self._endianness)

    def write32(self, address: int, value: int) -> None:
        for i, b in enumerate(value.to_bytes(4, self._endianness)):
            self.write8(address + i, b)


class MemMap(_Mem):

    def __init__(self, mem_map: dict[int: _Mem], endianness: Literal['big', 'little'] = 'big') -> None:

        _map = P.IntervalDict()

        for base, target in mem_map.items():
            assert (len(target) - 1) & base == 0, "target is not aligned"
            interval = P.closedopen(base, base + len(target))
            assert not self._mem[interval], "overlapping memory components"
            _map[interval] = base, target

        super().__init__(1 << (_map.domain().upper - 1).bit_length() if _map else 1, endianness=endianness)

        self._map = _map

    def read8(self, address: int) -> int:

        base, target = self._mem[address & self._mask]
        return target.read8(address - base)

    def write8(self, address: int, value: int) -> None:

        base, target = self._mem[address & self._mask]
        target.write8(address - base, value)


class ROM(_Mem):

    def __init__(self, content: bytes | Sequence[int], *, size: int = None, endianness: Literal['big', 'little'] = 'big', padding: bytes = b'\xff') -> None:

        nbytes = len(content) if isinstance(content, (bytes, bytearray)) else len(content) * 4

        if size is None:
            size = 1 << (nbytes - 1).bit_length()

        else:
            assert nbytes <= size, "content must fit within the size"

        super().__init__(size, endianness=endianness)

        if not isinstance(content, (bytes, bytearray)):
            content = b''.join(v.to_bytes(4, self._endianness) for v in content)

        pad_nbytes = self._size - len(content)
        if pad_nbytes > 0:
            skip = len(content) % len(padding)
            n = (pad_nbytes - 1 + skip) // len(padding) + 1
            content += (padding * n)[skip : skip + pad_nbytes]

        self._mem = np.frombuffer(content, dtype=np.uint8)

    def read8(self, address: int) -> int:
        return self._mem[address & self._mask]

    def write8(self, address: int, value: int) -> None:
        pass


class RAM(_Mem):

    def __init__(self, size: int = 256, *, endianness: Literal['big', 'little'] = 'big') -> None:

        super().__init__(size, endianness=endianness)

        self._mem = np.empty(self._size, dtype=np.uint8)

    def read8(self, address: int) -> int:
        return self._mem[address & self._mask]

    def write8(self, address: int, value: int) -> None:
        self._mem[address & self._mask] = value


teststack = Stack()
teststack.push(1)
teststack.push(100)
teststack.push(-50)
print(teststack.pop())
print(teststack.pop())
