from array import array
from dataclasses import dataclass
from sys import argv

def read_string(section: bytes, offset_words: int) -> str:
    buffer = section[offset_words * 4:]
    bytelen = buffer.index(0)
    return str(buffer[:bytelen], 'utf-8')

@dataclass
class Var:
    name: str | None
    
    id: int
    status: int
    flags: int
    reference_value: int | str

def read_variable_defs(section: bytes) -> list[Var]:
    arr = enumerate(array('I', section))
    
    count = next(arr)[1]
    variables = []
    
    for i, value in arr:
        id = next(arr)[1]
        raw_status = next(arr)[1]
        reference_value = next(arr)[1]
        
        status = raw_status & 0xffffff
        flags = raw_status >> 24
        
        if value == 0xFFFFFFFF:
            name = read_string(section, i + 5)
            
            for _ in range(next(arr)[1]):
                next(arr)
        else:
            assert value == 0
            name = None
        
        if status == 3:
            assert reference_value == 0
            j, word_len = next(arr)
            
            reference_value = read_string(section, j + 1)
            
            for _ in range(word_len):
                next(arr)
        
        variables.append(Var(name, id, status, flags, reference_value))
    
    assert len(variables) == count
    return variables

VAR_STATUS_NAMES = {
    4: 'Alloc',
    5: 'UserVar',
    0xd: 'QueuedFree',
    0xe: 'Uninitialized',
}

def print_var(var: Var) -> str:
    if isinstance(var.reference_value, str):
        reference_value = repr(var.reference_value)
    elif var.reference_value != 0:
        reference_value = f"0x{var.reference_value:x}"
    else:
        reference_value = var.reference_value
    
    if (var.status) in VAR_STATUS_NAMES:
        status = VAR_STATUS_NAMES[var.status] + f" # {var.status}"
    else:    
        status = var.status
    
    if var.name:
        return f"""  - name: {var.name}
    id: 0x{var.id:x}
    status: {status}
    flags: 0x{var.flags:x}
    reference_value: {reference_value}\n"""
    else:
        return f"""  - id: 0x{var.id:x}
    status: {status}
    flags: 0x{var.flags:x}
    reference_value: {reference_value}\n"""


def write_variables(sections: list[bytes], symbol_ids: dict):
    # section 2
    variables = read_variable_defs(sections[2])
    
    var_str = 'variables:\n'
    prev_status = None
    for var in variables:
        if prev_status != None and var.status != prev_status:
            var_str += '  \n'
        
        prev_status = var.status
        symbol_ids[var.id] = var
        var_str += print_var(var)
    
    # section 4
    variables2 = read_variable_defs(sections[4])
    
    var_str += '\nvariables2:\n'
    prev_status = None
    for var in variables2:
        if prev_status != None and var.status != prev_status:
            var_str += '  \n'
        
        prev_status = var.status
        symbol_ids[var.id] = var
        var_str += print_var(var)
    
    # section 6
    global_variables = read_variable_defs(sections[6])
    
    var_str += '\nglobal_variables:\n'
    prev_status = None
    for var in global_variables:
        if prev_status != None and var.status != prev_status:
            var_str += '  \n'
        
        prev_status = var.status
        symbol_ids[var.id] = var
        var_str += print_var(var)
    
    with open(argv[1] + '.variables.yaml', 'w') as f:
        f.write(var_str)
