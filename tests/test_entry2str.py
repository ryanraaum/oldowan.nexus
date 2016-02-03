from oldowan.nexus import entry2str
from nose.tools import raises

e1 = {'name': 'monkey', 'sequence': 'ACGT'}
e2 = {'name': 'monkey', 'sequence':
      'AACCAGGCGCATACATCGCATGCATGACTCGATCGATCGATCGATCAGCATCGATCGACATGCATCGATCGATCAGCATCGATCGATCGATCGATCGATCGATCGATCAGCATCGATCGATCAGT'}

def test_entry2str_simple():
    """basic call of entry2str"""
    txt = entry2str(e1, wrap_at=80, endline="\n")
    assert txt == "monkey  ACGT\n"

def test_entry2str_wrapping():
    """entry2str wrapping"""
    txt = entry2str(e2, wrap_at=30, endline="\n")
    lines = txt.strip().split('\n')
    # last line probably won't be full length
    for l in lines[:-1]:
        assert len(l) == 30
 
