from oldowan.nexus import nexus
from nose.tools import raises

import os

SIMPLE_TEXT = """
#NEXUS
Begin data;
Dimensions ntax=4 nchar=15;
Format datatype=dna symbols="ACTG" missing=? gap=-;
Matrix
Species1   atgctagctagctcg
Species2   atgcta??tag-tag
Species3   atgttagctag-tgg
Species4   atgttagctag-tag           
 ;
End;
"""

SIMPLE_FILEPATH = os.path.join(os.path.dirname(__file__),
        'test_files', 'simple.nexus')
MULTILINE_FILEPATH = os.path.join(os.path.dirname(__file__), 
        'test_files', 'multiline.nexus')

def test_mode_accessor():
    """test mode accessor"""

    f = nexus(SIMPLE_TEXT, 's')
    assert f.mode == 's'

    f = nexus(SIMPLE_FILEPATH, 'r')
    assert f.mode == 'rU'


@raises(ValueError)
def test_bad_mode_string():
    """pass unknown mode string"""

    f = nexus(SIMPLE_TEXT, 'q')


@raises(TypeError, ValueError)
def test_bad_mode_option():
    """pass non-string to mode option"""

    f = nexus(SIMPLE_TEXT, 1)


@raises(ValueError)
def test_bad_value_to_write():
    """try to write entry without name"""

    f = nexus(os.devnull, 'a')
    f.write({'sequence': 'AGCT'})
    f.close()


def test_basic_multi_entry_write():
    """try to write multiple entries"""

    entries = [{'name': 'a', 'sequence': 'A'}, {'name': 'g', 'sequence': 'G'}]
    f = nexus(os.devnull, 'a')
    f.write_entries(entries)
    f.close()


def test_read_from_string():
    """read a string of data"""

    # 's' is the 'string' mode
    f = nexus(SIMPLE_TEXT, 's')
    entries = f.readentries()
    f.close()
    print entries
    assert 4 == len(entries)

    assert isinstance(entries[0], dict)
    assert 'Species1' == entries[0]['name']
    assert 15 == len(entries[0]['sequence'])

    assert isinstance(entries[1], dict)
    assert 'Species2' == entries[1]['name']
    assert 15 == len(entries[1]['sequence'])


def test_read_from_file():
    """read from a filename"""

    f = nexus(SIMPLE_FILEPATH, 'r')
    entries = f.read()
    f.close()
    assert 4 == len(entries)

    assert isinstance(entries[0], dict)
    assert 'Species1' == entries[0]['name']
    assert 15 == len(entries[0]['sequence'])

    assert isinstance(entries[1], dict)
    assert 'Species2' == entries[1]['name']
    assert 15 == len(entries[1]['sequence'])


def test_read_from_file_handle():
    """read from an open file"""

    fh = open(SIMPLE_FILEPATH, 'r')
    f = nexus(fh, 'f')
    entries = f.readentries()
    f.close()
    assert 4 == len(entries)

    assert isinstance(entries[0], dict)
    assert 'Species1' == entries[0]['name']
    assert 15 == len(entries[0]['sequence'])

    assert isinstance(entries[1], dict)
    assert 'Species2' == entries[1]['name']
    assert 15 == len(entries[1]['sequence'])


def test_iterate():
    """iterate"""
    # first, from a string 
    for entry in nexus(SIMPLE_TEXT, 's'):
        assert isinstance(entry, dict)
    # next, from a filename
    for entry in nexus(SIMPLE_FILEPATH):
        assert isinstance(entry, dict)


def test_read_from_multiline_file():
    """read from a file where the entries span multiple lines"""

    f = nexus(MULTILINE_FILEPATH, 'r')
    entries = f.read()
    f.close()
    assert 2 == len(entries)

    assert isinstance(entries[0], dict)
    assert 'Species1' == entries[0]['name']
    assert 30 == len(entries[0]['sequence'])

    assert isinstance(entries[1], dict)
    assert 'Species2' == entries[1]['name']
    assert 30 == len(entries[1]['sequence'])



