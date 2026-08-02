import termios

_orig_tcgetattr = termios.tcgetattr
_orig_tcsetattr = termios.tcsetattr
_orig_tcflush = termios.tcflush

# Return a valid termios list: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
# where cc is a list of NCCS=19 control characters
_FAKE_ATTRS = [
    0,      # iflag
    0,      # oflag
    0x1cbd, # cflag (B115200 | CS8 | CREAD | CLOCAL)
    0,      # lflag (raw)
    0x1002, # ispeed (B115200)  
    0x1002, # ospeed (B115200)
    [0]*19  # cc (control chars)
]

def safe_tcgetattr(fd):
    try:
        return _orig_tcgetattr(fd)
    except (termios.error, OSError):
        return list(_FAKE_ATTRS)

def safe_tcsetattr(fd, when, attrs):
    try:
        _orig_tcsetattr(fd, when, attrs)
    except (termios.error, OSError):
        pass

def safe_tcflush(fd, queue):
    try:
        _orig_tcflush(fd, queue)
    except (termios.error, OSError):
        pass

termios.tcgetattr = safe_tcgetattr
termios.tcsetattr = safe_tcsetattr
termios.tcflush = safe_tcflush
