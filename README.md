# destructor

**The gizmo from Pismo (Beach)**

`destructor` is a library for processing binary data. There are many binary processing libraries; this one is mine. `destructor` takes a semi-declarative approach to binary processing similar to `construct` and `protlib`; however, instead of declaring the structure of the data using Python code, `destructor` parses C struct declarations to determine the structure of the data. As a result, it is quick and easy to prototype stuff if you have C struct declarations.

# Installation

    # python setup.py install

`destructor` depends on the `pycparser` module which is installed as a dependency by the setup script.

# Usage

Create a subclass of the `Structure` class, and set `source` to the structure definition (along with any required typedefs).

    >>> class TestStruct(Structure):
    ...     _source = """
    ...     typedef unsigned int    uint32_t;
    ...     typedef uint32_t        UINT32;
    ...     struct Test {
    ...         char                m_char;
    ...         signed char         m_signed_char;
    ...         unsigned char       m_unsigned_char;
    ...         _Bool               m_bool;
    ...         short               m_short;
    ...         unsigned short      m_unsigned_short;
    ...         int                 m_int;
    ...         unsigned int        m_unsigned_int;
    ...         long                m_long;
    ...         unsigned long       m_unsigned_long;
    ...         long long           m_long_long;
    ...         unsigned long long  m_unsigned_long_long;
    ...         float               m_float;
    ...         double              m_double;
    ...         char                m_string[16];
    ...         void *              m_void_p;
    ...         char *              m_char_p;
    ...         uint32_t            m_uint32_t;
    ...         UINT32              m_UINT32;
    ...     };
    ...     """

Instantiate the class and feed it some data.

    >>> data = (
    ...     "\x41"
    ...     "\xF2"
    ...     "\x03"
    ...     "\x01"
    ...     "\xFF\xF0"
    ...     "\xFF\xF0"
    ...     "\xFF\x00\xFF\x11"
    ...     "\xFF\x00\xFF\x22"
    ...     "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    ...     "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    ...     "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    ...     "\xFF\xFF\xFF\x80\x00\x00\x11\x00"
    ...     "\x00\x00\x11\x22"
    ...     "\x00\xFF\xFF\x80\x00\x00\x33\x00"
    ...     "AAAAAAAAAAAAAABB"
    ...     "\xFF\xFF\xFF\x80\x00\x00\x44\x00"
    ...     "\xFF\xFF\xFF\x80\x00\x00\x55\x00"
    ...     "\x00\x00\x11\x00"
    ...     "\x00\x00\x22\x00"
    ... )
    >>> thing = TestStruct()
    >>> thing.parse(data)

Grab a string representation of the struct.

    >>> repr(thing)
    'A\xf2\x03\x01\xff\xf0\xff\xf0\xff\x00\xff\x11\xff\x00\xff"\xff\xff\xff\x80
    \x00\x00\x11\x00\xff\xff\xff\x80\x00\x00\x11\x00\xff\xff\xff\x80\x00\x00\x11
    \x00\xff\xff\xff\x80\x00\x00\x11\x00\x00\x00\x11"\x00\xff\xff\x80\x00\x003
    \x00AAAAAAAAAAAAAABB\xff\xff\xff\x80\x00\x00D\x00\xff\xff\xff\x80\x00\x00U
    \x00\x00\x00\x11\x00\x00\x00"\x00'

Update a struct member and retrieve it.

    >>> thing.m_unsigned_long.value = 0
    >>> repr(thing.m_unsigned_long)
    '\x00\x00\x00\x00\x00\x00\x00\x00'
    >>> thing.m_unsigned_long.value = 0xffff
    >>> repr(thing.m_unsigned_long)
    '\xff\xff\x00\x00\x00\x00\x00\x00

Write the struct to file and read it back.

    >>> with open("temp.bin", "w+b") as f:
    ...     thing.write(f)
    >>> file("temp.bin").read()
    'A\xf2\x03\x01\xff\xf0\xff\xf0\xff\x00\xff\x11\xff\x00\xff"\xff\xff\xff\x80
    \x00\x00\x11\x00\xff\xff\x00\x00\x00\x00\x00\x00\xff\xff\xff\x80\x00\x00\x11
    \x00\xff\xff\xff\x80\x00\x00\x11\x00\x00\x00\x11"\x00\xff\xff\x80\x00\x003
    \x00AAAAAAAAAAAAAABB\xff\xff\xff\x80\x00\x00D\x00\xff\xff\xff\x80\x00\x00U
    \x00\x00\x00\x11\x00\x00\x00"\x00'

Endianness is determined by the `endian` parameter to `__init__`.

    >>> thing = TestStruct(endian=ENDIAN_BIG)
    >>> thing.parse(data)
    >>> repr(thing.m_unsigned_long)
    '\xff\xff\xff\x80\x00\x00\x11\x00'
    >>> thing.m_unsigned_long.value = 0xffff
    >>> repr(thing.m_unsigned_long)
    '\x00\x00\x00\x00\x00\x00\xff\xff'

The size of longs and pointers is determined by the `mode` parameter to `__init__`.

    >>> thing = TestStruct(mode=MODE_ILP32)
    >>> thing.parse(data)
    >>> thing.m_void_p.size
    4
    >>> thing = TestStruct(mode=MODE_LP64)
    >>> thing.parse(data)
    >>> thing.m_void_p.size
    8

Nested structs are supported, see `destructor_tests.py` for examples. I will add some better examples sometime.

# Caveats

It's pretty basic so far. Needs some work.

Unions are not yet supported.

Conditional parsing, array length depending on other fields, etc are not supported.

# Tests

destructor has a test suite. Run it by installing `nose`:

```bash
pip install nose
```

And either executing it via setuptools:

```bash
python setup.py nosetests
```

Or by using the nose test runner directly:

```bash
nosetests
```

# License

Buy snare a beer. Do it.
