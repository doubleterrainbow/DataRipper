from enum import IntEnum


class UnnamedEntryType(IntEnum):
    # Entry denoting an unnamed start of a reference node.
    UNNAMED_START_REF_NODE = 0x2
    # Entry denoting an unnamed start of a struct node.
    UNNAMED_START_STRUCT_NODE = 0x4
    # Entry denoting an unnamed internal reference.
    UNNAMED_INTERNAL_REF = 0xA
    # Entry denoting an unnamed external reference by index.
    UNNAMED_EXTERNAL_INDEX_REF = 0xC
    # Entry denoting an unnamed external reference by guid.
    UNNAMED_EXTERNAL_GUID_REF = 0xE
    # Entry denoting an unnamed sbyte.
    UNNAMED_SBYTE = 0x10
    # Entry denoting an unnamed byte.
    UNNAMED_BYTE = 0x12
    # Entry denoting an unnamed short.
    UNNAMED_SHORT = 0x14
    # Entry denoting an unnamed ushort.
    UNNAMED_U_SHORT = 0x16
    # Entry denoting an unnamed int.
    UNNAMED_INT = 0x18
    # Entry denoting an unnamed uint.
    UNNAMED_U_INT = 0x1A
    # Entry denoting an unnamed long.
    UNNAMED_LONG = 0x1C
    # Entry denoting an unnamed ulong.
    UNNAMED_U_LONG = 0x1E
    # Entry denoting an unnamed float.
    UNNAMED_FLOAT = 0x20
    # Entry denoting an unnamed double.
    UNNAMED_DOUBLE = 0x22
    # Entry denoting an unnamed decimal.
    UNNAMED_DECIMAL = 0x24
    # Entry denoting an unnamed char.
    UNNAMED_CHAR = 0x26
    # Entry denoting an unnamed string.
    UNNAMED_STRING = 0x28
    # Entry denoting an unnamed guid.
    UNNAMED_GUID = 0x2A
    # Entry denoting an unnamed boolean.
    UNNAMED_BOOL = 0x2C
    # Entry denoting an unnamed null.
    UNNAMED_NULL = 0x2E
    # Entry denoting an unnamed external reference by string.
    UNNAMED_EXT_STRING_REF = 0x33


class NamedEntryType(IntEnum):
    # Entry denoting a named start of a reference node.
    NAMED_START_REF_NODE = 0x1
    # Entry denoting a named start of a struct node.
    NAMED_START_STRUCT_NODE = 0x3
    # Entry denoting a named internal reference.
    NAMED_INTERNAL_REF = 0x9
    # Entry denoting a named external reference by index.
    NAMED_EXTERNAL_INDEX_REF = 0xB
    # Entry denoting a named external reference by guid.
    NAMED_EXTERNAL_GUID_REF = 0xD
    # Entry denoting a named sbyte.
    NAMED_SBYTE = 0xF
    # Entry denoting a named byte.
    NAMED_BYTE = 0x11
    # Entry denoting a named short.
    NAMED_SHORT = 0x13
    # Entry denoting a named ushort.
    NAMED_U_SHORT = 0x15
    # Entry denoting a named int.
    NAMED_INT = 0x17
    # Entry denoting a named uint.
    NAMED_U_INT = 0x19
    # Entry denoting a named long.
    NAMED_LONG = 0x1B
    # Entry denoting a named ulong.
    NAMED_U_LONG = 0x1D
    # Entry denoting a named float.
    NAMED_FLOAT = 0x1F
    # Entry denoting a named double.
    NAMED_DOUBLE = 0x21
    # Entry denoting a named decimal.
    NAMED_DECIMAL = 0x23
    # Entry denoting a named char.
    NAMED_CHAR = 0x25
    # Entry denoting a named string.
    NAMED_STRING = 0x27
    # Entry denoting a named guid.
    NAMED_GUID = 0x29
    # Entry denoting a named boolean.
    NAMED_BOOL = 0x2B
    # Entry denoting a named null.
    NAMED_NULL = 0x2D
    # Entry denoting a named external reference by string.
    NAMED_EXT_STRING_REF = 0x32


class EntryType(IntEnum):
    # An invalid entry.
    INVALID = 0x0
    # Entry denoting an end of node.
    NODE_END = 0x5
    # Entry denoting the start of an array.
    ARRAY_START = 0x6
    # Entry denoting the end of an array.
    ARRAY_END = 0x7
    # Entry denoting a primitive array.
    PRIMITIVE_ARRAY = 0x8
    # Entry denoting a type name
    TYPE_NAME = 0x2F
    # Entry denoting a type id.
    TYPE_ID = 0x30
    # Entry denoting that the end of the stream has been reached.
    STREAM_END = 0x31
    # Entry is a primitive value of type string or char.
    STRING = -1
    # Entry is a primitive value of type guid.
    GUID = -2
    # Entry is a primitive value of type sbyte, byte, short, ushort, int, uint, long or ulong.
    INTEGER = -3
    # Entry is a primitive value of type float, double or decimal.
    FLOATING_POINT = -4
    # Entry is a primitive boolean value.
    BOOLEAN = -5
    # Entry is a null value.
    NULL = -6
    # Entry marks the start of a node, IE, a complex type that contains values of its own.
    NODE_START = -7
    # Entry contains an ID that is a reference to a node defined previously in the stream.
    INTERNAL_REF = -9
    # Entry contains the index of an external object in the DeserializationContext.
    EXTERNAL_REF = -10
    # Entry contains the guid of an external object in the DeserializationContext.
    EXTERNAL_REF_GUID = -11
    # Entry contains the string id of an external object in the DeserializationContext.
    EXTERNAL_REF_STRING = -16
    # Unset
    UNSET = -999
