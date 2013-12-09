from nose.tools import *
from destructor import *
from pycparser import c_parser, c_ast
import os

TYPEDEFS = """
typedef unsigned int    uint32_t;
typedef uint32_t        UINT32;
"""

STRUCT = TYPEDEFS + """
struct Test {
    char                m_char;
    signed char         m_signed_char;
    unsigned char       m_unsigned_char;
    _Bool               m_bool;
    short               m_short;
    unsigned short      m_unsigned_short;
    int                 m_int;
    unsigned int        m_unsigned_int;
    long                m_long;
    unsigned long       m_unsigned_long;
    long long           m_long_long;
    unsigned long long  m_unsigned_long_long;
    float               m_float;
    double              m_double;
    char                m_string[16];
    void *              m_void_p;
    char *              m_char_p;
    uint32_t            m_uint32_t;
    UINT32              m_UINT32;
};
"""

DATA = (
    "\x41"
    "\xF2"
    "\x03"
    "\x01"
    "\xFF\xF0"
    "\xFF\xF0"
    "\xFF\x00\xFF\x11"
    "\xFF\x00\xFF\x22"
    "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    "\x00\x00\x11\x22"
    "\x00\xFF\xFF\x80\x00\x00\x33\x00"
    "AAAAAAAAAAAAAABB"
    "\xFF\xFF\xFF\x80\x00\x00\x44\x00"
    "\xFF\xFF\xFF\x80\x00\x00\x55\x00"
    "\x00\x00\x11\x00"
    "\x00\x00\x22\x00"
)

TYPEDEF_DECL = TYPEDEFS + """
UINT32 test;
"""

class TestStruct(Structure):
    source = STRUCT

def setup():
    global s1, s2, s3, s4, s5, s6, s7
    s1 = Structure(source=STRUCT)
    s2 = Structure(source=STRUCT, mode=MODE_ILP32)
    s3 = TestStruct()
    s4 = TestStruct()
    s4.parse(DATA)
    s5 = TestStruct(endian=ENDIAN_BIG)
    s5.parse(DATA)
    s6 = TestStruct(endian=ENDIAN_BIG, mode=MODE_ILP32)
    s6.parse(DATA)

    f = open("tests/test.bin", "w+b")
    f.write(DATA)
    f.close()

    s7 = TestStruct()
    f = open("tests/test.bin", "r+b")
    s7.read(file("tests/test.bin"))
    f.close()

def teardown():
    try:
        os.remove("tests/test.bin")
    except:
        pass
    try:
        os.remove("tests/test2.bin")
    except:
        pass

# basic class tests

def test_node_finder():
    ast = c_parser.CParser().parse(STRUCT, filename='<none>')
    matches = NodeFinder(c_parser.c_ast.IdentifierType).find(ast)
    assert len(matches) > 0

def test_resolver():
    ast = c_parser.CParser().parse(TYPEDEF_DECL, filename='<none>')
    res = TypeResolver(ast)
    t = res.resolve_type(ast.ext[-1].type)
    assert t.type.names == ['unsigned', 'int']

def test_set():
    s = StructureSet(source=STRUCT)
    assert len(s.decls) == 1

def test_create_struct():
    assert s1 != None

def test_struct_members():
    assert len(s1._members) == 19

def test_subclass():
    assert s3 != None

def test_subclass_m_char():
    assert s3.m_char.size == 1

def test_subclass_members():
    assert len(s3._members) == 19

# check member variable sizes and format strings

def test_m_char_size():
    assert s1.m_char.size == 1

def test_m_char_format():
    assert s1.m_char.format == '<c'

def test_m_signed_char_size():
    assert s1.m_signed_char.size == 1

def test_m_signed_char_format():
    assert s1.m_signed_char.format == '<b'

def test_m_unsigned_char_size():
    assert s1.m_unsigned_char.size == 1

def test_m_unsigned_char_format():
    assert s1.m_unsigned_char.format == '<B'

def test_m_bool_size():
    assert s1.m_bool.size == 1

def test_m_bool_format():
    assert s1.m_bool.format == '<?'

def test_m_short_size():
    assert s1.m_short.size == 2

def test_m_short_format():
    assert s1.m_short.format == '<h'

def test_m_unsigned_short_size():
    assert s1.m_unsigned_short.size == 2

def test_m_unsigned_short_format():
    assert s1.m_unsigned_short.format == '<H'

def test_m_int_size():
    assert s1.m_int.size == 4

