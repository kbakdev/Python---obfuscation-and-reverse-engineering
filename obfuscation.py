from types import *
from dis import dis, hasjabs, hasconst, hasname, haslocal, hasjrel
from opcode import HAVE_ARGUMENT, opmap
from struct import pack, unpack
import os

def rw(s): # Load 16-bit Word.
    return unpack("<H", s[0:2])[0]

def db(v): # Emit an 8-bit byte.
    return bytearray(pack("<B", v & 0xff))

def dw(v): # Emit 16-bit Word.
    return bytearray(pack("<H", v & 0xffff))

def emit_JUMP_FORWARD(jump):
    return db(opmap['JUMP_FORWARD']) + dw(jump)

def obfuscate_function_py3(f):
    code_obj = f.__code__
    bytecode = bytearray(code_obj.co_code)
    output_bytecode = []
    jump__map = {}
    jumps_to_fix = []
    JABS = 0
    JREL = 1

    # Phase 1: Generating the modified code.
    src_i = 0
    dst_i = 0
    while src_i < len(bytecode):
        opcode = bytecode[src_i]
        opcode_len = [1, 3][opcode >= HAVE_ARGUMENT]

        # Note the mapping of input to output address.
        jump_target_map[src_i] = dst_i

        # Emit jump and random bytes.
        JUMP_SIZE = 3
        TRASH_SIZE = 3
        output_bytecode.extend(emit_JUMP_FORWARD(TRASH_SIZE))
        output_bytecode.extend(os.urandom(TRASH_SIZE))
        dst_i += JUMP_SIZE + TRASH_SIZE

        # Emit original instruction.
        # If it is a relative or absolute jump, note its position.
        if opcode in hasjabs: # jabs - Jump ABSolute.
            org_jump_dst = rw(bytecode[src_i + 1:src_i + 3])
            jumps_to_fix.append((JABS, dst_i, org_jump_dst))
        elif opcode in hasjrel: # jrel - Jump RELative.
            org_jump_dst = (src_i + opcode_len + rw(bytecode[src_i + 1:src_i + 3]))
            jumps_to_fix.append((JREL, dst_i, org_jump_dst))

        output_bytecode.extend(bytecode[src_i:src_i + opcode_len])
        src_i += opcode_len
        dst_i += opcode_len

    # Phase 2: Improving the jump arguments.
    for jump_type, dst_i, org_jump_dst in jumps_to_fix:
        jump_dst = jump_target_map[org_jump_dst]
        if jump_type == JREL:
            jump_dst -= dst_i + 3 # Relativize the argument.
        output_bytecode[dst_i + 1:dst_i + 3] = dw(jump_dst)

    output_bytecode = bytes(output_bytecode)

    # Generating a text representation of the function object and code.
    s = []
    s.append('%s = types.FunctionType(' % f.__name__)
    s.append('types.CodeType(')

    for field in [
            'co_argcount', 'co_kwonlyargcount', 'co_nlocals', 'co_stacksize',
            'co_flags', 'co_code', 'co_consts', 'co_names', 'co_varnames', 'co_filename',
            'co_name', 'co_firslineno', 'co_lnotab', 'co_freevars', 'co_cellvars']:
        if field == 'co_code':
            s.append(repr(output_bytecode))
        else:
            s.append(repr(getattr(code_obj, field)))
        s.append(',')

    s.append('), globals())')

    return ''.join(s)

def hello_world():
    s = "Hello World"
    for ch in s:
        print(ch, end="")
    print("")

print("import types")
print(obfuscate_function_py3(hello_world))
print("hello_world()")