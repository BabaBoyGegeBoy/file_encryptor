#!/usr/bin/env python3
import argparse
import os
from encryptor import FileEncryptor

def main():
    parser = argparse.ArgumentParser(description='File Encryptor/Decryptor')
    subparsers = parser.add_subparsers(dest='command', required=True)

    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt files')
    encrypt_parser.add_argument('--algorithm', '-a', choices=['AES-CTR', 'RC4-MD5'], 
                                default='AES-CTR', help='Encryption algorithm')
    encrypt_parser.add_argument('--input', '-i', required=True, help='Input directory or file')
    encrypt_parser.add_argument('--output', '-o', required=True, help='Output directory')
    encrypt_parser.add_argument('--password', '-p', help='Encryption password')
    encrypt_parser.add_argument('--format', '-f', help='File format filter (e.g., .mp4)')
    encrypt_parser.add_argument('--encrypt-name', '-n', action='store_true', help='Encrypt filename')
    encrypt_parser.add_argument('--skip-small', '-s', action='store_true', help='Skip files smaller than 5MB')
    encrypt_parser.add_argument('--threshold', '-t', type=int, default=5242880, 
                                help='Small file threshold in bytes')

    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt files')
    decrypt_parser.add_argument('--algorithm', '-a', choices=['AES-CTR', 'RC4-MD5'], 
                                default='AES-CTR', help='Encryption algorithm')
    decrypt_parser.add_argument('--input', '-i', required=True, help='Input directory or file')
    decrypt_parser.add_argument('--output', '-o', required=True, help='Output directory')
    decrypt_parser.add_argument('--password', '-p', help='Decryption password')

    args = parser.parse_args()

    encryptor = FileEncryptor(args.algorithm)

    if args.command == 'encrypt':
        if os.path.isdir(args.input):
            results = encryptor.encrypt_directory(
                args.input, args.output, args.password, 
                args.format, args.encrypt_name, 
                args.skip_small, args.threshold
            )
            print(f"Encryption completed:")
            print(f"  Success: {len(results['success'])} files")
            print(f"  Skipped: {len(results['skipped'])} files")
            print(f"  Failed: {len(results['failed'])} files")
            for path, error in results['failed'][:5]:
                print(f"    - {path}: {error}")
        else:
            try:
                output_path = os.path.join(args.output, os.path.basename(args.input) + '.enc')
                encryptor.encrypt_file(
                    args.input, output_path, args.password, 
                    args.encrypt_name, args.skip_small, args.threshold
                )
                print(f"Encrypted: {args.input} -> {output_path}")
            except Exception as e:
                print(f"Encryption failed: {e}")

    elif args.command == 'decrypt':
        if os.path.isdir(args.input):
            results = encryptor.decrypt_directory(args.input, args.output, args.password)
            print(f"Decryption completed:")
            print(f"  Success: {len(results['success'])} files")
            print(f"  Failed: {len(results['failed'])} files")
            for path, error in results['failed'][:5]:
                print(f"    - {path}: {error}")
        else:
            try:
                encryptor.decrypt_file(args.input, args.output, args.password)
                print(f"Decrypted: {args.input} -> {args.output}")
            except Exception as e:
                print(f"Decryption failed: {e}")

if __name__ == '__main__':
    main()