def test_m_int_format():
    assert s1.m_int.format == '<i'

def test_m_unsigned_int_size():
    assert s1.m_unsigned_int.size == 4

def test_m_unsigned_int_format():
    assert s1.m_unsigned_int.format == '<I'

def test_m_long_size():
    assert s1.m_long.size == 8

def test_m_long_format():
    assert s1.m_long.format == '<q'

def test_m_unsigned_long_size():
    assert s1.m_unsigned_long.size == 8

def test_m_unsigned_long_format():
    assert s1.m_unsigned_long.format == '<Q'

def test_m_long_ilp32_size():
    assert s2.m_long.size == 4

def test_m_long_ilp32_format():
    assert s2.m_long.format == '<l'

def test_m_unsigned_long_ilp32_size():
    assert s2.m_unsigned_long.size == 4

def test_m_unsigned_long_ilp32_format():
    assert s2.m_unsigned_long.format == '<L'

def test_m_long_long_size():
    assert s1.m_long_long.size == 8

def test_m_long_long_format():
    assert s1.m_long_long.format == '<q'

def test_m_unsigned_long_long_size():
    assert s1.m_unsigned_long_long.size == 8

def test_m_unsigned_long_long_format():
    assert s1.m_unsigned_long_long.format == '<Q'

def test_m_float_size():
    assert s1.m_float.size == 4

def test_m_float_format():
    assert s1.m_float.format == '<f'

def test_m_double_size():
    assert s1.m_double.size == 8

def test_m_double_format():
    assert s1.m_double.format == '<d'

def test_m_string_size():
    assert s1.m_string.size == 16

def test_m_string_format():
    assert s1.m_string.format == '<16s'

def test_m_void_p_size():
    assert s1.m_void_p.size == 8

def test_m_void_p_format():
    assert s1.m_void_p.format == '<Q'

def test_m_void_p_ilp_32_size():
    assert s2.m_void_p.size == 4

def test_m_void_p_ilp_32_format():
    assert s2.m_void_p.format == '<L'

def test_m_char_p_size():
    assert s1.m_char_p.size == 8

def test_m_char_p_format():
    assert s1.m_char_p.format == '<Q'

def test_m_char_p_ilp_32_size():
    assert s2.m_char_p.size == 4

def test_m_char_p_ilp_32_format():
    assert s2.m_char_p.format == '<L'

def test_m_uint32_t_size():
    assert s1.m_uint32_t.size == 4

def test_m_uint32_t_format():
    assert s1.m_uint32_t.format == '<I'

def test_m_UINT32_size():
    assert s1.m_UINT32.size == 4

def test_m_UINT32_format():
    assert s1.m_UINT32.format == '<I'

# test format strings big endian

def test_struct_endian():
    assert s5._endian == ENDIAN_BIG

def test_m_char_format_big_endian():
    assert s5.m_char.format == '>c'

def test_m_signed_char_format_big_endian():
    assert s5.m_signed_char.format == '>b'

def test_m_unsigned_char_format_big_endian():
    assert s5.m_unsigned_char.format == '>B'

def test_m_bool_format_big_endian():
    assert s5.m_bool.format == '>?'

def test_m_short_format_big_endian():
    assert s5.m_short.format == '>h'

def test_m_unsigned_short_format_big_endian():
    assert s5.m_unsigned_short.format == '>H'

def test_m_int_format_big_endian():
    assert s5.m_int.format == '>i'

def test_m_unsigned_int_format_big_endian():
    assert s5.m_unsigned_int.format == '>I'

def test_m_long_format_big_endian():
    assert s5.m_long.format == '>q'

def test_m_unsigned_long_format_big_endian():
    assert s5.m_unsigned_long.format == '>Q'

def test_m_long_ilp32_format_big_endian():
    assert s6.m_long.format == '>l'

def test_m_unsigned_long_ilp32_format_big_endian():
    assert s6.m_unsigned_long.format == '>L'

def test_m_long_long_format_big_endian():
    assert s5.m_long_long.format == '>q'

def test_m_unsigned_long_long_format_big_endian():
    assert s5.m_unsigned_long_long.format == '>Q'

def test_m_float_format_big_endian():
    assert s5.m_float.format == '>f'

def test_m_double_format_big_endian():
    assert s5.m_double.format == '>d'

def test_m_string_format_big_endian():
    assert s5.m_string.format == '>16s'

def test_m_void_p_format_big_endian():
    assert s5.m_void_p.format == '>Q'

