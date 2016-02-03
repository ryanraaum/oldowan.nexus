Read and write NEXUS format.

oldowan.nexus is a small bioinformatic utility to read and write sequence data
in the NEXUS_ format. NEXUS is a commonly used file format for storing multiple
DNA, RNA, or protein sequences in a single file. It is a text-based,
human-readable format. This utility does not even begin to be a complete NEXUS
file utility. It does not read or write trees or any of the other blocks that
might be found in a NEXUS file. It solely reads and writes the data block, and
on top of that limitation, assumes that the data are sequence data.

Installation Instructions
=========================

This package is pure Python and has no dependencies outside of the standard
library. The easist way to install is using ``easy_install`` from the
setuptools_ package.  This usually goes something like this::

	$ easy_install oldowan.nexus

or on a unix-like system, assuming you are installing to the main Python
``site-packages`` directory as a non-privileged user, this::

	$ sudo easy_install oldowan.nexus

You may also use the standard python distutils setup method. Download the
current source archive from the file list towards the bottom of this page,
unarchive it, and install. On Mac OS X and many other unix-like systems, having
downloaded the archive and changed to the directory containing this archive in
your shell, this might go something like::

	$ tar xvzf oldowan.nexus*
	$ cd oldowan.nexus*
	$ python setup.py install

Quick Start
===========

oldowan.nexus has an interface based on the standard Python ``file``.  Import
oldowan.nexus::

  >>> from oldowan.nexus import nexus

Read a NEXUS format file::

  >>> for entry in nexus('sequences.nexus', 'r'):
  ...     print entry['name'], len(entry['sequence'])

A more cumbersome, but equivalent way of doing the above::

  >>> nexus_file = nexus('sequences.nexus', 'r')
  >>> for entry in nexus_file:
  ...     print entry['name'], len(entry['sequence'])
  >>> nexus_file.close()

Even more cumbersome::

  >>> nexus_file = nexus('sequence.nexus', 'r')
  >>> entries = nexus_file.readentries()
  >>> nexus_file.close()
  >>> for entry in entries:
  ...     print entry['name'], len(entry['sequence'])

Read a string of NEXUS format sequences::

  >>> nexus_string = open('sequences.nexus', 'r').read()
  >>> for entry in nexus(nexus_string, 's'):
  ...     print entry['name'], len(entry['sequence'])

Read a file object::

  >>> nexus_file = open('sequences.nexus', 'r')
  >>> for entry in nexus(nexus_file, 'f'):
  ...     print entry['name'], len(entry['sequence'])

Write to a file::

  >>> nexus_file = open('sequences.nexus', 'w')
  >>> nexus_file.write({'name':'Sequence1', 'sequence':'AGCTAGCT'})
  >>> nexus_file.close()

Release History
===============

1.0.0 (April 6, 2011)
    initial release of module.

.. _NEXUS: http://en.wikipedia.org/wiki/Nexus_file 
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall
