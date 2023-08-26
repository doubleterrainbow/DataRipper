from collections.abc import Callable
from enum import IntEnum

# Scroll to bottom for documentation
# This is the bare minimum amount of functions I could translate from C# to get this to run with the skill tomes
# This may break at some point, or not work with other files such as map data
# This code is based on https://github.com/TeamSirenix/odin-serializer/blob/master/OdinSerializer/Core/DataReaderWriters/Binary/BinaryDataReader.cs
class NodeInfo:
    Name = ''
    Id = 0
    Type = ''
    IsArray = False
    IsEmpty = False

    def __init__(self, name:str, id:int, type:Type, isArray:bool):
        self.Name = name
        self.Id = id
        self.Type = type
        self.IsArray = isArray
        self.IsEmpty = False

EmptyNodeInfo = NodeInfo(None, 0, None, False)
EmptyNodeInfo.IsEmpty = True

class EntryType(IntEnum):
    # An invalid entry.
    Invalid = 0x0,
    # Entry denoting a named start of a reference node.
    NamedStartOfReferenceNode = 0x1,
    # Entry denoting an unnamed start of a reference node.
    UnnamedStartOfReferenceNode = 0x2,
    # Entry denoting a named start of a struct node.
    NamedStartOfStructNode = 0x3,
    # Entry denoting an unnamed start of a struct node.
    UnnamedStartOfStructNode = 0x4,
    # Entry denoting an end of node.
    EndOfNode = 0x5,
    # Entry denoting the start of an array.
    StartOfArray = 0x6,
    # Entry denoting the end of an array.
    EndOfArray = 0x7,
    # Entry denoting a primitive array.
    PrimitiveArray = 0x8,
    # Entry denoting a named internal reference.
    NamedInternalReference = 0x9,
    # Entry denoting an unnamed internal reference.
    UnnamedInternalReference = 0xA,
    # Entry denoting a named external reference by index.
    NamedExternalReferenceByIndex = 0xB,
    # Entry denoting an unnamed external reference by index.
    UnnamedExternalReferenceByIndex = 0xC,
    # Entry denoting a named external reference by guid.
    NamedExternalReferenceByGuid = 0xD,
    # Entry denoting an unnamed external reference by guid.
    UnnamedExternalReferenceByGuid = 0xE,
    # Entry denoting a named sbyte.
    NamedSByte = 0xF,
    # Entry denoting an unnamed sbyte.
    UnnamedSByte = 0x10,
    # Entry denoting a named byte.
    NamedByte = 0x11,
    # Entry denoting an unnamed byte.
    UnnamedByte = 0x12,
    # Entry denoting a named short.
    NamedShort = 0x13,
    # Entry denoting an unnamed short.
    UnnamedShort = 0x14,
    # Entry denoting a named ushort.
    NamedUShort = 0x15,
    # Entry denoting an unnamed ushort.
    UnnamedUShort = 0x16,
    # Entry denoting a named int.
    NamedInt = 0x17,
    # Entry denoting an unnamed int.
    UnnamedInt = 0x18,
    # Entry denoting a named uint.
    NamedUInt = 0x19,
    # Entry denoting an unnamed uint.
    UnnamedUInt = 0x1A,
    # Entry denoting a named long.
    NamedLong = 0x1B,
    # Entry denoting an unnamed long.
    UnnamedLong = 0x1C,
    # Entry denoting a named ulong.
    NamedULong = 0x1D,
    # Entry denoting an unnamed ulong.
    UnnamedULong = 0x1E,
    # Entry denoting a named float.
    NamedFloat = 0x1F,
    # Entry denoting an unnamed float.
    UnnamedFloat = 0x20,
    # Entry denoting a named double.
    NamedDouble = 0x21,
    # Entry denoting an unnamed double.
    UnnamedDouble = 0x22,
    # Entry denoting a named decimal.
    NamedDecimal = 0x23,
    # Entry denoting an unnamed decimal.
    UnnamedDecimal = 0x24,
    # Entry denoting a named char.
    NamedChar = 0x25,
    # Entry denoting an unnamed char.
    UnnamedChar = 0x26,
    # Entry denoting a named string.
    NamedString = 0x27,
    # Entry denoting an unnamed string.
    UnnamedString = 0x28,
    # Entry denoting a named guid.
    NamedGuid = 0x29,
    # Entry denoting an unnamed guid.
    UnnamedGuid = 0x2A,
    # Entry denoting a named boolean.
    NamedBoolean = 0x2B,
    # Entry denoting an unnamed boolean.
    UnnamedBoolean = 0x2C,
    # Entry denoting a named null.
    NamedNull = 0x2D,
    # Entry denoting an unnamed null.
    UnnamedNull = 0x2E,
    # Entry denoting a type name.
    TypeName = 0x2F,
    # Entry denoting a type id.
    TypeID = 0x30,
    # Entry denoting that the end of the stream has been reached.
    EndOfStream = 0x31,
    # Entry denoting a named external reference by string.
    NamedExternalReferenceByString = 0x32,
    # Entry denoting an unnamed external reference by string.
    UnnamedExternalReferenceByString = 0x33,

    # Entry is a primitive value of type string or char.
    String = -1,
    # Entry is a primitive value of type guid.
    Guid = -2,
    # Entry is a primitive value of type sbyte, byte, short, ushort, int, uint, long or ulong.
    Integer = -3,
    # Entry is a primitive value of type float, double or decimal.
    FloatingPoint = -4,
    # Entry is a primitive boolean value.
    Boolean = -5,
    # Entry is a null value.
    Null = -6,
    # Entry marks the start of a node, IE, a complex type that contains values of its own.
    StartOfNode = -7,
    # Entry contains an ID that is a reference to a node defined previously in the stream.
    InternalReference = -9,
    # Entry contains the index of an external object in the DeserializationContext.
    ExternalReferenceByIndex = -10,
    # Entry contains the guid of an external object in the DeserializationContext.
    ExternalReferenceByGuid = -11,
    # Entry contains the string id of an external object in the DeserializationContext.
    ExternalReferenceByString = -16,
    # Unset
    Unset = -999

class lookupExternalReference_type(IntEnum):
    guid = 1,
    index = 2,
    id = 3,
    name = 4

