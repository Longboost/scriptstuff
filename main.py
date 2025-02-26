#!/bin/env python3
from array import array
from struct import unpack
from sys import argv
from typing import TypeVar

from functions import print_function_definitions, print_function_imports
from tables import print_tables
from util import SymbolIds
from variables import write_variables

T = TypeVar('T')

def read_ksm_container(file: bytes) -> list[bytes]:
    header = list(unpack('4siiiiiiiiii', file[:0x2c]))
    assert header[0] == b'KSMR'
    assert header[1] == 0x10300
    assert header[10] == 0
    
    header[10] = len(file) // 4
    
    # god python can be so beautiful
    sections = [file[start * 4:end * 4] for start, end in zip(header[2:], header[3:])]
    return sections

def print_section_0(sections: list[bytes]) -> str:
    section = sections[0]
    arr = array('I', section)
    
    assert len(arr) == 3
    assert arr[0] == 0
    assert arr[1] == 0
    
    out_str = 'section_0:\n'
    out_str += f"  - {hex(arr[2])} # mysterious number\n"
    
    return out_str


def main():
    if len(argv) == 1 or argv[1] == '--help' or argv[1] == '-h':
        print("Sticker Star KSM Script Dumper")
        print("Usage: main.py <input file.bin>")
        return
    
    with open(argv[1], 'rb') as f:
        input_file = f.read()
    
    # predefined symbol ids for expressions (incomplete)
    symbol_ids = SymbolIds()
    
    # TODO: make these only available in expressions and not outside
    # TODO: what is next_function?
    symbol_ids.add('next_function', id=0x3f)
    symbol_ids.add('(', id=0x41)
    symbol_ids.add(')', id=0x42)
    symbol_ids.add('||', id=0x43)
    symbol_ids.add('&&', id=0x44)    
    
    symbol_ids.add('|', id=0x45)
    symbol_ids.add('&', id=0x46)
    symbol_ids.add('^', id=0x47)
    symbol_ids.add('<<', id=0x48)
    symbol_ids.add('>>', id=0x49)
    
    symbol_ids.add('==', id=0x4a)
    symbol_ids.add('!=', id=0x4b)
    symbol_ids.add('>', id=0x4c)
    symbol_ids.add('<', id=0x4d)
    symbol_ids.add('>=', id=0x4e)
    symbol_ids.add('<=', id=0x4f)
    
    symbol_ids.add('%', id=0x52)
    symbol_ids.add('+', id=0x53)
    symbol_ids.add('-', id=0x54)
    symbol_ids.add('*', id=0x55)
    symbol_ids.add('/', id=0x56)
    
    sections = read_ksm_container(input_file)
    
    write_variables(sections, symbol_ids)
    
    # output main yaml
    main_out_str = print_section_0(sections)

    main_out_str += print_function_imports(sections, symbol_ids)
    main_out_str += print_tables(sections, symbol_ids)
    main_out_str += print_function_definitions(sections, symbol_ids)
    
    
    with open(argv[1] + '.yaml', 'w') as f:
        f.write(main_out_str)

if __name__ ==  '__main__':
    main()
