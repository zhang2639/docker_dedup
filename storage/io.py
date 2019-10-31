
def read_chunks_from_file(fin, block_size):
    with open(path, 'rb', buffering=1024*64) as fin:
        while True:
            piece = fin.read(block_size)
            if not piece:
                return
            yield piece                                                    

def write_chunks_to_file(path, block_gen):
    with open(path, 'wb') as fout:
        for block in block_gen:
            fout.write(block)


# def read_file_part(path, offset, nb_bytes):
#     with open(path, 'rb') as fin:
#         fin.seek(offset)
#         data = fin.read(nb_bytes)
#     return data

# def write_file_part(path, offset, data):
#     with open(path, 'r+b') as fout:
#         fout.seek(offset)
#         fout.write(data)
#         fout.flush()

# def create_file(path):
#     open(path, 'w').close()

def decompress_file(infile, outfile, compressor):
    block_size = 2**24
    block_gen = read_chunks_from_file(infile, block_size)
    comp_block_gen = compressor.streaming_decompression(block_gen)
    write_chunks_to_file(outfile, comp_block_gen)