class SkillTomeParser:
    buffer = bytearray()
    bufferIndex = 0
    peekedEntryType = EntryType.Unset
    peekedEntryName = ''
    bufferIndex = 0
    bufferEnd = 0
    IsLittleEndian = True
    nodes = [EmptyNodeInfo] * 32
    nodesLength = 0
    output = {}

    def unset_lookupExternalReference(val:str|int, type:lookupExternalReference_type): return ''
    lookupExternalReference = unset_lookupExternalReference

    @property
    def CurrentNodeId(self) -> int: return self.CurrentNode.Id

    @property
    def CurrentNodeDepth(self) -> int: return self.nodesLength

    @property
    def CurrentNodeName(self) -> str: return self.CurrentNode.Name

    @property
    def CurrentNode(self):
        if (self.nodesLength == 0):
            return EmptyNodeInfo
        else:
            return self.nodes[self.nodesLength - 1]

    def __init__(self, SerializedBytes:str, lookupExternalReference:Callable[[str|int, lookupExternalReference_type], str]):
        self.buffer = bytearray.fromhex(SerializedBytes)
        self.bufferEnd = len(self.buffer)
        self.lookupExternalReference = lookupExternalReference
    
    def HasBufferData(self, amount:int) -> bool:
        return self.bufferIndex + amount <= self.bufferEnd

    def PeekEntry(self) -> tuple[EntryType, str]:
        if (self.peekedEntryType != EntryType.Unset):
            return self.peekedEntryType, self.peekedEntryName
        
        if (self.HasBufferData(1)):
            self.peekedEntryType = EntryType(self.buffer[self.bufferIndex])
            self.bufferIndex += 1
        else:
            self.peekedEntryType = EntryType.EndOfStream

        name = None
        if (self.peekedEntryType == EntryType.EndOfStream):
            name = None
            self.peekedEntryName = None
            self.peekedEntryType = EntryType.EndOfStream

        elif (self.peekedEntryType == EntryType.NamedStartOfReferenceNode or self.peekedEntryType == EntryType.NamedStartOfStructNode):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.StartOfNode

        elif (self.peekedEntryType == EntryType.UnnamedStartOfReferenceNode or self.peekedEntryType == EntryType.UnnamedStartOfStructNode):
            name = None
            self.peekedEntryType = EntryType.StartOfNode

        elif (self.peekedEntryType == EntryType.EndOfNode):
            name = None
            self.peekedEntryType = EntryType.EndOfNode

        elif (self.peekedEntryType == EntryType.StartOfArray):
            name = None
            self.peekedEntryType = EntryType.StartOfArray

        elif (self.peekedEntryType == EntryType.EndOfArray):
            name = None
            self.peekedEntryType = EntryType.EndOfArray

        elif (self.peekedEntryType == EntryType.PrimitiveArray):
            name = None
            self.peekedEntryType = EntryType.PrimitiveArray

        elif (self.peekedEntryType == EntryType.NamedInternalReference):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.InternalReference

        elif (self.peekedEntryType == EntryType.UnnamedInternalReference):
            name = None
            self.peekedEntryType = EntryType.InternalReference

        elif (self.peekedEntryType == EntryType.NamedExternalReferenceByIndex):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.ExternalReferenceByIndex

        elif (self.peekedEntryType == EntryType.UnnamedExternalReferenceByIndex):
            name = None
            self.peekedEntryType = EntryType.ExternalReferenceByIndex

        elif (self.peekedEntryType == EntryType.NamedExternalReferenceByGuid):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.ExternalReferenceByGuid

        elif (self.peekedEntryType == EntryType.UnnamedExternalReferenceByGuid):
            name = None
            self.peekedEntryType = EntryType.ExternalReferenceByGuid

        elif (self.peekedEntryType == EntryType.NamedExternalReferenceByString):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.ExternalReferenceByString

        elif (self.peekedEntryType == EntryType.UnnamedExternalReferenceByString):
            name = None
            self.peekedEntryType = EntryType.ExternalReferenceByString

        elif (self.peekedEntryType == EntryType.NamedSByte):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedSByte):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedByte):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedByte):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedShort):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedShort):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedUShort):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedUShort):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedInt):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedInt):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedUInt):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedUInt):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedLong):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedLong):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedULong):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.UnnamedULong):
            name = None
            self.peekedEntryType = EntryType.Integer

        elif (self.peekedEntryType == EntryType.NamedFloat):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.FloatingPoint

        elif (self.peekedEntryType == EntryType.UnnamedFloat):
            name = None
            self.peekedEntryType = EntryType.FloatingPoint

        elif (self.peekedEntryType == EntryType.NamedDouble):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.FloatingPoint

        elif (self.peekedEntryType == EntryType.UnnamedDouble):
            name = None
            self.peekedEntryType = EntryType.FloatingPoint

        elif (self.peekedEntryType == EntryType.NamedDecimal):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.FloatingPoint

        elif (self.peekedEntryType == EntryType.UnnamedDecimal):
            name = None
            self.peekedEntryType = EntryType.FloatingPoint

        elif (self.peekedEntryType == EntryType.NamedChar):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.String

        elif (self.peekedEntryType == EntryType.UnnamedChar):
            name = None
            self.peekedEntryType = EntryType.String

        elif (self.peekedEntryType == EntryType.NamedString):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.String

        elif (self.peekedEntryType == EntryType.UnnamedString):
            name = None
            self.peekedEntryType = EntryType.String

        elif (self.peekedEntryType == EntryType.NamedGuid):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Guid

        elif (self.peekedEntryType == EntryType.UnnamedGuid):
            name = None
            self.peekedEntryType = EntryType.Guid

        elif (self.peekedEntryType == EntryType.NamedBoolean):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Boolean

        elif (self.peekedEntryType == EntryType.UnnamedBoolean):
            name = None
            self.peekedEntryType = EntryType.Boolean

        elif (self.peekedEntryType == EntryType.NamedNull):
            name = self.ReadStringValue()
            self.peekedEntryType = EntryType.Null

        elif (self.peekedEntryType == EntryType.UnnamedNull):
            name = None
            self.peekedEntryType = EntryType.Null

        elif (self.peekedEntryType == EntryType.TypeName or self.peekedEntryType == EntryType.TypeID):
            self.peekedEntryType = EntryType.Invalid

        else:
            name = None
            self.peekedEntryType = EntryType.Invalid

        self.peekedEntryName = name
        return self.peekedEntryType, self.peekedEntryName
    
    def SkipBuffer(self, amount:int) -> bool:
        newIndex = self.bufferIndex + amount
        if (newIndex > self.bufferEnd):
            self.bufferIndex = self.bufferEnd
            return False

        self.bufferIndex = newIndex
        return True
        
    def SkipPeekedEntryContent(self):
        if (self.peekedEntryType == EntryType.Unset):
            return
        
        if self.peekedEntryType == EntryType.NamedStartOfReferenceNode or self.peekedEntryType == EntryType.UnnamedStartOfReferenceNode:
            self.ReadTypeEntry()
            [success] = self.SkipBuffer(4)
            if (not success):
                return

        elif self.peekedEntryType == EntryType.NamedStartOfStructNode or self.peekedEntryType == EntryType.UnnamedStartOfStructNode:
            self.ReadTypeEntry()

        elif self.peekedEntryType == EntryType.StartOfArray:
            self.SkipBuffer(8)

        elif self.peekedEntryType == EntryType.PrimitiveArray:
            [success1, elements] = self.UNSAFE_Read_4_Int32()
            [success2, bytesPerElement] = self.UNSAFE_Read_4_Int32()
            if (not success1 or not success2):
                return

            self.SkipBuffer(elements * bytesPerElement)

        elif self.peekedEntryType == EntryType.NamedSByte or self.peekedEntryType == EntryType.UnnamedSByte or self.peekedEntryType == EntryType.NamedByte or self.peekedEntryType == EntryType.UnnamedByte or self.peekedEntryType == EntryType.NamedBoolean or self.peekedEntryType == EntryType.UnnamedBoolean or self.peekedEntryType == EntryType.Boolean:
            self.SkipBuffer(1)

        elif self.peekedEntryType == EntryType.NamedChar or self.peekedEntryType == EntryType.UnnamedChar or self.peekedEntryType == EntryType.NamedShort or self.peekedEntryType == EntryType.UnnamedShort or self.peekedEntryType == EntryType.NamedUShort or self.peekedEntryType == EntryType.UnnamedUShort:
            self.SkipBuffer(2)

        elif self.peekedEntryType == EntryType.NamedInternalReference or self.peekedEntryType == EntryType.UnnamedInternalReference or self.peekedEntryType == EntryType.NamedInt or self.peekedEntryType == EntryType.UnnamedInt or self.peekedEntryType == EntryType.NamedUInt or self.peekedEntryType == EntryType.UnnamedUInt or self.peekedEntryType == EntryType.NamedExternalReferenceByIndex or self.peekedEntryType == EntryType.UnnamedExternalReferenceByIndex or self.peekedEntryType == EntryType.NamedFloat or self.peekedEntryType == EntryType.UnnamedFloat or self.peekedEntryType == EntryType.FloatingPoint or self.peekedEntryType == EntryType.Integer:
            self.SkipBuffer(4)

        elif self.peekedEntryType == EntryType.NamedLong or self.peekedEntryType == EntryType.UnnamedLong or self.peekedEntryType == EntryType.NamedULong or self.peekedEntryType == EntryType.UnnamedULong or self.peekedEntryType == EntryType.NamedDouble or self.peekedEntryType == EntryType.UnnamedDouble:
            self.SkipBuffer(8)

        elif self.peekedEntryType == EntryType.NamedGuid or self.peekedEntryType == EntryType.UnnamedGuid or self.peekedEntryType == EntryType.NamedExternalReferenceByGuid or self.peekedEntryType == EntryType.UnnamedExternalReferenceByGuid or self.peekedEntryType == EntryType.NamedDecimal or self.peekedEntryType == EntryType.UnnamedDecimal or self.peekedEntryType == EntryType.Guid:
            self.SkipBuffer(8)

        elif self.peekedEntryType == EntryType.NamedString or self.peekedEntryType == EntryType.UnnamedString or self.peekedEntryType == EntryType.NamedExternalReferenceByString or self.peekedEntryType == EntryType.UnnamedExternalReferenceByString or self.peekedEntryType == EntryType.String:
            self.SkipStringValue()

        elif self.peekedEntryType == EntryType.TypeName:
            print("Parsing error in binary data reader: should not be able to peek a TypeName entry.")
            self.SkipBuffer(4)
            self.ReadStringValue()

        elif self.peekedEntryType == EntryType.TypeID:
            print("Parsing error in binary data reader: should not be able to peek a TypeID entry.")
            self.SkipBuffer(4)
        
        self.MarkEntryContentConsumed()
    
    def ReadToNextEntry(self) -> EntryType:
        self.SkipPeekedEntryContent()
        return self.PeekEntry()
    
    def SkipEntry(self):
        peekedEntry = self.PeekEntry()

        if (peekedEntry == EntryType.StartOfNode):
            [success, _] = self.EnterNode()

            if (success):
                self.ReadValueWeak()
            else:
                while (True):
                    peekedEntry = self.PeekEntry()
                    if (peekedEntry == EntryType.EndOfStream):
                        break
                    elif (peekedEntry == EntryType.EndOfNode):
                        break
                    elif (peekedEntry == EntryType.EndOfArray):
                        self.ReadToNextEntry()
                    else:
                        self.SkipEntry()
            
            self.ExitNode()
        
        elif (peekedEntry == EntryType.StartOfArray):
            self.ReadToNextEntry()
            while (True):
                peekedEntry = self.PeekEntry()
                if (peekedEntry == EntryType.EndOfStream):
                    break
                elif (peekedEntry == EntryType.EndOfArray):
                    self.ReadToNextEntry()
                elif (peekedEntry == EntryType.EndOfNode):
                    self.ReadToNextEntry()
                else:
                    self.SkipEntry()
        
        elif (peekedEntry != EntryType.EndOfArray and peekedEntry != EntryType.EndOfNode):
            self.ReadToNextEntry()
    
    def MarkEntryContentConsumed(self):
        self.peekedEntryType = EntryType.Unset
        self.peekedEntryName = None
    
    def ReadTypeEntry(self) -> tuple[EntryType, any]:
        if (not self.HasBufferData(1)):
            return None, None

        entryType = EntryType(self.buffer[self.bufferIndex])
        self.bufferIndex += 1

        if (entryType == EntryType.TypeID):
            [success, id] = self.UNSAFE_Read_4_Int32()
            if (not success):
                return entryType, None
            return entryType, id
        
        elif (entryType == EntryType.TypeName):
            [success, id] = self.UNSAFE_Read_4_Int32()
            if (not success):
                return entryType, None

            return entryType, self.ReadStringValue()

        elif (entryType == EntryType.UnnamedNull):
            return entryType, None

        else:
            print("Expected TypeName, TypeID or UnnamedNull entry flag for reading type data, but instead got the entry flag: " + str(entryType) + ".")
            return entryType, None
    
    def EnterNode(self) -> tuple[bool, EntryType]:
        if (self.peekedEntryType == EntryType.Unset):
            self.PeekEntry()

        if (self.peekedEntryType == EntryType.NamedStartOfReferenceNode or self.peekedEntryType == EntryType.UnnamedStartOfReferenceNode or self.peekedEntryType == EntryType.StartOfNode):
            self.MarkEntryContentConsumed()
            [type, _] = self.ReadTypeEntry()
            [success, id] = self.UNSAFE_Read_4_Int32()

            if (not success):
                return False, None

            self.PushNode(self.peekedEntryName, id, type)
            return True, type
        
        elif (self.peekedEntryType == EntryType.NamedStartOfStructNode or self.peekedEntryType == EntryType.UnnamedStartOfStructNode):
            [type, _] = self.ReadTypeEntry()
            self.PushNode(self.peekedEntryName, -1, type)
            self.MarkEntryContentConsumed()
            return True, type
        
        else:
            self.SkipEntry()
            return False, None
    
    def ExitNode(self) -> bool:
        if (self.peekedEntryType == EntryType.Unset):
            self.PeekEntry()

        while (self.peekedEntryType != EntryType.EndOfNode and self.peekedEntryType != EntryType.EndOfStream):
            if (self.peekedEntryType == EntryType.EndOfArray):
                print("Data layout mismatch skipping past array boundary when exiting node.")
                self.MarkEntryContentConsumed()

            self.SkipEntry()

        if (self.peekedEntryType == EntryType.EndOfNode):
            self.MarkEntryContentConsumed()
            self.PopNode(self.CurrentNodeName)
            return True

        return False
    
    def EnterArray(self) -> tuple[bool, int]:
        if (self.peekedEntryType == EntryType.Unset):
            self.PeekEntry()

        if (self.peekedEntryType == EntryType.StartOfArray):
            self.PushArray()
            self.MarkEntryContentConsumed()
            [success, length] = self.UNSAFE_Read_8_Int64()
            if (success):
                if (length < 0):
                    print("Invalid array length: " + length + ".")
                    return False, 0
                
                else: return True, length
            else: return False, 0
        
        else:
            self.SkipEntry()
            return False, 0

    def ExitArray(self) -> bool:
        if (self.peekedEntryType == EntryType.Unset):
            self.PeekEntry()

        while (self.peekedEntryType != EntryType.EndOfArray and self.peekedEntryType != EntryType.EndOfStream):
            if (self.peekedEntryType == EntryType.EndOfNode):
                print("Data layout mismatch skipping past node boundary when exiting array.")
                self.MarkEntryContentConsumed()

            self.SkipEntry()

        if (self.peekedEntryType == EntryType.EndOfArray):
            self.MarkEntryContentConsumed()
            self.PopArray()
            return True

        return False

    def PushNode(self, name:str, id:int, type:EntryType):
        if (self.nodesLength == len(self.nodes)):
            self.ExpandNodes()
        
        self.nodes[self.nodesLength] = NodeInfo(name, id, type, False)
        self.nodesLength += 1

    def PushArray(self):
        if (self.nodesLength == len(self.nodes)):
            self.ExpandNodes()

        if (self.nodesLength == 0 or self.nodes[self.nodesLength - 1].IsArray):
            self.nodes[self.nodesLength] = NodeInfo(None, -1, None, True)
        else:
            current = self.nodes[self.nodesLength - 1]
            self.nodes[self.nodesLength] = NodeInfo(current.Name, current.Id, current.Type, True)
        
        self.nodesLength += 1

    def ExpandNodes(self):
        newArr = NodeInfo[len(self.nodes) * 2]
        oldNodes = self.nodes
        for i in range(0, len(oldNodes)):
            newArr[i] = oldNodes[i]
        self.nodes = newArr

    def PopNode(self, name:str):
        self.nodesLength -= 1

    def PopArray(self):
        self.nodesLength -= 1
    
    def ReadStringValue(self):
        [success, charSizeFlag] = self.UNSAFE_Read_1_Byte()
        if (not success):
            return None
        
        [success, length] = self.UNSAFE_Read_4_Int32()
        if (not success):
            return None

        str = ''

        # 8 bit
        if (charSizeFlag == 0):
            if (self.IsLittleEndian):
                r = range(1, int(length / 2))
            else:
                r = range(0, int(length / 2))

            # Skip every other string byte
            start = self.bufferIndex
            end = start + length
            str = self.buffer[start:end][::2].decode('utf-8')
            self.bufferIndex = end
            return str
        
        # 16 bit
        else:
            length *= 2
            start = self.bufferIndex
            end = start + length
            str = self.buffer[start:end].decode('utf-16')
            self.bufferIndex = end
            return str
        
    def ReadExternalReference(self) -> tuple[bool, str]:
        if (self.peekedEntryType == EntryType.Unset):
            self.PeekEntry()

        if (self.peekedEntryType == EntryType.NamedExternalReferenceByGuid or self.peekedEntryType == EntryType.UnnamedExternalReferenceByGuid or self.peekedEntryType == EntryType.ExternalReferenceByGuid):
            self.MarkEntryContentConsumed()
            return self.UNSAFE_Read_16_Guid()
        elif (self.peekedEntryType == EntryType.ExternalReferenceByIndex or self.peekedEntryType == EntryType.NamedExternalReferenceByIndex or self.peekedEntryType == EntryType.UnnamedExternalReferenceByIndex):
            self.MarkEntryContentConsumed()
            return self.UNSAFE_Read_4_Int32()
        else:
            self.SkipEntry()
            return False, '00000000000000000000000000000000'
    
    def ReadInt64(self) -> tuple[bool, int]:
        if (self.peekedEntryType == EntryType.Unset):
            self.PeekEntry()
        
        try:
            if self.peekedEntryType == EntryType.NamedSByte or self.peekedEntryType == EntryType.UnnamedSByte:
                [success, value] = self.UNSAFE_Read_1_SByte()
                if (success):
                    return True, value
                else:
                    return False, 0
            elif self.peekedEntryType == EntryType.NamedByte or self.peekedEntryType == EntryType.UnnamedByte:
                [success, value] = self.UNSAFE_Read_1_Byte()
                if (success):
                    return True, value
                else:
                    return False, 0

            elif self.peekedEntryType == EntryType.NamedShort or self.peekedEntryType == EntryType.UnnamedShort:
                [success, value] = self.UNSAFE_Read_2_Int16()
                if (success):
                    return True, value
                else:
                    return False, 0

            elif self.peekedEntryType == EntryType.NamedUShort or self.peekedEntryType == EntryType.UnnamedUShort:
                [success, value] = self.UNSAFE_Read_2_UInt16()
                if (success):
                    return True, value
                else:
                    return False, 0

            elif self.peekedEntryType == EntryType.NamedInt or self.peekedEntryType == EntryType.UnnamedInt or self.peekedEntryType == EntryType.Integer:
                [success, value] = self.UNSAFE_Read_4_Int32()
                if (success):
                    return True, value
                else:
                    return False, 0

            elif self.peekedEntryType == EntryType.NamedUInt or self.peekedEntryType == EntryType.UnnamedUInt:
                [success, value] = self.UNSAFE_Read_4_UInt32()
                if (success):
                    return True, value
                else:
                    return False, 0

            elif self.peekedEntryType == EntryType.NamedLong or self.peekedEntryType == EntryType.UnnamedLong:
                [success, value] = self.UNSAFE_Read_8_Int64()
                if (success):
                    return True, value
                else:
                    return False, 0

            elif self.peekedEntryType == EntryType.NamedULong or self.peekedEntryType == EntryType.UnnamedULong:
                [success, value] = self.UNSAFE_Read_8_UInt64()
                if (success):
                    return True, value
                else:
                    return False, 0

            else:        
                self.SkipEntry()
                return False, 0
        finally:
            self.MarkEntryContentConsumed()

    def UNSAFE_Read_1_Byte(self) -> tuple[bool, int]:
        if (self.HasBufferData(1)):
            self.bufferIndex += 1
            return True, self.buffer[self.bufferIndex - 1]
        return False, 0

    def UNSAFE_Read_4_Int32(self) -> tuple[bool, int]:
        if (not self.HasBufferData(4)):
            self.bufferIndex = self.bufferEnd
            return False, 0
        
        value = 0
        start = self.bufferIndex
        end = start + 4
        if (self.IsLittleEndian):
            value = int.from_bytes(self.buffer[start:end], byteorder='little', signed=True)
        else:
            value = int.from_bytes(self.buffer[start:end], byteorder='big', signed=True)
        
        self.bufferIndex = end
        return True, value
        
    def UNSAFE_Read_8_Int64(self) -> tuple[bool, int]:
        if (not self.HasBufferData(8)):
            self.bufferIndex = self.bufferEnd
            return False, 0
        
        value = 0
        start = self.bufferIndex
        end = start + 8
        if (self.IsLittleEndian):
            value = int.from_bytes(self.buffer[start:end], byteorder='little', signed=True)
        else:
            value = int.from_bytes(self.buffer[start:end], byteorder='big', signed=True)

        self.bufferIndex = end
        return True, value
    
    def UNSAFE_Read_16_Guid(self) -> tuple[bool, str]:
        if (not self.HasBufferData(16)):
            self.bufferIndex = self.bufferEnd
            return False, '00000000000000000000000000000000'
        
        start = self.bufferIndex
        end = start + 16
        str = self.buffer[start:end].decode('utf-8')
        self.bufferIndex = end
        return True, str

    def ReadValueWeak(self, output:dict):
        if (self.bufferIndex >= self.bufferEnd):
            return None, None, None
        
        value = None
        [entry, name] = self.PeekEntry()
        if (not name):
            name = 0
        
        if (entry == EntryType.Null):
            self.ReadNull()

        elif (entry == EntryType.ExternalReferenceByIndex):
            [_, index] = self.ReadExternalReference()
            value = self.lookupExternalReference(index, lookupExternalReference_type.index)

        elif (entry == EntryType.ExternalReferenceByGuid):
            [_, guid] = self.ReadExternalReference()
            value = self.lookupExternalReference(guid, lookupExternalReference_type.guid)

        elif (entry == EntryType.ExternalReferenceByString):
            [_, id] = self.ReadExternalReference()
            value = self.lookupExternalReference(id, lookupExternalReference_type.id)

        elif (entry == EntryType.InternalReference):
            [_, id] = self.ReadInternalReference()
            value = self.GetInternalReference(id)

        elif (entry == EntryType.StartOfNode):
            [success, _] = self.EnterNode()
            if (success):
                innerEntry = entry
                output[name] = {}
                for i in range (0, 999):
                    if (EntryType(self.buffer[self.bufferIndex]) == EntryType.EndOfNode):
                        break

                    output[name][i] = {}
                    [innerValue, innerEntry, innerName] = self.ReadValueWeak(output[name][i])

                    # Sometimes invalid shit ends up in here
                    while (innerEntry == EntryType.Invalid):
                        [innerValue, innerEntry, innerName] = self.ReadValueWeak(output[name][i])

                    innerList = list(output[name][i].values())
                    if (innerName and innerValue):
                        del output[name][i]
                        output[name][innerName] = innerValue
                    elif (innerValue and not output[name][i]):
                        output[name][i] = innerValue
                    elif (len(innerList) == 1):
                        output[name][i] = innerList[0]
                    elif (len(innerList) < 1):
                        del output[name][i]
                
                if (len(output[name]) == 1):
                    output[name] = list(output[name].values())[0]
                
                self.ExitNode()
                return value, entry, name
            else:
                print("Failed to enter node '" + name + "'.")
            self.ExitNode()

        elif (entry == EntryType.StartOfArray):
            [success, length] = self.EnterArray()
            if (success):
                output[name] = [None] * length
                for i in range (0, length):
                    if (EntryType(self.buffer[self.bufferIndex]) == EntryType.EndOfArray):
                        break

                    output[name][i] = {}
                    [innerValue, innerEntry, innerName] = self.ReadValueWeak(output[name][i])

                    # Sometimes invalid shit ends up in here
                    while (innerEntry == EntryType.Invalid):
                        [innerValue, innerEntry, innerName] = self.ReadValueWeak(output[name][i])

                    innerList = list(output[name][i].values())
                    if (innerValue and not output[name][i]):
                        output[name][i] = innerValue
                    elif (len(innerList) == 1):
                        output[name][i] = innerList[0]
                    elif (len(innerList) < 1):
                        del output[name][i]
                
                if (len(output[name]) == 1):
                    output[name] = list(output[name].values())[0]
                
                self.ExitArray()
                return value, entry, name
            
            else:
                print("Failed to enter array '" + name + "'.")
            self.ExitArray()
        
        elif (entry == EntryType.Boolean):
            value = self.ReadBoolean()

        elif (entry == EntryType.FloatingPoint):
            value = self.ReadDouble()

        elif (entry == EntryType.Integer):
            [_, value] = self.ReadInt64()

        elif (entry == EntryType.String):
            value = self.ReadString()

        elif (entry == EntryType.Guid):
            value = self.ReadGuid()
        
        elif (entry == EntryType.EndOfStream):
            value = ''

        else:
            self.SkipEntry()
        
        return value, entry, name

    def parse(self) -> dict:
        value = {}
        [innerValue, entryType, _] = self.ReadValueWeak(value)
        while (entryType != EntryType.EndOfNode and entryType != EntryType.EndOfArray and entryType != EntryType.EndOfStream and self.bufferIndex < self.bufferEnd):
            [innerValue, entryType, _] = self.ReadValueWeak(value)
        
        while (len(value) == 1):
            value = list(value.values())[0]
        
        return value

