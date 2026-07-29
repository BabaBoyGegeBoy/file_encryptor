import os
import shutil
import tempfile
from encryptor import FileEncryptor

def test_encrypt_decrypt():
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = os.path.join(tmpdir, 'input')
        output_dir = os.path.join(tmpdir, 'output')
        decrypt_dir = os.path.join(tmpdir, 'decrypt')
        
        os.makedirs(input_dir)
        os.makedirs(output_dir)
        os.makedirs(decrypt_dir)

        test_file = os.path.join(input_dir, 'test.txt')
        test_content = b'Hello, World! This is a test file for encryption.'
        with open(test_file, 'wb') as f:
            f.write(test_content)

        encryptor = FileEncryptor('AES-CTR')

        print("Testing AES-CTR encryption without password...")
        results = encryptor.encrypt_directory(input_dir, output_dir)
        assert len(results['success']) == 1, f"Expected 1 success, got {len(results['success'])}"
        
        print("Testing AES-CTR decryption without password...")
        results = encryptor.decrypt_directory(output_dir, decrypt_dir)
        assert len(results['success']) == 1, f"Expected 1 success, got {len(results['success'])}"
        
        decrypted_file = os.path.join(decrypt_dir, 'test.txt')
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        assert decrypted_content == test_content, "Decrypted content mismatch"
        print("\u2713 AES-CTR without password: PASSED")

        shutil.rmtree(output_dir)
        shutil.rmtree(decrypt_dir)
        os.makedirs(output_dir)
        os.makedirs(decrypt_dir)

        print("Testing AES-CTR encryption with password...")
        results = encryptor.encrypt_directory(input_dir, output_dir, password='test_password')
        assert len(results['success']) == 1
        
        print("Testing AES-CTR decryption with password...")
        results = encryptor.decrypt_directory(output_dir, decrypt_dir, password='test_password')
        assert len(results['success']) == 1
        
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        assert decrypted_content == test_content
        print("\u2713 AES-CTR with password: PASSED")

        shutil.rmtree(output_dir)
        shutil.rmtree(decrypt_dir)
        os.makedirs(output_dir)
        os.makedirs(decrypt_dir)

        encryptor_rc4 = FileEncryptor('RC4-MD5')
        
        print("Testing RC4-MD5 encryption with password...")
        results = encryptor_rc4.encrypt_directory(input_dir, output_dir, password='test_password')
        assert len(results['success']) == 1
        
        print("Testing RC4-MD5 decryption with password...")
        results = encryptor_rc4.decrypt_directory(output_dir, decrypt_dir, password='test_password')
        assert len(results['success']) == 1
        
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        assert decrypted_content == test_content
        print("\u2713 RC4-MD5 with password: PASSED")

        shutil.rmtree(output_dir)
        shutil.rmtree(decrypt_dir)
        os.makedirs(output_dir)
        os.makedirs(decrypt_dir)

        print("Testing filename encryption...")
        results = encryptor.encrypt_directory(input_dir, output_dir, password='test_password', encrypt_name=True)
        assert len(results['success']) == 1
        
        results = encryptor.decrypt_directory(output_dir, decrypt_dir, password='test_password')
        assert len(results['success']) == 1
        assert os.path.exists(decrypted_file)
        print("\u2713 Filename encryption: PASSED")

        print("\nAll tests passed!")

if __name__ == '__main__':
    test_encrypt_decrypt()
