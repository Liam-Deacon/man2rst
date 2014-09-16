#!/usr/bin/env python
# encoding: utf-8

##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.deacon@diamond.ac.uk                                         #
#                                                                            #
# Created on 6 Jun 2014                                                      #
#                                                                            #
# Copyright: Copyright (C) 2014 Liam Deacon                                  #
#                                                                            #
# License: MIT License                                                       #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the "Software"), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
##############################################################################
'''
man2rst -- generate restructured text from man pages
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-06-06'
__updated__ = '2014-06-06'
__contact__ = 'liam.deacon@diamond.ac.uk'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): 
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "man2rst -- generate restructured text from man pages"
    program_longdesc = '\n'.join([line for line in __import__('__main__').__doc__.split("\n") 
                                                           if not line.startswith('@')])
    program_license = '''%s

  Created by Liam Deacon on %s.
  Copyright 2014 Diamond Light Source Ltd. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

  Please send your feedback, including bug notifications 
  and fixes to: %s

usage:-
''' % (program_longdesc, str(__date__), __contact__)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, 
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', 
                            version=program_version_message)
        parser.add_argument('-i', '--input', 
                            metavar='<man_file>', dest='input', 
                            help="specifies man input file to convert")
        parser.add_argument('-o', '--output', 
                            metavar='rst_file>', dest='output',
                            default=None, help='path to output file. If no '
                            'path given then output will be printed to stdout')
        # Process arguments
        args = parser.parse_args()

        try:  # read man
            with open(args.input, 'r') as f:
                text = []
                for line in f:
                    line = line.replace('\-', '-').replace('\n\r', '\n')
                    if line.startswith(r'.\"'):
                        line = line.replace(r'.\"', '..')
                        text.append(line)
                    elif line.startswith('.TH '):
                        line = line.replace('.TH ', '')
                        text.append(line)
                        text.append('=' * (len(line) - 1) + '\n')
                    elif line.startswith('.SH '):
                        line = line.replace('.SH ', '').capitalize()
                        text.append(line)
                        text.append(str('-' * (len(line) - 1)) + '\n')
                    elif line.startswith('.B '):
                        line = line.replace('.B ', '**'
                                        ).replace('\n', '').rstrip() + '**\n'
                        text.append(line)
                    elif line.startswith('.I '):
                        line = line.replace('.I ', '*'
                                        ).replace('\n', '').rstrip() + '*\n'
                        text.append(line)
                    elif line.startswith('.IP '):
                        line = line.replace('.IP ', '*'
                                        ).replace('\n', '').rstrip() + '*\n'
                        text.append(line)
                    elif line.startswith('.PP'):
                        line = line.replace('.PP', ''
                                        ).replace('\n', '').rstrip() + '\n'
                        text.append(line)
                    else:
                        text.append(line)
                        
                for i, line in enumerate(text):
                    if line[-2:] == '*\n':
                        text[i] = line.replace('*\n', '* ')
                        
                # adjust text
                padding = [0] * (len(text) + 1)
                pads = 0
                for i, line in enumerate(text):
                    padding[i] = pads
                    if line.startswith('.RS'):
                        pads += 2
                        text[i] = '\n\n'
                    elif '.RS\n' in line:
                        text[i] = line.replace('.RS\n', '\n\n')
                        pads += 2
                    elif line.startswith('.RE'):
                        pads -= 2
                        text[i] = '\n'
                    elif '.RE\n' in line:
                        pads -= 2
                        text[i] = line.replace('.RE\n', '\n')
                    
                for i in range(len(text)):
                    text[i] = text[i].ljust(padding[i])
            
        except IOError:
            sys.stderr.write("Cannot load input file: '%s'\n" % args.input)
            sys.exit(1)

        if args.output != None:
            # print to file
            pass
        else:
            print("".join(text))

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'man2rst_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
        
    sys.exit(main())
