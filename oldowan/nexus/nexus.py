import re
import StringIO


class nexus(object):
    """Create a nexus file object::

        f = nexus(filename_or_data,[ mode="r"])

    The API for the nexus file object closely follows the interface of the
    standard python file object.

    The mode can be one of:

    * 'r' - reading (default)
    * 's' - string data
    * 'f' - file object
    * 'a' - append
    * 'w' - write

    The file will be created if it doesn't exist for writing or appending; it
    will be truncated when opened for reading.

    For read mode, universal newline support is automatically invoked.

    Each NEXUS entry is parsed into a dict with 'name' and 'sequence' values. 
    """

    __mode = None

    def __get_mode(self):
        return self.__mode

    mode = property(fget=__get_mode,
                    doc="file mode ('r', 's', 'f', 'w', or 'a')")

    def __get_closed(self):
        return self.__fobj.closed

    closed = property(fget=__get_closed,
                      doc="True if the file is closed")

    __fobj = None
    __buff = None
    __blocks = None
    __cursor = 0

    __ntax = None

    def __get_ntax(self):
        return self.__ntax

    ntax = property(fget=__get_ntax,
                    doc="number of taxa (integer)")

    __nchar = None

    def __get_nchar(self):
        return self.__nchar

    nchar = property(fget=__get_nchar,
                    doc="number of characters (integer)")

    def __init__(self, filename_or_data, mode='r'):
        """x.__init__(...) initializes x

        see x.__class__.__doc__ for signature"""

        if mode[0] in ['r', 'a', 'w']:
            if mode == 'r':
                # force universal read mode
                mode = 'rU'
            self.__fobj = open(filename_or_data, mode)
        elif mode == 'f':
            self.__fobj = filename_or_data
        elif mode == 's':
            self.__fobj = StringIO.StringIO(filename_or_data)
        else:
            msg = "mode string must start with 'r', 'a', 'w', 'f' or 's', \
                    not '%s'" % mode[0]
            raise ValueError(msg)
        self.__mode = mode

    def __iter__(self):
        """x.__iter__() <==> iter(x)"""
        return self

    def __enter__(self):
        """__enter__() -> self."""
        return self

    def __exit__(self, type, value, traceback):
        """__exit__(*excinfo) -> None.  Closes the file."""
        self.close()

    def close(self):
        """close() -> None or (perhaps) an integer.  Close the file."""
        if self.__mode == 'w':
            self.__buff.insert(0, self.__header())
            self.__buff.append(';\nEND;\n')
            self.__fobj.write(''.join(self.__buff))
        return self.__fobj.close()

    def __header(self):
        h = []
        h.append('#NEXUS\n')
        h.append('BEGIN Data;')
        h.append('  Dimensions ntax=%d nchar=%d;' %
                 (self.ntax,
                  self.nchar))
        h.append('  Format Datatype=DNA missing=? gap=-;')
        h.append('Matrix\n')
        return '\n'.join(h)

    def flush(self):
        """flush() -> None.  Flush the internal I/O buffer."""
        return self.__fobj.flush()

    def next(self):
        """next() -> the next entry, or raise StopIteration"""
        nxt = self.readentry()
        if nxt is None:
            raise StopIteration
        return nxt

    def read(self):
        """read() -> list of dict entries, reads the remainder of the data.

        Equivalent to readentries()."""
        return self.readentries()

    def readentry(self):
        """readentry() -> next entry, as a dict.

        Return None at EOF."""
        # because of the complexity of the format, have to parse
        # the whole file at once.
        if self.__blocks is None:
            self.__parse()
        if self.__blocks.has_key('data') and self.__blocks['data'].has_key('matrix'):
            if self.__cursor < self.ntax:
                current = self.__blocks['data']['matrix'][self.__cursor]
                self.__cursor = self.__cursor + 1
                return current
        return None
        
    def readentries(self):
        """readentries() -> list of entries, each a dict.

        Call readentry() repeatedly and return a list of the entries read."""
        return list(x for x in self)

    def write(self, entry, wrap_at=80, endline='\n'):
        """write(entry) -> None. Write entry dict to file.

        argument dict 'entry' must have keys 'name' and 'sequence', both
        with string values."""
        if not ('name' in entry and 'sequence' in entry):
            raise ValueError('entry missing either name or sequence')
        if self.__blocks is None:
            self.__buff = []
            self.__blocks = {}
            self.__blocks['data'] = {}
            self.__blocks['data']['matrix'] = []
            self.__ntax = 0
            self.__nchar = len(entry['sequence'])
        else:
            if len(entry['sequence']) != self.nchar:
                raise ValueError("Sequence length does not match")
        self.__ntax += 1 
        self.__blocks['data']['matrix'].append(entry)
        self.__buff.append(entry2str(entry, wrap_at, endline))

    def write_entries(self, entries):
        """write_entries(entries) -> None. Write list of entries to file.

        The equivalent of calling write for each entry."""
        for entry in entries:
            self.write(entry)

    def __parse(self):  
        # whether the __blocks variable is None or a dict determines if
        # the nexus data has been parsed
        self.__blocks = {}

        all = self.__fobj.read()
        self.__fobj.close()

        if re.match(r'\s*#NEXUS', all, re.I) is None:
            raise ValueError('does not appear to be in NEXUS format')

        reBEGIN = re.compile(r'^\s*BEGIN', re.I | re.M)
        blocks = reBEGIN.split(all)
        # first group is going to be the "#NEXUS" declaration
        # so drop that
        blocks = blocks[1:]
        # find the 'data' block
        datablock = [x for x in blocks if re.match(r'^\s*data', x, re.I)]
        if len(datablock) != 1:
            raise ValueError('No single DATA block found')
        else:
            self.__parse_datablock(datablock[0])

    def __parse_datablock(self, text):
        self.__blocks['data'] = {}

        reMATRIX = re.compile(r'^\s*MATRIX', re.I | re.M)
        matrixsplit = reMATRIX.split(text)
        if len(matrixsplit) != 2:
            raise ValueError("No MATRIX in DATA block")
        info_text   = matrixsplit[0]
        matrix_text = matrixsplit[1]

        m_ntax  = re.search(r'ntax=(\d+)', info_text, re.I)
        if m_ntax is not None:
            self.__ntax = int(m_ntax.groups()[0])

        m_nchar = re.search(r'nchar=(\d+)', info_text, re.I)
        if m_nchar is not None:
            self.__nchar = int(m_nchar.groups()[0])

        m_interleave = re.search(r'interleave', info_text, re.I)
        if m_interleave is None:
            self.__parse_matrix(matrix_text)
        else:
            self.__parse_interleaved_matrix(matrix_text)


    def __parse_matrix(self, text):
        self.__blocks['data']['matrix'] = []
        matrix_lines = text.split('\n')
        keep_reading = False
        current = None
        for line in matrix_lines:
            sline = line.rstrip()
            # if the line is not blank or indicating the end of the matrix,
            # continue
            if len(sline) != 0 and re.match(r'\s*;|\s*end;', sline, re.I) is None:
                entries = sline.strip().split()
                # when expecting a new entry, raise an error if that's not true
                if not keep_reading and len(entries) < 2:
                    raise ValueError("Error in MATRIX")
                # create a new entry
                if not keep_reading:
                    current = {'name': entries[0],
                               'sequence': ''.join(entries[1:]) }
                else:
                    current['sequence'] = current['sequence'] + ''.join(entries)
                if len(current['sequence']) < self.nchar:
                    keep_reading = True
                elif len(current['sequence']) > self.nchar:
                    raise ValueError("Somehow got too much sequence")
                else:
                    keep_reading = False
                if not keep_reading:
                    self.__blocks['data']['matrix'].append(current)
        

    def __parse_interleaved_matrix(self, text):
        raise NotImplementedError



def entry2str(entry, wrap_at, endline):
    """entry2str(entry[, wrap_at[, endline]]) -> a string. entry is a dict.

    Given an entry dict with string values for 'name' and 'sequence', will
    return a string in non-interleaved NEXUS format. 'endline's (default \\n) 
    will be inserted into the sequence every 'wrap_at' characters (default 80)."""

    s = []
    namelen = len(entry['name'])
    remaining = wrap_at - namelen - 2
    s.append('%s  %s%s' % (entry['name'], entry['sequence'][0:remaining], endline))
    if len(entry['sequence']) >= remaining:
        # for the wrapping, DON'T use 'textwrap.wrap'. It is very slow because
        # it tries to be clever and find word breaks to wrap at.
        exploded_seq = list(entry['sequence'][remaining:])
        wrap_points = range(1, len(exploded_seq), wrap_at - 8)
        wrap_points.reverse()
        exploded_seq.insert(0, '        ')
        for i in wrap_points[:-1]:
            exploded_seq.insert(i, '\n        ')
        s = s + exploded_seq + ['\n']
    return ''.join(s)
    