# This is just an example - ideally it would look up the index then guid properly
def lookupExternalReference_exploration(val:str|int, type:lookupExternalReference_type):
    if (type == lookupExternalReference_type.index):
        return [
            # - {fileID: 11400000, guid: 6f0516996260c4a45b5164d0a52806b9, type: 2}
            'Stone',

            # - {fileID: 11400000, guid: 8a5cbc0a8856cf14d88d38897fe4b6c8, type: 2}
            'Mana',

            # - {fileID: 11400000, guid: 240424be298cf9e4cb302853f12bb425, type: 2}
            'Mushroom',

            # - {fileID: 11400000, guid: c3769028894733f41954ed09308de302, type: 2}
            'Sand Dollar',

            # - {fileID: 11400000, guid: 918c1933186f4aa42ab8330164720e25, type: 2}
            'Log',

            # - {fileID: 11400000, guid: 63bc98a48e34ee6439559a21a5f86750, type: 2}
            'Seaweed',

            # - {fileID: 11400000, guid: 7552890e242d7ba41af297c94732b55a, type: 2}
            'Apple',

            # - {fileID: 11400000, guid: c38f639119cc69140bc232bb237e942c, type: 2}
            'Blueberry',

            # - {fileID: 11400000, guid: 0007b2926c970464c9db529019dd6f87, type: 2}
            'Strawberry',

            # - {fileID: 11400000, guid: 95a4b2e24f4c4ef439730697210c2a3d, type: 2}
            'Orange',

            # - {fileID: 11400000, guid: f31d8231625470a439f011523357b02d, type: 2}
            'Clam'
        ][val]


