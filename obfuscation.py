from types import *
from dis import dis, hasjabs, hasconst, hasname, haslocal, hasjrel
from opcode import HAVE_ARGUMENT, opmap
from struct import pack, unpack
import os

def rw(s): # Load 16-bit Word.
    