def test_m_void_p_ilp_32_format_big_endian():
    assert s6.m_void_p.format == '>L'

def test_m_char_p_format_big_endian():
    assert s5.m_char_p.format == '>Q'

def test_m_char_p_ilp_32_format_big_endian():
    assert s6.m_char_p.format == '>L'

def test_m_uint32_t_format_big_endian():
    assert s5.m_uint32_t.format == '>I'

def test_m_UINT32_format_big_endian():
    assert s5.m_UINT32.format == '>I'

# test values

def test_m_char_value():
    assert s4.m_char.value == 'A'

def test_m_signed_char_value():
    assert s4.m_signed_char.value == -14

def test_m_unsigned_char_value():
    assert s4.m_unsigned_char.value == 3

def test_m_bool_value():
    assert s4.m_bool.value == 1

def test_m_short_value():
    assert s4.m_short.value == -3841

def test_m_unsigned_short_value():
    assert s4.m_unsigned_short.value == 0xF0FF

def test_m_int_value():
    assert s4.m_int.value == 0x11FF00FF

def test_m_unsigned_int_value():
    assert s4.m_unsigned_int.value == 0x22FF00FF

def test_m_long_value():
    assert s4.m_long.value == 0x11000080FFFFFF

def test_m_unsigned_long_value():
    assert s4.m_unsigned_long.value == 0x11000080FFFFFF

def test_m_long_long_value():
    assert s4.m_long_long.value == 0x11000080FFFFFF

def test_m_unsigned_long_long_value():
    assert s4.m_unsigned_long_long.value == 0x11000080FFFFFF

def test_m_float_value():
    assert s4.m_float.value == 1.9651164376299768e-18

def test_m_double_value():
    assert s4.m_double.value == 1.0569105105056467e-307

def test_m_string_value():
    assert s4.m_string.value == "AAAAAAAAAAAAAABB"

def test_m_void_p_value():
    assert s4.m_void_p.value == 0x44000080FFFFFF

def test_m_char_p_value():
    assert s4.m_char_p.value == 0x55000080FFFFFF

def test_m_uint32_t_value():
    assert s4.m_uint32_t.value == 0x110000

def test_m_UINT32_value():
    assert s4.m_UINT32.value == 0x220000

def test_parse_string():
    s1.parse(DATA)
    assert repr(s1) == DATA

# test values big endian

def test_m_char_value_big_endian():
    assert s5.m_char.value == 'A'

def test_m_signed_char_value_big_endian():
    assert s5.m_signed_char.value == -14

def test_m_unsigned_char_value_big_endian():
    assert s5.m_unsigned_char.value == 3

def test_m_bool_value_big_endian():
    assert s5.m_bool.value == 1

def test_m_short_value_big_endian():
    assert s5.m_short.value == -16

def test_m_unsigned_short_value_big_endian():
    assert s5.m_unsigned_short.value == 0xFFF0

def test_m_int_value_big_endian():
    assert s5.m_int.value == -16711919

def test_m_unsigned_int_value_big_endian():
    assert s5.m_unsigned_int.value == 0xFF00FF22

def test_m_long_value_big_endian():
    assert s5.m_long.value == -549755809536

def test_m_unsigned_long_value_big_endian():
    assert s5.m_unsigned_long.value == 0xFFFFFF8000001100

def test_m_long_long_value_big_endian():
    assert s5.m_long_long.value == -549755809536

def test_m_unsigned_long_long_value_big_endian():
    assert s5.m_unsigned_long_long.value == 0xFFFFFF8000001100

def test_m_float_value_big_endian():
    assert s5.m_float.value == 6.146095064528648e-42

def test_m_double_value_big_endian():
    assert s5.m_double.value == 7.2906770047952646e-304

def test_m_string_value_big_endian():
    assert s5.m_string.value == "AAAAAAAAAAAAAABB"

def test_m_void_p_value_big_endian():
    assert s5.m_void_p.value == 0xffffff8000004400

def test_m_char_p_value_big_endian():
    assert s5.m_char_p.value == 0xffffff8000005500

def test_m_uint32_t_value_big_endian():
    assert s5.m_uint32_t.value == 0x1100

def test_m_UINT32_value_big_endian():
    assert s5.m_UINT32.value == 0x2200

def test_parse_string_big_endian():
    s5.parse(DATA)
    assert repr(s5) == DATA

# test repr values little endian

def test_m_char_repr():
    assert repr(s4.m_char) == "\x41"

