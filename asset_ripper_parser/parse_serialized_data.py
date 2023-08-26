from collections.abc import Callable
from enum import IntEnum
from typing import Any

from asset_ripper_parser.serialized_entry_type import (
    EntryType,
    NamedEntryType,
    UnnamedEntryType,
)


# This is the bare minimum amount of functions I could translate from C# to get this to run with the skill tomes
# This may break at some point, or not work with other files such as map data
# This code is based on
# https://github.com/TeamSirenix/odin-serializer/blob/master/OdinSerializer/Core/DataReaderWriters/Binary/BinaryDataReader.cs
class NodeInfo:
    name = ""
    node_id = 0
    node_type = ""
    is_array = False
    is_empty = False

    def __init__(
        self,
        name: str | None,
        node_id: int,
        node_type: Any,
        is_array: bool,
        is_empty=False,
    ):
        self.name = name
        self.node_id = node_id
        self.node_type = node_type
        self.is_array = is_array
        self.is_empty = is_empty


EmptyNodeInfo = NodeInfo(None, 0, None, False, is_empty=True)


class LookupRefType(IntEnum):
    GUID = 1
    INDEX = 2
    ID = 3
    NAME = 4


def blank_ref_lookup(ref: str | int, _: LookupRefType):
    return ref


class SkillTomeParser:
    buffer = bytearray()
    buffer_index = 0
    peeked_entry_type = EntryType.UNSET
    peeked_entry_name = ""
    buffer_end = 0
    is_little_endian = True
    nodes = [EmptyNodeInfo] * 32
    nodesLength = 0
    output = {}

    lookup_external_reference = blank_ref_lookup

    @property
    def current_node_id(self) -> int:
        return self.current_node.node_id

    @property
    def current_node_depth(self) -> int:
        return self.nodesLength

    @property
    def current_node_name(self) -> str:
        return self.current_node.name

    @property
    def current_node(self):
        if self.nodesLength == 0:
            return EmptyNodeInfo
        else:
            return self.nodes[self.nodesLength - 1]

    def __init__(
        self,
        serialized_bytes: str,
        lookup_external_reference: Callable[[str | int, LookupRefType], str],
    ):
        self.buffer = bytearray.fromhex(serialized_bytes)
        self.buffer_end = len(self.buffer)
        self.lookup_external_reference = lookup_external_reference

    def has_buffer_data(self, amount: int) -> bool:
        return self.buffer_index + amount <= self.buffer_end

    def peek_entry(self) -> tuple[EntryType, str]:
        if self.peeked_entry_type != EntryType.UNSET:
            return self.peeked_entry_type, self.peeked_entry_name

        if self.has_buffer_data(1):
            current_entry = self.buffer[self.buffer_index]
            if current_entry in list(EntryType):
                self.peeked_entry_type = EntryType(current_entry)
            elif current_entry in list(NamedEntryType):
                self.peeked_entry_type = NamedEntryType(current_entry)
            elif current_entry in list(UnnamedEntryType):
                self.peeked_entry_type = UnnamedEntryType(current_entry)
            self.buffer_index += 1
        else:
            self.peeked_entry_type = EntryType.STREAM_END

        name = None
        if self.peeked_entry_type == EntryType.STREAM_END:
            name = None
            self.peeked_entry_name = None
            self.peeked_entry_type = EntryType.STREAM_END

        elif (
            self.peeked_entry_type == NamedEntryType.NAMED_START_REF_NODE
            or self.peeked_entry_type == NamedEntryType.NAMED_START_STRUCT_NODE
        ):
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.NODE_START

        elif (
            self.peeked_entry_type == UnnamedEntryType.UNNAMED_START_REF_NODE
            or self.peeked_entry_type == UnnamedEntryType.UNNAMED_START_STRUCT_NODE
        ):
            name = None
            self.peeked_entry_type = EntryType.NODE_START

        elif self.peeked_entry_type in [
            EntryType.NODE_END,
            EntryType.ARRAY_START,
            EntryType.ARRAY_END,
            EntryType.PRIMITIVE_ARRAY,
        ]:
            name = None

        elif self.peeked_entry_type == NamedEntryType.NAMED_INTERNAL_REF:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.INTERNAL_REF

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_INTERNAL_REF:
            name = None
            self.peeked_entry_type = EntryType.INTERNAL_REF

        elif self.peeked_entry_type == NamedEntryType.NAMED_EXTERNAL_INDEX_REF:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.EXTERNAL_REF

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_EXTERNAL_INDEX_REF:
            name = None
            self.peeked_entry_type = EntryType.EXTERNAL_REF

        elif self.peeked_entry_type == NamedEntryType.NAMED_EXTERNAL_GUID_REF:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.EXTERNAL_REF_GUID

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_EXTERNAL_GUID_REF:
            name = None
            self.peeked_entry_type = EntryType.EXTERNAL_REF_GUID

        elif self.peeked_entry_type == NamedEntryType.NAMED_EXT_STRING_REF:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.EXTERNAL_REF_STRING

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_EXT_STRING_REF:
            name = None
            self.peeked_entry_type = EntryType.EXTERNAL_REF_STRING

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_SBYTE,
            NamedEntryType.NAMED_BYTE,
            NamedEntryType.NAMED_SHORT,
            NamedEntryType.NAMED_U_SHORT,
            NamedEntryType.NAMED_INT,
            NamedEntryType.NAMED_U_INT,
            NamedEntryType.NAMED_LONG,
            NamedEntryType.NAMED_U_LONG,
        ]:
            self.peeked_entry_type = EntryType.INTEGER
            name = self.read_string_value()

        elif self.peeked_entry_type in [
            UnnamedEntryType.UNNAMED_SBYTE,
            UnnamedEntryType.UNNAMED_BYTE,
            UnnamedEntryType.UNNAMED_SHORT,
            UnnamedEntryType.UNNAMED_U_SHORT,
            UnnamedEntryType.UNNAMED_INT,
            UnnamedEntryType.UNNAMED_U_INT,
            UnnamedEntryType.UNNAMED_LONG,
            UnnamedEntryType.UNNAMED_U_LONG,
        ]:
            self.peeked_entry_type = EntryType.INTEGER
            name = None

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_FLOAT,
            NamedEntryType.NAMED_DOUBLE,
            NamedEntryType.NAMED_DECIMAL,
        ]:
            self.peeked_entry_type = EntryType.FLOATING_POINT
            name = self.read_string_value()

        elif self.peeked_entry_type in [
            UnnamedEntryType.UNNAMED_FLOAT,
            UnnamedEntryType.UNNAMED_DOUBLE,
            UnnamedEntryType.UNNAMED_DECIMAL,
        ]:
            self.peeked_entry_type = EntryType.FLOATING_POINT
            name = None

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_CHAR,
            NamedEntryType.NAMED_STRING,
        ]:
            self.peeked_entry_type = EntryType.STRING
            name = self.read_string_value()

        elif self.peeked_entry_type in [
            UnnamedEntryType.UNNAMED_CHAR,
            UnnamedEntryType.UNNAMED_STRING,
        ]:
            self.peeked_entry_type = EntryType.STRING
            name = None

        elif self.peeked_entry_type == NamedEntryType.NAMED_GUID:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.GUID

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_GUID:
            name = None
            self.peeked_entry_type = EntryType.GUID

        elif self.peeked_entry_type == NamedEntryType.NAMED_BOOL:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.BOOLEAN

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_BOOL:
            name = None
            self.peeked_entry_type = EntryType.BOOLEAN

        elif self.peeked_entry_type == NamedEntryType.NAMED_NULL:
            name = self.read_string_value()
            self.peeked_entry_type = EntryType.NULL

        elif self.peeked_entry_type == UnnamedEntryType.UNNAMED_NULL:
            name = None
            self.peeked_entry_type = EntryType.NULL

        elif (
            self.peeked_entry_type == EntryType.TYPE_NAME
            or self.peeked_entry_type == EntryType.TYPE_ID
        ):
            self.peeked_entry_type = EntryType.INVALID

        else:
            name = None
            self.peeked_entry_type = EntryType.INVALID

        self.peeked_entry_name = name
        return self.peeked_entry_type, self.peeked_entry_name

    def skip_buffer(self, amount: int) -> bool:
        new_index = self.buffer_index + amount
        if new_index > self.buffer_end:
            self.buffer_index = self.buffer_end
            return False

        self.buffer_index = new_index
        return True

    def skip_peeked_entry_content(self):
        if self.peeked_entry_type == EntryType.UNSET:
            return

        if (
            self.peeked_entry_type == NamedEntryType.NAMED_START_REF_NODE
            or self.peeked_entry_type == UnnamedEntryType.UNNAMED_START_REF_NODE
        ):
            self.read_type_entry()
            success = self.skip_buffer(4)
            if not success:
                return

        elif (
            self.peeked_entry_type == NamedEntryType.NAMED_START_STRUCT_NODE
            or self.peeked_entry_type == UnnamedEntryType.UNNAMED_START_STRUCT_NODE
        ):
            self.read_type_entry()

        elif self.peeked_entry_type == EntryType.ARRAY_START:
            self.skip_buffer(8)

        elif self.peeked_entry_type == EntryType.PRIMITIVE_ARRAY:
            [success1, elements] = self.unsafe_read_4_int32()
            [success2, bytes_per_element] = self.unsafe_read_4_int32()
            if not success1 or not success2:
                return

            self.skip_buffer(elements * bytes_per_element)

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_SBYTE,
            UnnamedEntryType.UNNAMED_SBYTE,
            NamedEntryType.NAMED_BYTE,
            UnnamedEntryType.UNNAMED_BYTE,
            NamedEntryType.NAMED_BOOL,
            UnnamedEntryType.UNNAMED_BOOL,
            EntryType.BOOLEAN,
        ]:
            self.skip_buffer(1)

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_CHAR,
            UnnamedEntryType.UNNAMED_CHAR,
            NamedEntryType.NAMED_SHORT,
            UnnamedEntryType.UNNAMED_SHORT,
            NamedEntryType.NAMED_U_SHORT,
            UnnamedEntryType.UNNAMED_U_SHORT,
        ]:
            self.skip_buffer(2)

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_INTERNAL_REF,
            UnnamedEntryType.UNNAMED_INTERNAL_REF,
            NamedEntryType.NAMED_INT,
            UnnamedEntryType.UNNAMED_INT,
            NamedEntryType.NAMED_U_INT,
            UnnamedEntryType.UNNAMED_U_INT,
            NamedEntryType.NAMED_EXTERNAL_INDEX_REF,
            UnnamedEntryType.UNNAMED_EXTERNAL_INDEX_REF,
            NamedEntryType.NAMED_FLOAT,
            UnnamedEntryType.UNNAMED_FLOAT,
            EntryType.FLOATING_POINT,
            EntryType.INTEGER,
        ]:
            self.skip_buffer(4)

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_LONG,
            UnnamedEntryType.UNNAMED_LONG,
            NamedEntryType.NAMED_U_LONG,
            UnnamedEntryType.UNNAMED_U_LONG,
            NamedEntryType.NAMED_DOUBLE,
            UnnamedEntryType.UNNAMED_DOUBLE,
        ]:
            self.skip_buffer(8)

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_GUID,
            UnnamedEntryType.UNNAMED_GUID,
            NamedEntryType.NAMED_EXTERNAL_GUID_REF,
            UnnamedEntryType.UNNAMED_EXTERNAL_GUID_REF,
            NamedEntryType.NAMED_DECIMAL,
            UnnamedEntryType.UNNAMED_DECIMAL,
            EntryType.GUID,
        ]:
            self.skip_buffer(8)

        elif self.peeked_entry_type in [
            NamedEntryType.NAMED_STRING,
            UnnamedEntryType.UNNAMED_STRING,
            NamedEntryType.NAMED_EXT_STRING_REF,
            UnnamedEntryType.UNNAMED_EXT_STRING_REF,
            EntryType.STRING,
        ]:
            raise Exception("self.skip_string_value() not implemented")

        elif self.peeked_entry_type == EntryType.TYPE_NAME:
            print(
                "Parsing error in binary data reader: should not be able to peek a TypeName entry."
            )
            self.skip_buffer(4)
            self.read_string_value()

        elif self.peeked_entry_type == EntryType.TYPE_ID:
            print(
                "Parsing error in binary data reader: should not be able to peek a TypeID entry."
            )
            self.skip_buffer(4)

        self.mark_entry_content_consumed()

    def read_to_next_entry(self) -> EntryType:
        self.skip_peeked_entry_content()
        return self.peek_entry()

    def skip_entry(self):
        peeked_entry = self.peek_entry()

        if peeked_entry == EntryType.NODE_START:
            [success, _] = self.enter_node()

            if success:
                self.read_value_weak({})
            else:
                while True:
                    peeked_entry = self.peek_entry()
                    if peeked_entry == EntryType.STREAM_END:
                        break
                    elif peeked_entry == EntryType.NODE_END:
                        break
                    elif peeked_entry == EntryType.ARRAY_END:
                        self.read_to_next_entry()
                    else:
                        self.skip_entry()

            self.exit_node()

        elif peeked_entry == EntryType.ARRAY_START:
            self.read_to_next_entry()
            while True:
                peeked_entry = self.peek_entry()
                if peeked_entry == EntryType.STREAM_END:
                    break
                elif peeked_entry == EntryType.ARRAY_END:
                    self.read_to_next_entry()
                elif peeked_entry == EntryType.NODE_END:
                    self.read_to_next_entry()
                else:
                    self.skip_entry()

        elif peeked_entry != EntryType.ARRAY_END and peeked_entry != EntryType.NODE_END:
            self.read_to_next_entry()

    def mark_entry_content_consumed(self):
        self.peeked_entry_type = EntryType.UNSET
        self.peeked_entry_name = None

    def read_type_entry(self) -> tuple[EntryType | None, any]:
        if not self.has_buffer_data(1):
            return None, None

        entry_type = EntryType(self.buffer[self.buffer_index])
        self.buffer_index += 1

        if entry_type == EntryType.TYPE_ID:
            [success, entry_id] = self.unsafe_read_4_int32()
            if not success:
                return entry_type, None
            return entry_type, entry_id

        elif entry_type == EntryType.TYPE_NAME:
            [success, entry_id] = self.unsafe_read_4_int32()
            if not success:
                return entry_type, None

            return entry_type, self.read_string_value()

        elif entry_type == UnnamedEntryType.UNNAMED_NULL:
            return entry_type, None

        else:
            print(
                "Expected TypeName, TypeID or UnnamedNull entry flag for reading type data, "
                f"but instead got the entry flag: {entry_type}."
            )
            return entry_type, None

    def enter_node(self) -> tuple[bool, EntryType | None]:
        if self.peeked_entry_type == EntryType.UNSET:
            self.peek_entry()

        if (
            self.peeked_entry_type == NamedEntryType.NAMED_START_REF_NODE
            or self.peeked_entry_type == UnnamedEntryType.UNNAMED_START_REF_NODE
            or self.peeked_entry_type == EntryType.NODE_START
        ):
            self.mark_entry_content_consumed()
            [entry_type, _] = self.read_type_entry()
            [success, entry_id] = self.unsafe_read_4_int32()

            if not success:
                return False, None

            self.push_node(self.peeked_entry_name, entry_id, entry_type)
            return True, entry_type

        elif (
            self.peeked_entry_type == NamedEntryType.NAMED_START_STRUCT_NODE
            or self.peeked_entry_type == UnnamedEntryType.UNNAMED_START_STRUCT_NODE
        ):
            [entry_type, _] = self.read_type_entry()
            self.push_node(self.peeked_entry_name, -1, entry_type)
            self.mark_entry_content_consumed()
            return True, entry_type

        else:
            self.skip_entry()
            return False, None

    def exit_node(self) -> bool:
        if self.peeked_entry_type == EntryType.UNSET:
            self.peek_entry()

        while (
            self.peeked_entry_type != EntryType.NODE_END
            and self.peeked_entry_type != EntryType.STREAM_END
        ):
            if self.peeked_entry_type == EntryType.ARRAY_END:
                print(
                    "Data layout mismatch skipping past array boundary when exiting node."
                )
                self.mark_entry_content_consumed()

            self.skip_entry()

        if self.peeked_entry_type == EntryType.NODE_END:
            self.mark_entry_content_consumed()
            self.pop_node(self.current_node_name)
            return True

        return False

    def enter_array(self) -> tuple[bool, int]:
        if self.peeked_entry_type == EntryType.UNSET:
            self.peek_entry()

        if self.peeked_entry_type == EntryType.ARRAY_START:
            self.push_array()
            self.mark_entry_content_consumed()
            [success, length] = self.unsafe_read_8_int64()
            if success:
                if length < 0:
                    print(f"Invalid array length: {length}.")
                    return False, 0

                return True, length
            return False, 0

        self.skip_entry()
        return False, 0

    def exit_array(self) -> bool:
        if self.peeked_entry_type == EntryType.UNSET:
            self.peek_entry()

        while (
            self.peeked_entry_type != EntryType.ARRAY_END
            and self.peeked_entry_type != EntryType.STREAM_END
        ):
            if self.peeked_entry_type == EntryType.NODE_END:
                print(
                    "Data layout mismatch skipping past node boundary when exiting array."
                )
                self.mark_entry_content_consumed()

            self.skip_entry()

        if self.peeked_entry_type == EntryType.ARRAY_END:
            self.mark_entry_content_consumed()
            self.pop_array()
            return True

        return False

    def push_node(self, name: str, entry_id: int, entry_type: EntryType):
        if self.nodesLength == len(self.nodes):
            self.expand_nodes()

        self.nodes[self.nodesLength] = NodeInfo(name, entry_id, entry_type, False)
        self.nodesLength += 1

    def push_array(self):
        if self.nodesLength == len(self.nodes):
            self.expand_nodes()

        if self.nodesLength == 0 or self.nodes[self.nodesLength - 1].is_array:
            self.nodes[self.nodesLength] = NodeInfo(None, -1, None, True)
        else:
            current = self.nodes[self.nodesLength - 1]
            self.nodes[self.nodesLength] = NodeInfo(
                current.name, current.node_id, current.node_type, True
            )

        self.nodesLength += 1

    def expand_nodes(self):
        new_arr = NodeInfo[len(self.nodes) * 2]
        old_nodes = self.nodes
        for i in range(0, len(old_nodes)):
            new_arr[i] = old_nodes[i]
        self.nodes = new_arr

    def pop_node(self, name: str):
        self.nodesLength -= 1

    def pop_array(self):
        self.nodesLength -= 1

    def read_string_value(self):
        [success, char_size_flag] = self.unsafe_read_1_byte()
        if not success:
            return None

        [success, length] = self.unsafe_read_4_int32()
        if not success:
            return None

        current_string = ""

        # 8 bit
        if char_size_flag == 0:
            if self.is_little_endian:
                char_range = range(1, int(length / 2))
            else:
                char_range = range(0, int(length / 2))

            # Skip every other string byte
            start = self.buffer_index
            end = start + length
            current_string = self.buffer[start:end][::2].decode("utf-8")
            self.buffer_index = end
            return current_string

        # 16 bit
        else:
            length *= 2
            start = self.buffer_index
            end = start + length
            current_string = self.buffer[start:end].decode("utf-16")
            self.buffer_index = end
            return current_string

    def read_external_reference(self) -> tuple[bool, str | int]:
        if self.peeked_entry_type == EntryType.UNSET:
            self.peek_entry()

        if self.peeked_entry_type in [
            NamedEntryType.NAMED_EXTERNAL_GUID_REF,
            UnnamedEntryType.UNNAMED_EXTERNAL_GUID_REF,
            EntryType.EXTERNAL_REF_GUID,
        ]:
            self.mark_entry_content_consumed()
            return self.unsafe_read_16_guid()

        elif self.peeked_entry_type in [
            EntryType.EXTERNAL_REF,
            NamedEntryType.NAMED_EXTERNAL_INDEX_REF,
            UnnamedEntryType.UNNAMED_EXTERNAL_INDEX_REF,
        ]:
            self.mark_entry_content_consumed()
            return self.unsafe_read_4_int32()
        else:
            self.skip_entry()
            return False, "00000000000000000000000000000000"

    def read_int64(self) -> tuple[bool, int]:
        if self.peeked_entry_type == EntryType.UNSET:
            self.peek_entry()

        try:
            if (
                self.peeked_entry_type == NamedEntryType.NAMED_SBYTE
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_SBYTE
            ):
                raise Exception("self.unsafe_read_1_sbyte() not implemented")
                # [success, value] = self.UNSAFE_Read_1_SByte()
                # if success:
                #     return True, value
                # else:
                #     return False, 0
            elif (
                self.peeked_entry_type == NamedEntryType.NAMED_BYTE
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_BYTE
            ):
                [success, value] = self.unsafe_read_1_byte()
                if success:
                    return True, value
                else:
                    return False, 0

            elif (
                self.peeked_entry_type == NamedEntryType.NAMED_SHORT
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_SHORT
            ):
                raise Exception("self.unsafe_read_2_int16() not implemented")
                # [success, value] = self.UNSAFE_Read_2_Int16()
                # if success:
                #     return True, value
                # else:
                #     return False, 0

            elif (
                self.peeked_entry_type == NamedEntryType.NAMED_U_SHORT
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_U_SHORT
            ):
                raise Exception("self.unsafe_read_2_uint16() not implemented")
                # [success, value] = self.UNSAFE_Read_2_UInt16()
                # if success:
                #     return True, value
                # else:
                #     return False, 0

            elif self.peeked_entry_type in [
                NamedEntryType.NAMED_INT,
                UnnamedEntryType.UNNAMED_INT,
                EntryType.INTEGER,
            ]:
                [success, value] = self.unsafe_read_4_int32()
                if success:
                    return True, value
                else:
                    return False, 0

            elif (
                self.peeked_entry_type == NamedEntryType.NAMED_U_INT
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_U_INT
            ):
                raise Exception("self.unsafe_read_4_uint32() not implemented")
                # [success, value] = self.UNSAFE_Read_4_UInt32()
                # if success:
                #     return True, value
                # else:
                #     return False, 0

            elif (
                self.peeked_entry_type == NamedEntryType.NAMED_LONG
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_LONG
            ):
                [success, value] = self.unsafe_read_8_int64()
                if success:
                    return True, value
                else:
                    return False, 0

            elif (
                self.peeked_entry_type == NamedEntryType.NAMED_U_LONG
                or self.peeked_entry_type == UnnamedEntryType.UNNAMED_U_LONG
            ):
                raise Exception("self.unsafe_read_8_uint64() not implemented")
                # [success, value] = self.UNSAFE_Read_8_UInt64()
                # if success:
                #     return True, value
                # else:
                #     return False, 0

            else:
                self.skip_entry()
                return False, 0
        finally:
            self.mark_entry_content_consumed()

    def unsafe_read_1_byte(self) -> tuple[bool, int]:
        if self.has_buffer_data(1):
            self.buffer_index += 1
            return True, self.buffer[self.buffer_index - 1]
        return False, 0

    def unsafe_read_4_int32(self) -> tuple[bool, int]:
        if not self.has_buffer_data(4):
            self.buffer_index = self.buffer_end
            return False, 0

        start = self.buffer_index
        end = start + 4
        if self.is_little_endian:
            value = int.from_bytes(
                self.buffer[start:end], byteorder="little", signed=True
            )
        else:
            value = int.from_bytes(self.buffer[start:end], byteorder="big", signed=True)

        self.buffer_index = end
        return True, value

    def unsafe_read_8_int64(self) -> tuple[bool, int]:
        if not self.has_buffer_data(8):
            self.buffer_index = self.buffer_end
            return False, 0

        start = self.buffer_index
        end = start + 8
        if self.is_little_endian:
            value = int.from_bytes(
                self.buffer[start:end], byteorder="little", signed=True
            )
        else:
            value = int.from_bytes(self.buffer[start:end], byteorder="big", signed=True)

        self.buffer_index = end
        return True, value

    def unsafe_read_16_guid(self) -> tuple[bool, str]:
        if not self.has_buffer_data(16):
            self.buffer_index = self.buffer_end
            return False, "00000000000000000000000000000000"

        start = self.buffer_index
        end = start + 16
        buffer_str = self.buffer[start:end].decode("utf-8")
        self.buffer_index = end
        return True, buffer_str

    def read_value_weak(self, output: dict):
        if self.buffer_index >= self.buffer_end:
            return None, None, None

        value = None
        [entry, name] = self.peek_entry()
        if not name:
            name = 0

        if entry == EntryType.NULL:
            raise Exception("self.read_null() not implemented")
            # self.ReadNull()

        elif entry == EntryType.EXTERNAL_REF:
            [_, index] = self.read_external_reference()
            value = self.lookup_external_reference(index, LookupRefType.INDEX)

        elif entry == EntryType.EXTERNAL_REF_GUID:
            [_, guid] = self.read_external_reference()
            value = self.lookup_external_reference(guid, LookupRefType.GUID)

        elif entry == EntryType.EXTERNAL_REF_STRING:
            [_, entry_id] = self.read_external_reference()
            value = self.lookup_external_reference(entry_id, LookupRefType.ID)

        elif entry == EntryType.INTERNAL_REF:
            raise Exception("self.read_internal_reference() not implemented")
            # [_, id] = self.ReadInternalReference()
            # value = self.GetInternalReference(id)

        elif entry == EntryType.NODE_START:
            [success, _] = self.enter_node()
            if success:
                # inner_entry = entry
                output[name] = {}
                for i in range(0, 999):
                    if (
                        self.buffer[self.buffer_index] in list(EntryType)
                        and EntryType(self.buffer[self.buffer_index])
                        == EntryType.NODE_END
                    ):
                        break

                    output[name][i] = {}
                    [inner_value, inner_entry, inner_name] = self.read_value_weak(
                        output[name][i]
                    )

                    # Sometimes invalid shit ends up in here
                    while inner_entry == EntryType.INVALID:
                        [inner_value, inner_entry, inner_name] = self.read_value_weak(
                            output[name][i]
                        )

                    inner_list = list(output[name][i].values())
                    if inner_name and inner_value:
                        del output[name][i]
                        output[name][inner_name] = inner_value
                    elif inner_value and not output[name][i]:
                        output[name][i] = inner_value
                    elif len(inner_list) == 1:
                        output[name][i] = inner_list[0]
                    elif len(inner_list) < 1:
                        del output[name][i]

                if len(output[name]) == 1:
                    output[name] = list(output[name].values())[0]

                self.exit_node()
                return value, entry, name
            else:
                print("Failed to enter node '" + name + "'.")
            self.exit_node()

        elif entry == EntryType.ARRAY_START:
            [success, length] = self.enter_array()
            if success:
                output[name] = [None] * length
                for i in range(0, length):
                    if self.buffer[self.buffer_index] == EntryType.ARRAY_END:
                        break

                    output[name][i] = {}
                    [inner_value, inner_entry, inner_name] = self.read_value_weak(
                        output[name][i]
                    )

                    # Sometimes invalid shit ends up in here
                    while inner_entry == EntryType.INVALID:
                        [inner_value, inner_entry, inner_name] = self.read_value_weak(
                            output[name][i]
                        )

                    inner_list = list(output[name][i].values())
                    if inner_value and not output[name][i]:
                        output[name][i] = inner_value
                    elif len(inner_list) == 1:
                        output[name][i] = inner_list[0]
                    elif len(inner_list) < 1:
                        del output[name][i]

                if len(output[name]) == 1:
                    output[name] = list(output[name].values())[0]

                self.exit_array()
                return value, entry, name

            else:
                print("Failed to enter array '" + name + "'.")
            self.exit_array()

        elif entry == EntryType.BOOLEAN:
            raise Exception("read_boolean() not implemented")
            # value = self.ReadBoolean()

        elif entry == EntryType.FLOATING_POINT:
            raise Exception("read_double() not implemented")
            # value = self.ReadDouble()

        elif entry == EntryType.INTEGER:
            [_, value] = self.read_int64()

        elif entry == EntryType.STRING:
            raise Exception("read_string() not implemented")
            # value = self.ReadString()

        elif entry == EntryType.GUID:
            raise Exception("read_guid() not implemented")
            # value = self.ReadGuid()

        elif entry == EntryType.STREAM_END:
            value = ""

        else:
            self.skip_entry()

        return value, entry, name

    def parse(self) -> dict:
        value = {}
        [inner_value, entry_type, _] = self.read_value_weak(value)
        while (
            entry_type != EntryType.NODE_END
            and entry_type != EntryType.ARRAY_END
            and entry_type != EntryType.STREAM_END
            and self.buffer_index < self.buffer_end
        ):
            [inner_value, entry_type, _] = self.read_value_weak(value)

        while len(value) == 1:
            value = list(value.values())[0]

        return value
