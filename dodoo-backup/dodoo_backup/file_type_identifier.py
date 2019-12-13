# =============================================================================
# Created By : David Arnold
# Credits    : https://stackoverflow.com/a/13044946
# Sources    : https://www.garykessler.net/library/file_sigs.html
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements a file type identifier"""


magic_dict = {
    "\x50\x4b\x03\x04": "zip",
    "\x1f\x8b\x08": "gztar",
    "\x42\x5a\x68": "bztar",
    "\x75\x73\x74\x61\x72": "tar",
    "\xfd\x37\x7a\x58\x5a\x00": "xztar",
}

max_len = max(len(x) for x in magic_dict)


def file_type(filename):
    with open(filename) as f:
        file_start = f.read(max_len)
    for magic, filetype in magic_dict.items():
        if file_start.startswith(magic):
            return filetype
