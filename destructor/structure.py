import pycparser
import struct

from pycparser import c_parser, c_ast

MODE_ILP32 = 'ILP32'
MODE_LP64 = 'LP64'

ENDIAN_LITTLE = 'little'
ENDIAN_BIG = 'big'


def sizeof(obj):
    return obj.size


class NodeFinder(object):
    nodes = []

    def __init__(self, cls):
        self.col = NodeCollector(cls)

    def find(self, node):
        self.col.visit(node)
        return self.col.nodes


class NodeCollector(c_ast.NodeVisitor):
    """
    A NodeVisitor subclass used to collect instances of a specific node class
    """
    cls = None

    def __init__(self, cls):
        self.nodes = []
        self.cls = cls

    def visit_collect(self, node):
        if type(node) is self.cls:
            self.nodes.append(node)

    def __getattribute__(self, name):
        if name.startswith('visit_') and name == 'visit_' + self.cls.__name__:
            return self.visit_collect
        else:
            return object.__getattribute__(self, name)


class TypeResolver(object):
    """
    A utility class to resolve typedefs and get some other type info from the AST
    """

    base_types = ['char', '_Bool', 'int', 'long', 'long long', 'float', 'double', 'long double']

    def __init__(self, ast):
        self.typedefs = NodeFinder(pycparser.c_ast.Typedef).find(ast)

    def resolve_type(self, thetype):
        # find the IdentifierType node
        ident = NodeFinder(pycparser.c_ast.IdentifierType).find(thetype)[0]

        try:
            # find a match
            match = [t for t in self.typedefs if t.name == ident.names[0]][0]
            match_ident = NodeFinder(pycparser.c_ast.IdentifierType).find(match)[0]

            # if this resolves to a base type
            if len([n for n in match_ident.names if n in self.base_types]):
                # we're done
                return match.type
            else:
                # otherwise keep going
                return self.resolve_type(match)
        except IndexError:
            # didn't find a match, return the type we were given
            return thetype

    def name_for_type(self, thetype):
        # find the IdentifierType node
        ident = NodeFinder(pycparser.c_ast.IdentifierType).find(thetype)[0]

        # join the type name components
        return ' '.join(ident.names)

    def find_struct_node(self, thetype):
        try:
            # find a Struct node
            s = NodeFinder(pycparser.c_ast.Struct).find(thetype)[0]
        except IndexError:
            s = None
        return s


class StructureMember(object):
    """
    A structure member variable. Keeps track of the size, format, etc for an
    individual struct member.
    """
    sizes = {
        'char':     1,
        '_Bool':    1,
        'short':    2,
        'int':      4,
        'long':     0, # [4, 8] determined programatically below based on mode
        'long long':8,
        'float':    4,
        'double':   8
    }
    formats = {
        '_Bool':                '?',
        'unsigned char':        'B',
        'signed char':          'b',
        'char':                 'c',
        'unsigned short':       'H',
        'short':                'h',
        'unsigned int':         'I',
        'int':                  'i',
        'unsigned long':        'L',
        'long':                 'l',
        'unsigned long long':   'Q',
        'long long':            'q',
        'float':                'f',
        'double':               'd'
    }

    _size = 0
    _array_len = 1
    _value = None
    _endian = ENDIAN_LITTLE

    def __init__(self, name=None, type_name=None, node=None, mode=MODE_LP64, array_len=1, endian=ENDIAN_LITTLE):
        self._basic_type = type_name.replace('unsigned', '').replace('signed', '').strip()
        self._full_type = type_name
        self._array_len = array_len
        self._endian = endian

        if type_name in self.formats:
            # sort out the basic types
            self._size = self.sizes[self._basic_type]
            self._format = self.formats[self._full_type]

            # mode-specific sizes/formats
            if type_name == 'unsigned long':
                self._format = 'Q' if mode == MODE_LP64 else 'L'
                self._size = 8 if mode == MODE_LP64 else 4
            elif type_name == 'long':
                self._format = 'q' if mode == MODE_LP64 else 'l'
                self._size = 8 if mode == MODE_LP64 else 4

            # if it's a character array, use the string formatter instead
            if type_name == "char" and array_len > 1:
                self._format = 's'
        elif type_name.strip().endswith('*'):
            # we use a quad/double word instead of pointers due to the endian
            # stuff in the struct module (see the doco for details)
            self._format = 'Q' if mode == MODE_LP64 else 'L'
            self._size = 8 if mode == MODE_LP64 else 4
        else:
            raise Exception("Unknown type '%s'" % type_name)

    def __str__(self):
        return self.packed

    @property
    def size(self):
        return self._size * self._array_len

    @property
    def format(self):
        if self._array_len > 1:
            a = str(self.array_len)
        else:
            a = ''
        return self.endian_format + a + self._format

    @property
    def endian_format(self):
        return '<' if self._endian == ENDIAN_LITTLE else '>'

    @property
    def array_len(self):
        return self._array_len

    @array_len.setter
    def array_len(self, value):
        self._array_len = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def packed(self):
        if type(self.value) == list:
            data = struct.pack(self.format, *self.value)
        else:
            data = struct.pack(self.format, self.value)
        return data

    def read(self, input):
        if type(input) == str:
            data = input
        else:
            data = input.read(self.size)
        self.parse(data)

    def parse(self, data, offset=0):
        self.value = list(struct.unpack(self.format, data[offset:offset+self.size]))
        if len(self.value) == 1:
            self.value = self.value[0]

    def write(self, output):
        output.write(self.packed)


