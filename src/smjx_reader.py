"""
Scott Lamkin 09/13/2022 - ShotSpotter

smjx_reader.py: Module to read "smjx" metadata chunk and sample rate from ShotSpotter WAV files.

Usage: On import, read_smjx_from_file method passes the sample_rate for usage with find_pulses.py.
       As a script point to a ShotSpotter WAV file.
"""

import os
import sys
import argparse
import json
import pathlib
import zlib


def parse_arguments():
    parser = argparse.ArgumentParser(description='path to wave file')
    parser.add_argument('path', type=pathlib.Path)
    args = parser.parse_args()
    return args


def read_wav_into_binary(wavpath):
    if os.path.exists(wavpath):
        with open(wavpath, 'rb') as f:
            return f.read()
    raise IOError


def read_RIFF_chunks(bindata):
    if (bindata[:4] != b'RIFF') or (bindata[8:12] != b'WAVE'):
        raise IOError
    all_chunks = read_all_chunks(bindata[12:])
    return all_chunks


def read_all_chunks(bindata):
    chunk_names = []
    chunk_lengths = []
    chunks = []
    remainder = 0
    while True:
        bindata, remainder, chunk_name, chunk_length, chunk = read_next_chunk(bindata, remainder)
        if chunk_length <= 1:
            break
        chunk_names.append(chunk_name)
        chunk_lengths.append(chunk_length)
        chunks.append(chunk)
    return chunk_names, chunk_lengths, chunks


def read_next_chunk(bindata, remainder):
    chunk_name = bindata[:4]
    chunk_length = int.from_bytes(bindata[4:8], byteorder="little")
    if remainder > 0:
        bindata = bindata[1:]
        remainder = 0
    chunk = bindata[8:8+chunk_length]
    if chunk_length % 2 == 1:
        remainder = 1
    return bindata[8+chunk_length:], remainder, chunk_name, chunk_length, chunk


def parse_smjx_chunk(smjx_chunk):
    inflated_smjx = zlib.decompress(smjx_chunk)
    return json.loads(inflated_smjx)


def read_sr(fmt__chunk):
    return int.from_bytes(fmt__chunk[4:8], byteorder="little")


def read_smjx_from_file(wavpath):
    chunk_names, _, chunk_data = read_RIFF_chunks(read_wav_into_binary(wavpath))
    smjx_index = [b'smj' in chunk_name for chunk_name in chunk_names].index(True)
    fmt__index = chunk_names.index(b'fmt ')
    smjx_dict = parse_smjx_chunk(chunk_data[smjx_index])
    sr = read_sr(chunk_data[fmt__index])
    return sr, smjx_dict


def main():
    args = parse_arguments()
    try:
        _, smjx_dict = read_smjx_from_file(args.path)
    except IOError:
        sys.stderr.write("Not a WAV file\n")
        return 1
    except ValueError:
        sys.stderr.write("No smjx chunk found\n")
        return 1
    else:
        sys.stdout.write(json.dumps(smjx_dict, indent=4, sort_keys=True))
        sys.stdout.write("\n")
        return 0


if __name__ == '__main__':
    sys.exit(main())
