import os
import shutil
import hashlib
from .algorithms import AESCTR, RC4MD5, KeyDerivation
from .file_format import EncryptedFileHeader, is_encrypted_file

CHUNK_SIZE = 64 * 1024

class FileEncryptor:
    def __init__(self, algorithm: str = 'AES-CTR'):
        self.algorithm = algorithm.upper()
        self.alg_instance = self._get_algorithm()

    def _get_algorithm(self):
        if self.algorithm == 'AES-CTR':
            return AESCTR
        elif self.algorithm == 'RC4-MD5':
            return RC4MD5
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def encrypt_file(self, input_path: str, output_path: str, password: str = None, 
                     encrypt_name: bool = False, skip_small: bool = False, 
                     small_threshold: int = 5 * 1024 * 1024) -> bool:
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if skip_small and os.path.getsize(input_path) < small_threshold:
            return False

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if password:
            key, salt = KeyDerivation.pbkdf2(password)
        else:
            salt = os.urandom(16)
            key = hashlib.sha256(salt).digest()

        header = EncryptedFileHeader()
        header.algorithm = self.algorithm.encode()
        header.salt = salt
        header.name_encrypted = encrypt_name

        original_name = os.path.basename(input_path)
        if encrypt_name and password:
            name_encrypted, name_iv = AESCTR.encrypt(key, original_name.encode())
            header.original_name = name_iv + name_encrypted
        else:
            header.original_name = original_name.encode()

        with open(input_path, 'rb') as in_file:
            with open(output_path, 'wb') as out_file:
                out_file.write(header.pack())
                
                first_chunk = True
                while True:
                    chunk = in_file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    encrypted_chunk, iv = self.alg_instance.encrypt(key, chunk)
                    if first_chunk:
                        header.iv = iv
                        out_file.seek(0)
                        out_file.write(header.pack())
                        out_file.seek(EncryptedFileHeader.HEADER_SIZE)
                        first_chunk = False
                    else:
                        out_file.write(iv)
                    out_file.write(encrypted_chunk)

        return True

    def decrypt_file(self, input_path: str, output_path: str, password: str = None) -> bool:
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not is_encrypted_file(input_path):
            raise ValueError("Not an encrypted file")

        with open(input_path, 'rb') as in_file:
            header_data = in_file.read(EncryptedFileHeader.HEADER_SIZE)
            header = EncryptedFileHeader.unpack(header_data)

            if password:
                key, _ = KeyDerivation.pbkdf2(password, header.salt)
            else:
                key = hashlib.sha256(header.salt).digest()

            if header.name_encrypted and password:
                name_iv = header.original_name[:16]
                name_encrypted = header.original_name[16:]
                original_name = AESCTR.decrypt(key, name_encrypted, name_iv).decode()
            else:
                original_name = header.original_name.decode()

            if os.path.isdir(output_path):
                final_output_path = os.path.join(output_path, original_name)
            else:
                final_output_path = output_path

            os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

            with open(final_output_path, 'wb') as out_file:
                current_iv = header.iv
                first_chunk = True
                
                while True:
                    if first_chunk:
                        encrypted_chunk = in_file.read(CHUNK_SIZE)
                        first_chunk = False
                    else:
                        iv_data = in_file.read(16)
                        if not iv_data:
                            break
                        current_iv = iv_data
                        encrypted_chunk = in_file.read(CHUNK_SIZE)
                    
                    if not encrypted_chunk:
                        break
                    
                    decrypted_chunk = self.alg_instance.decrypt(key, encrypted_chunk, current_iv)
                    out_file.write(decrypted_chunk)

        return True

    def encrypt_directory(self, input_dir: str, output_dir: str, password: str = None,
                         file_format: str = None, encrypt_name: bool = False,
                         skip_small: bool = False, small_threshold: int = 5 * 1024 * 1024) -> dict:
        results = {'success': [], 'skipped': [], 'failed': []}
        
        for root, dirs, files in os.walk(input_dir):
            rel_path = os.path.relpath(root, input_dir)
            out_root = os.path.join(output_dir, rel_path) if rel_path != '.' else output_dir
            
            for filename in files:
                if file_format and not filename.endswith(file_format):
                    continue
                
                input_path = os.path.join(root, filename)
                output_path = os.path.join(out_root, filename + '.enc')
                
                try:
                    success = self.encrypt_file(input_path, output_path, password, 
                                               encrypt_name, skip_small, small_threshold)
                    if success:
                        results['success'].append((input_path, output_path))
                    else:
                        results['skipped'].append(input_path)
                except Exception as e:
                    results['failed'].append((input_path, str(e)))
        
        return results

    def decrypt_directory(self, input_dir: str, output_dir: str, password: str = None) -> dict:
        results = {'success': [], 'failed': []}
        
        for root, dirs, files in os.walk(input_dir):
            rel_path = os.path.relpath(root, input_dir)
            out_root = os.path.join(output_dir, rel_path) if rel_path != '.' else output_dir
            
            for filename in files:
                if not filename.endswith('.enc'):
                    continue
                
                input_path = os.path.join(root, filename)
                
                try:
                    self.decrypt_file(input_path, out_root, password)
                    results['success'].append(input_path)
                except Exception as e:
                    results['failed'].append((input_path, str(e)))
        
        return results
