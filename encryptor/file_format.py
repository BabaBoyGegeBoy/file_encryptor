import struct
import os

MAGIC_BYTES = b'\xFA\xCE\x45\x4E\x43\x52\x59'

class EncryptedFileHeader:
    HEADER_SIZE = 128

    def __init__(self):
        self.algorithm = b''
        self.iv = b''
        self.salt = b''
        self.original_name = b''
        self.name_encrypted = False

    def pack(self) -> bytes:
        header = bytearray(EncryptedFileHeader.HEADER_SIZE)
        header[:7] = MAGIC_BYTES
        struct.pack_into('B', header, 7, len(self.algorithm))
        header[8:8+len(self.algorithm)] = self.algorithm
        
        struct.pack_into('B', header, 16, len(self.iv))
        header[17:17+len(self.iv)] = self.iv
        
        struct.pack_into('B', header, 33, len(self.salt))
        header[34:34+len(self.salt)] = self.salt
        
        name_len = len(self.original_name)
        struct.pack_into('H', header, 50, name_len)
        header[52:52+name_len] = self.original_name
        
        struct.pack_into('?', header, 127, self.name_encrypted)
        
        return bytes(header)

    @classmethod
    def unpack(cls, data: bytes) -> 'EncryptedFileHeader':
        if len(data) < EncryptedFileHeader.HEADER_SIZE:
            raise ValueError("Invalid header size")
        
        if data[:7] != MAGIC_BYTES:
            raise ValueError("Invalid magic bytes")
        
        header = cls()
        algo_len = struct.unpack_from('B', data, 7)[0]
        header.algorithm = data[8:8+algo_len]
        
        iv_len = struct.unpack_from('B', data, 16)[0]
        header.iv = data[17:17+iv_len]
        
        salt_len = struct.unpack_from('B', data, 33)[0]
        header.salt = data[34:34+salt_len]
        
        name_len = struct.unpack_from('H', data, 50)[0]
        header.original_name = data[52:52+name_len]
        
        header.name_encrypted = struct.unpack_from('?', data, 127)[0]
        
        return header

def is_encrypted_file(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            header = f.read(7)
            return header == MAGIC_BYTES
    except:
        return False