def lookupExternalReference_farming(val:str|int, type:lookupExternalReference_type):
    if (type == lookupExternalReference_type.index):
        return [
            # - {fileID: 11400000, guid: 6f0516996260c4a45b5164d0a52806b9, type: 2}
            'Stone',

            # - {fileID: 11400000, guid: 8a5cbc0a8856cf14d88d38897fe4b6c8, type: 2}
            'Mana',

            # - {fileID: 11400000, guid: 137f5f1e6fb4100459edba7617168833, type: 2}
            'Wheat',

            # - {fileID: 11400000, guid: d709db72fa7611d44b59e1c7793dcb5c, type: 2}
            'Potato',

            # - {fileID: 11400000, guid: 7b20e2d05650a464faa7a42b32484232, type: 2}
            'Lettuce',

            # - {fileID: 11400000, guid: 1d1fbe585c5e38046a4a47b297cd43b3, type: 2}
            'Carrot',

            # - {fileID: 11400000, guid: 633c39cee4d8609459bd5c5c7e92516c, type: 2}
            'Tomato',

            # - {fileID: 11400000, guid: 0ae531686b6a1a2498a64b770262ed94, type: 2}
            'Onion',

            # - {fileID: 11400000, guid: 895b3d112d12118448c229052ce55651, type: 2}
            'Rice',

            # - {fileID: 11400000, guid: 81d9cf4e4d3d58e48a7c47d1d982863e, type: 2}
            'Pepper',

            # - {fileID: 11400000, guid: 96896c4101540fe409b77637f7951175, type: 2}
            'Shimmeroot'
        ][val]