def test_m_signed_char_repr():
    assert repr(s4.m_signed_char) == "\xF2"

def test_m_unsigned_char_repr():
    assert repr(s4.m_unsigned_char) == "\x03"

def test_m_bool_repr():
    assert repr(s4.m_bool) == "\x01"

def test_m_short_repr():
    assert repr(s4.m_short) == "\xFF\xF0"

def test_m_unsigned_short_repr():
    assert repr(s4.m_unsigned_short) == "\xFF\xF0"

def test_m_int_repr():
    assert repr(s4.m_int) == "\xFF\x00\xFF\x11"

def test_m_unsigned_int_repr():
    assert repr(s4.m_unsigned_int) == "\xFF\x00\xFF\x22"

def test_m_long_repr():
    assert repr(s4.m_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_unsigned_long_repr():
    assert repr(s4.m_unsigned_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_long_long_repr():
    assert repr(s4.m_long_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_unsigned_long_long_repr():
    assert repr(s4.m_unsigned_long_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_float_repr():
    assert repr(s4.m_float) == "\x00\x00\x11\x22"

def test_m_double_repr():
    assert repr(s4.m_double) == "\x00\xFF\xFF\x80\x00\x00\x33\x00"

def test_m_string_repr():
    assert repr(s4.m_string) == "AAAAAAAAAAAAAABB"

def test_m_void_p_repr():
    assert repr(s4.m_void_p) == "\xFF\xFF\xFF\x80\x00\x00\x44\x00"

def test_m_char_p_repr():
    assert repr(s4.m_char_p) == "\xFF\xFF\xFF\x80\x00\x00\x55\x00"

def test_m_uint32_t_repr():
    assert repr(s4.m_uint32_t) == "\x00\x00\x11\x00"

def test_m_UINT32_repr():
    assert repr(s4.m_UINT32) == "\x00\x00\x22\x00"

# test repr values big endian

def test_m_char_repr_big_endian():
    assert repr(s5.m_char) == "\x41"

def test_m_signed_char_repr_big_endian():
    assert repr(s5.m_signed_char) == "\xF2"

def test_m_unsigned_char_repr_big_endian():
    assert repr(s5.m_unsigned_char) == "\x03"

def test_m_bool_repr_big_endian():
    assert repr(s5.m_bool) == "\x01"

def test_m_short_repr_big_endian():
    assert repr(s5.m_short) == "\xFF\xF0"

def test_m_unsigned_short_repr_big_endian():
    assert repr(s5.m_unsigned_short) == "\xFF\xF0"

def test_m_int_repr_big_endian():
    assert repr(s5.m_int) == "\xFF\x00\xFF\x11"

def test_m_unsigned_int_repr_big_endian():
    assert repr(s5.m_unsigned_int) == "\xFF\x00\xFF\x22"

def test_m_long_repr_big_endian():
    assert repr(s5.m_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_unsigned_long_repr_big_endian():
    assert repr(s5.m_unsigned_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_long_long_repr_big_endian():
    assert repr(s5.m_long_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_unsigned_long_long_repr_big_endian():
    assert repr(s5.m_unsigned_long_long) == "\xFF\xFF\xFF\x80\x00\x00\x11\x00"

def test_m_float_repr_big_endian():
    assert repr(s5.m_float) == "\x00\x00\x11\x22"

def test_m_double_repr_big_endian():
    assert repr(s5.m_double) == "\x00\xFF\xFF\x80\x00\x00\x33\x00"

def test_m_string_repr_big_endian():
    assert repr(s5.m_string) == "AAAAAAAAAAAAAABB"

def test_m_void_p_repr_big_endian():
    assert repr(s5.m_void_p) == "\xFF\xFF\xFF\x80\x00\x00\x44\x00"

def test_m_char_p_repr_big_endian():
    assert repr(s5.m_char_p) == "\xFF\xFF\xFF\x80\x00\x00\x55\x00"

def test_m_uint32_t_repr_big_endian():
    assert repr(s5.m_uint32_t) == "\x00\x00\x11\x00"

def test_m_UINT32_repr_big_endian():
    assert repr(s5.m_UINT32) == "\x00\x00\x22\x00"

# test file read/write

def test_file_read():
    assert repr(s7) == DATA

def test_file_write():
    f = open("tests/test2.bin", "w+b")
    s7.write(f)
    f.close()
    d = file("tests/test2.bin").read()
    assert d == DATA