class Structure(object):
    """
    A structure. Initialise this with the source for a struct definition. If
    multiple struct definitions are found the first one will be used.
    """
    _members = {}
    _endian = ENDIAN_LITTLE

    _source = None
    _name = None

    def __init__(self, binary=None, source=None, filename=None, decl=None, ast=None, mode=MODE_LP64, endian=ENDIAN_LITTLE):
        self._endian = endian

        # if we didn't have any source provided by our subclass, override it with what was passed to __init__()
        if not self._source:
            self._source = source

        # parse source/file if we got some
        if self._source or filename:
            # create a structure set
            self._ss = StructureSet(source=self._source, filename=filename)
            ast = self._ss.ast

            # find the structure by name if one was given
            if self._name:
                decl = self._ss.decl_named(self._name)
                if not decl:
                    raise NameError("No struct declaration was found named '%s'" % self.name)
            else:
                # otherwise grab the first struct
                try:
                    decl = self._ss.decls[0]
                except IndexError:
                    raise IndexError("No struct declaration was found")

        # keep references to our ast and decl. check if we don't aready have them, as we may have if this came from
        # a StructureSet
        if not self._ast:
            self._ast = ast
        if not self._decl:
            self._decl = decl
        if not self._name:
            self._name = self._decl.name

        # find any typedefs we might need
        self._tr = TypeResolver(self._ast)

        # parse the declarator for our member info
        self.parse_decl(self._decl, mode)

        # if we got a binary, parse it
        if binary:
            if type(binary) == str:
                self.parse(binary)
            else:
                self.read(binary)

    def __str__(self):
        return ''.join([str(m) for m in self._members_ord])

    @property
    def size(self):
        return sum([m.size for m in self._members_ord])

    @property
    def endian(self):
        return self._endian

    def parse_decl(self, decl, mode=MODE_LP64):
        self._mode = mode
        self._members = {}
        self._members_ord = []

        index = 0
        for name, node in decl.children():
            # process the type
            if type(node.type) == pycparser.c_ast.PtrDecl:
                # find the type node hanging off this pointer node and resolve it
                t = NodeFinder(pycparser.c_ast.TypeDecl).find(node)[0]
                t = self._tr.resolve_type(t)

                # get the name of the underlying type and add a * because it's a pointer
                type_name = self._tr.name_for_type(t) + ' *'

                # instantiate the member
                member = StructureMember(name=node.name, node=node, type_name=type_name, mode=mode,
                                         endian=self._endian)
                self._members[node.name] = member
                self._members_ord.append(member)
            elif type(node.type) == pycparser.c_ast.TypeDecl:
                # see if this is a nested struct
                s = self._tr.find_struct_node(node.type)
                if s:
                    # it is, find the first declaration of this struct name
                    if self._ss:
                        s = self._ss.decl_named(s.name)

                    # and process it
                    member = Structure(decl=s, ast=self._ast, mode=mode, endian=self._endian)
                else:
                    # otherwise, resolve this type if it's a typedef
                    t = self._tr.resolve_type(node.type)

                    # get its name
                    type_name = self._tr.name_for_type(t)

                    # instantiate the member
                    member = StructureMember(name=node.name, node=node, type_name=type_name, mode=mode,
                                             endian=self._endian)

                # store the new member
                self._members[node.name] = member
                self._members_ord.append(member)
            elif type(node.type) == pycparser.c_ast.ArrayDecl:
                # find the type node hanging off this array node and resolve it
                t = NodeFinder(pycparser.c_ast.TypeDecl).find(node)[0]
                t = self._tr.resolve_type(t)

                # get the name of the underlying type
                type_name = self._tr.name_for_type(t)

                # get the array length
                array_len = int(node.type.dim.value)

                # instantiate the member
                member = StructureMember(name=node.name, node=node, type_name=type_name, mode=mode,
                                         endian=self._endian, array_len=array_len)
                self._members[node.name] = member
                self._members_ord.append(member)
            elif type(node.type) == pycparser.c_ast.Struct:
                raise NotImplementedError("Nested structs aren't supported yet")
            else:
                raise Exception("Unexpected node")
            index += 1

    def __getattr__(self, name):
        if not name.startswith('_') and name in self._members:
            return self._members[name]

    def read(self, infile, offset=0):
        infile.seek(offset)
        for m in self._members_ord:
            m.read(infile)

    def parse(self, data, offset=0):
        for m in self._members_ord:
            m.parse(data, offset)
            offset += m.size

    def write(self, outfile, offset=0):
        outfile.seek(offset)
        for m in self._members_ord:
            m.write(outfile)


class StructureSet(object):
    """
    A set of structures. Hand this class a header file and then retrieve
    Structure objects by name.
    """
    def __init__(self, source=None, filename=None):
        self.parser = c_parser.CParser()
        if source:
            self.parse_source(source)
        elif filename:
            self.parse_file(filename)

    def parse_source(self, source):
        # parse the C source
        self.ast = self.parser.parse(source, filename='<none>')

        # find any struct declarations
        self.decls = NodeFinder(pycparser.c_ast.Struct).find(self.ast)

    def parse_file(self, filename):
        self.parse_source(file(filename).read())

    def decl_named(self, name):
        try:
            decl = [d for d in self.decls if d.name == name][0]
        except IndexError:
            decl = None
        return decl

    def struct_named(self, name):
        decl = self.decl_named(name);
        if decl:
            st = type(name, (Structure,), {'_decl': decl, '_ast': self.ast, '_name': name, '_ss': self})
        else:
            st = None
        return st

    def all_structs(self):
        return [type(decl.name, (Structure,),
                    {'_decl': decl, '_ast': self.ast, '_name': decl.name, '_ss': self}) for decl in self.decls]