def lookupExternalReference_mining(val:str|int, type:lookupExternalReference_type):
    if (type == lookupExternalReference_type.index):
        return [
            # - {fileID: 11400000, guid: 6f0516996260c4a45b5164d0a52806b9, type: 2}
            'Stone',

            # - {fileID: 11400000, guid: 8a5cbc0a8856cf14d88d38897fe4b6c8, type: 2}
            'Mana',

            # - {fileID: 11400000, guid: f0ba0d69eb56f804d84bf6b4a9899241, type: 2}
            'Coal',

            # - {fileID: 11400000, guid: d7aff8306b022e645a8ef108db9da027, type: 2}
            'Copper Ore',

            # - {fileID: 11400000, guid: 155d40f643606664e904b0f81923ddd8, type: 2}
            'Iron Ore',

            # - {fileID: 11400000, guid: 61c84bc8461eb464eb89aa4b14bd4cbe, type: 2}
            'Adamant Ore',

            # - {fileID: 11400000, guid: a7f26d6e21ab419429a94ba525e68bf0, type: 2}
            'Gold Ore',

            # - {fileID: 11400000, guid: c2f5e06bfb030dd409a0bc3e3864da12, type: 2}
            'Sapphire',

            # - {fileID: 11400000, guid: f7ef2d21c841f234280708a531ee8e02, type: 2}
            'Ruby',

            # - {fileID: 11400000, guid: 52935e8a4d086974dbe3d2503070e6ad, type: 2}
            'Amethyst',

            # - {fileID: 11400000, guid: bd491cdcc4b9db644b6c3e2e957dbe1c, type: 2}
            'Diamond'
        ][val]


