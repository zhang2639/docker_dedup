
def enum(**enums):
    return type('Enum', (), enums)


# def generate_file_md5(path, block_size=2**20, block_count=10):
#     import hashlib
#     m = hashlib.md5()
#     c = 0
#     with open(path, "rb") as f:
#         while True:
#             buf = f.read(block_size)
#             if not buf:
#                 break
#             m.update(buf)
#             if c == block_count: break
#             c += 1
#     return m.hexdigest()