def lookupExternalReference_combat(val:str|int, type:lookupExternalReference_type):
    if (type == lookupExternalReference_type.index):
        return [
            # - {fileID: 11400000, guid: 6f0516996260c4a45b5164d0a52806b9, type: 2}
            'Stone',

            # - {fileID: 11400000, guid: 8a5cbc0a8856cf14d88d38897fe4b6c8, type: 2}
            'Mana',

            # - {fileID: 11400000, guid: 9e8fb36a374869f4d906a716c00afda8, type: 2}
            'Leafie\'s Leaf',

            # - {fileID: 11400000, guid: 0103286953ec5f844817c4537a42e8b8, type: 2}
            'Hot Sauce',

            # - {fileID: 11400000, guid: d5019577e294467499d6ca576218abad, type: 2}
            'Haunted Log',

            # - {fileID: 11400000, guid: a7dcc8c84c1d60042abc281f6bb60348, type: 2}
            'Prickletot Pear',

            # - {fileID: 11400000, guid: 5d2ea8b216f3616428bc3a0e500b7737, type: 2}
            'Bug Shell',

            # - {fileID: 11400000, guid: 0f3f35da95a50fe42a8e343f2ce30309, type: 2}
            'Squashed Banana',

            # - {fileID: 11400000, guid: 23f3d98c9c1d9a940b67466e21ba793f, type: 2}
            'Lightning in a Bottle',

            # - {fileID: 11400000, guid: e6b22263fffc8794a959bf1d9eae6de6, type: 2}
            'Pricklepop Pear'
        ][val]


def lookupExternalReference_fish(val:str|int, type:lookupExternalReference_type):
    if (type == lookupExternalReference_type.index):
        return [
            # - {fileID: 11400000, guid: 6f0516996260c4a45b5164d0a52806b9, type: 2}
            'Stone',

            # - {fileID: 11400000, guid: 8a5cbc0a8856cf14d88d38897fe4b6c8, type: 2}
            'Mana',

            # - {fileID: 11400000, guid: d87dcb5f918367b4784c34f8a641adcd, type: 2}
            'Dorado',

            # - {fileID: 11400000, guid: 708220e78ceadc14594cbe219d20fcc8, type: 2}
            'Duorado',

            # - {fileID: 11400000, guid: 7a7b08657c772534ca6acf1f3909fa1e, type: 2}
            'Crab',

            # - {fileID: 11400000, guid: 49686d0e804fcbc499e91662cd9ce709, type: 2}
            'Lobster',

            # - {fileID: 11400000, guid: 4ffce8d338b52b34dbdf5acef9617938, type: 2}
            'Gold Boot',

            # - {fileID: 11400000, guid: bbbb63424a5451e4c9996f5aebbc5fee, type: 2}
            'Old Boot',

            # - {fileID: 11400000, guid: 1236d6b75e9e9ce4e9ed747a772ad8c3, type: 2}
            'Devilfin',

            # - {fileID: 11400000, guid: 1de6bbbf271f9de408600f3700d60642, type: 2}
            'Sea Bass',

            # - {fileID: 11400000, guid: b54eaa9d38009124393768b7c4c90485, type: 2}
            'Angelfin',

            # - {fileID: 11400000, guid: b51f4ecd3ab0ec54b8adb172ec8ea376, type: 2}
            'Bubblefish',

            # - {fileID: 11400000, guid: accf813bfd09b174799e7f5a7fec799e, type: 2}
            'Chromafin',

            # - {fileID: 11400000, guid: ba0e9e4e0e23027468d6950199f7bc2c, type: 2}
            'Shadow Tuna'
        ][val]


# Print in wiki table format
def printRecipes(recipes:list[list[dict]]):
    for recipe in recipes:
        ingredientsStr = ''
        for ingredient in recipe:
            if (ingredient != recipe[0]):
                ingredientsStr += '; '
            ingredientsStr += ingredient['item'] + '*' + str(ingredient['amount'])
        print('{{Recipe\n|recipesource = Skill:Tomes of Skill\n|workbench    = Anvil\n|ingredients  = ' + ingredientsStr + '\n|time         = 15m\n|yield        = }}')

# USAGE:
# Inside e.g. Recipe 18103 - Combat Skill Tome.asset there's a node called "serializationData".
# Inside this node the important parts are "SerializedBytes" and "ReferencedUnityObjects"
# Pass in SerializedBytes as a string as the first parameter, and pass in a function that looks up the ReferencedUnityObjects by index as a second parameter
#
# This is an example of usage - you just pass in the serialized string and a function to look up the GUID references
# Theoretically this could be used for other data
print('\n\n\n====================\n=   Exploration    =\n====================')
printRecipes(SkillTomeParser(
    '01010b000000720061006e0064006f006d0049006e007000750074002f00000000017a000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b00530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c00690062005d005d002c0020006d00730063006f0072006c006900620000000000060a00000000000000022f01000000014b000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c006900620001000000060200000000000000022f02000000011c00000057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f0072006500020000000b01040000006900740065006d000000000017010600000061006d006f0075006e007400e703000005023002000000030000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000004000000060200000000000000023002000000050000000b01040000006900740065006d000200000017010600000061006d006f0075006e0074002800000005023002000000060000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000007000000060200000000000000023002000000080000000b01040000006900740065006d000300000017010600000061006d006f0075006e0074002800000005023002000000090000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000a0000000602000000000000000230020000000b0000000b01040000006900740065006d000400000017010600000061006d006f0075006e00740058020000050230020000000c0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000d0000000602000000000000000230020000000e0000000b01040000006900740065006d000500000017010600000061006d006f0075006e00740028000000050230020000000f0000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000010000000060200000000000000023002000000110000000b01040000006900740065006d000600000017010600000061006d006f0075006e0074006400000005023002000000120000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000013000000060200000000000000023002000000140000000b01040000006900740065006d000700000017010600000061006d006f0075006e0074005000000005023002000000150000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000016000000060200000000000000023002000000170000000b01040000006900740065006d000800000017010600000061006d006f0075006e0074004600000005023002000000180000000b01040000006900740065006d000100000017010600000061006d006f0075006e00740064000000050705023001000000190000000602000000000000000230020000001a0000000b01040000006900740065006d000900000017010600000061006d006f0075006e00740050000000050230020000001b0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000001c0000000602000000000000000230020000001d0000000b01040000006900740065006d000a00000017010600000061006d006f0075006e00740028000000050230020000001e0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050705',
    lookupExternalReference_exploration
).parse())

print('\n\n\n====================\n=     Farming      =\n====================')
printRecipes(SkillTomeParser(
    '01010b000000720061006e0064006f006d0049006e007000750074002f00000000017a000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b00530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c00690062005d005d002c0020006d00730063006f0072006c006900620000000000060a00000000000000022f01000000014b000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c006900620001000000060200000000000000022f02000000011c00000057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f0072006500020000000b01040000006900740065006d000000000017010600000061006d006f0075006e007400e703000005023002000000030000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000004000000060200000000000000023002000000050000000b01040000006900740065006d000200000017010600000061006d006f0075006e0074007800000005023002000000060000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000007000000060200000000000000023002000000080000000b01040000006900740065006d000300000017010600000061006d006f0075006e0074006400000005023002000000090000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000a0000000602000000000000000230020000000b0000000b01040000006900740065006d000400000017010600000061006d006f0075006e00740050000000050230020000000c0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000d0000000602000000000000000230020000000e0000000b01040000006900740065006d000500000017010600000061006d006f0075006e0074005a000000050230020000000f0000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000010000000060200000000000000023002000000110000000b01040000006900740065006d000600000017010600000061006d006f0075006e0074005a00000005023002000000120000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000013000000060200000000000000023002000000140000000b01040000006900740065006d000700000017010600000061006d006f0075006e0074005a00000005023002000000150000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000016000000060200000000000000023002000000170000000b01040000006900740065006d000800000017010600000061006d006f0075006e0074006400000005023002000000180000000b01040000006900740065006d000100000017010600000061006d006f0075006e00740064000000050705023001000000190000000602000000000000000230020000001a0000000b01040000006900740065006d000900000017010600000061006d006f0075006e00740050000000050230020000001b0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000001c0000000602000000000000000230020000001d0000000b01040000006900740065006d000a00000017010600000061006d006f0075006e00740032000000050230020000001e0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050705',
    lookupExternalReference_farming
).parse())

print('\n\n\n====================\n=     Mining       =\n====================')
printRecipes(SkillTomeParser(
    '01010b000000720061006e0064006f006d0049006e007000750074002f00000000017a000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b00530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c00690062005d005d002c0020006d00730063006f0072006c006900620000000000060a00000000000000022f01000000014b000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c006900620001000000060200000000000000022f02000000011c00000057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f0072006500020000000b01040000006900740065006d000000000017010600000061006d006f0075006e007400e703000005023002000000030000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000004000000060200000000000000023002000000050000000b01040000006900740065006d000200000017010600000061006d006f0075006e0074003c00000005023002000000060000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000007000000060200000000000000023002000000080000000b01040000006900740065006d000300000017010600000061006d006f0075006e007400c800000005023002000000090000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000a0000000602000000000000000230020000000b0000000b01040000006900740065006d000400000017010600000061006d006f0075006e00740050000000050230020000000c0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000d0000000602000000000000000230020000000e0000000b01040000006900740065006d000500000017010600000061006d006f0075006e0074005a000000050230020000000f0000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000010000000060200000000000000023002000000110000000b01040000006900740065006d000600000017010600000061006d006f0075006e0074004b00000005023002000000120000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000013000000060200000000000000023002000000140000000b01040000006900740065006d000700000017010600000061006d006f0075006e0074003200000005023002000000150000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000016000000060200000000000000023002000000170000000b01040000006900740065006d000800000017010600000061006d006f0075006e0074002800000005023002000000180000000b01040000006900740065006d000100000017010600000061006d006f0075006e00740064000000050705023001000000190000000602000000000000000230020000001a0000000b01040000006900740065006d000900000017010600000061006d006f0075006e0074001e000000050230020000001b0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000001c0000000602000000000000000230020000001d0000000b01040000006900740065006d000a00000017010600000061006d006f0075006e00740019000000050230020000001e0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050705',
    lookupExternalReference_mining
).parse())

print('\n\n\n====================\n=      Combat      =\n====================')
printRecipes(SkillTomeParser(
    '01010b000000720061006e0064006f006d0049006e007000750074002f00000000017a000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b00530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c00690062005d005d002c0020006d00730063006f0072006c006900620000000000060900000000000000022f01000000014b000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c006900620001000000060200000000000000022f02000000011c00000057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f0072006500020000000b01040000006900740065006d000000000017010600000061006d006f0075006e007400e703000005023002000000030000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000004000000060200000000000000023002000000050000000b01040000006900740065006d000200000017010600000061006d006f0075006e0074005000000005023002000000060000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000007000000060200000000000000023002000000080000000b01040000006900740065006d000300000017010600000061006d006f0075006e0074005000000005023002000000090000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000a0000000602000000000000000230020000000b0000000b01040000006900740065006d000400000017010600000061006d006f0075006e00740050000000050230020000000c0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000d0000000602000000000000000230020000000e0000000b01040000006900740065006d000500000017010600000061006d006f0075006e00740050000000050230020000000f0000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000010000000060200000000000000023002000000110000000b01040000006900740065006d000600000017010600000061006d006f0075006e0074005000000005023002000000120000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000013000000060200000000000000023002000000140000000b01040000006900740065006d000700000017010600000061006d006f0075006e0074005000000005023002000000150000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000016000000060200000000000000023002000000170000000b01040000006900740065006d000800000017010600000061006d006f0075006e0074005000000005023002000000180000000b01040000006900740065006d000100000017010600000061006d006f0075006e00740064000000050705023001000000190000000602000000000000000230020000001a0000000b01040000006900740065006d000900000017010600000061006d006f0075006e00740050000000050230020000001b0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050705',
    lookupExternalReference_combat
).parse())

print('\n\n\n====================\n=     Fishing      =\n====================')
printRecipes(SkillTomeParser(
    '01010b000000720061006e0064006f006d0049006e007000750074002f00000000017a000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b00530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c00690062005d005d002c0020006d00730063006f0072006c006900620000000000060a00000000000000022f01000000014b000000530079007300740065006d002e0043006f006c006c0065006300740069006f006e0073002e00470065006e0065007200690063002e004c00690073007400600031005b005b0057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f00720065005d005d002c0020006d00730063006f0072006c006900620001000000060200000000000000022f02000000011c00000057006900730068002e004900740065006d0049006e0066006f002c002000530075006e0048006100760065006e002e0043006f0072006500020000000b01040000006900740065006d000000000017010600000061006d006f0075006e007400e703000005023002000000030000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000004000000060300000000000000023002000000050000000b01040000006900740065006d000200000017010600000061006d006f0075006e0074000a00000005023002000000060000000b01040000006900740065006d000300000017010600000061006d006f0075006e0074000a00000005023002000000070000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000008000000060300000000000000023002000000090000000b01040000006900740065006d000400000017010600000061006d006f0075006e0074000f000000050230020000000a0000000b01040000006900740065006d000500000017010600000061006d006f0075006e00740006000000050230020000000b0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000000c0000000603000000000000000230020000000d0000000b01040000006900740065006d000600000017010600000061006d006f0075006e00740002000000050230020000000e0000000b01040000006900740065006d000700000017010600000061006d006f0075006e00740004000000050230020000000f0000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000010000000060200000000000000023002000000110000000b01040000006900740065006d000800000017010600000061006d006f0075006e0074000200000005023002000000120000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000013000000060200000000000000023002000000140000000b01040000006900740065006d000900000017010600000061006d006f0075006e0074001400000005023002000000150000000b01040000006900740065006d000100000017010600000061006d006f0075006e0074006400000005070502300100000016000000060200000000000000023002000000170000000b01040000006900740065006d000a00000017010600000061006d006f0075006e0074000200000005023002000000180000000b01040000006900740065006d000100000017010600000061006d006f0075006e00740064000000050705023001000000190000000602000000000000000230020000001a0000000b01040000006900740065006d000b00000017010600000061006d006f0075006e00740002000000050230020000001b0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000001c0000000602000000000000000230020000001d0000000b01040000006900740065006d000c00000017010600000061006d006f0075006e00740002000000050230020000001e0000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050230010000001f000000060200000000000000023002000000200000000b01040000006900740065006d000d00000017010600000061006d006f0075006e0074000200000005023002000000210000000b01040000006900740065006d000100000017010600000061006d006f0075006e007400640000000507050705',
    lookupExternalReference_fish
).parse())