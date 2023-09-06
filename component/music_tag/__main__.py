#!/usr/bin/env python
# pylint: disable=unused-import
r"""CLI for music_tag

Examples

    Printing tags:

        $ # Print tags from all audio files in sample directory
        $ python -m music_tag --print ./sample

        $ # Print specific tags from all audio files in sample directory      
        $ python -m music_tag --print --tags="Title : Album" ./sample

        $ # Write tags from all audio files in sample directory to a csv file
        $ python -m music_tag --to-csv tags.csv ./sample

        $ # Write specific tags from all audio files in sample directory to a csv file
        $ python -m music_tag --tags="Title : Album" --to-csv tags.csv ./sample

    Setting tags:

        $ # Set a couple tags for multiple files      
        $ python -m music_tag --set "genre:Pop" --set "comment:cli test" \
        $                       ./sample/440Hz.aac ./sample/440Hz.flac

        $ # Write tags from csv file to audio files (assuming file paths in
        $ # the csv file are relative to the sample directory
        $ python -m music_tag --from-csv tags.csv
"""

from __future__ import print_function
import argparse
from argparse import RawTextHelpFormatter
import csv
import fnmatch
import os
import sys

import music_tag
from music_tag import load_file


_audio_pattern = ['*.wav', '*.aac', '*.aiff', '*.dsf', '*.flac',
                  '*.m4a', '*.mp3', '*.ogg', '*.opus', '*.wv']

_default_tags = ('Disc Number : Total Discs : Track Number : Total Tracks '
                 ': Title : Artist : Album : Album Artist '
                 ': Year : Genre : Comment')


def _expand_files(files):
    ret = []
    for f in files:
        if os.path.isdir(f):
            # walk directory looking for music files
            for root, dirs, files in os.walk(f):
                for pattern in _audio_pattern:
                    for filename in fnmatch.filter(files, pattern):
                        ret.append(os.path.join(root, filename))
        else:
            ret.append(f)
    return ret


def _main():
    parser = argparse.ArgumentParser(prog='python -m music_tag',
                                     description=__doc__,
                                     formatter_class=RawTextHelpFormatter)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--version', action='version',
                              version='music-tag ' + music_tag.__version__)
    action_group.add_argument('--print', action='store_true',
                              help='print tags')
    action_group.add_argument('--set', action='append', default=[],
                              help='set tag')
    action_group.add_argument('--to-csv', action='store',
                              help='write tags to csv file')
    action_group.add_argument('--from-csv', action='store',
                              help='write tags from csv file')

    parser.add_argument('--tags', action='store', default=_default_tags,
                        help='tags to print')
    parser.add_argument('-I', '--ignore-missing', action='store_true',
                        help='ignore missing audio files when using from-csv')
    parser.add_argument('-D', '--csv-dialect', action='store', default='excel',
                        help='csv file dialect (excel | excel_tab | unix)')
    parser.add_argument('--resolve', action='store_true',
                        help='Use resolve to discern missing tags')
    parser.add_argument('files', nargs='*')

    args = parser.parse_args()

    
    if args.print:
        print()
        fnames = _expand_files(args.files)
        tags = [t.strip() for t in args.tags.split(':')]

        for fname in fnames:
            f = music_tag.load_file(fname)
            print(f.info(tags=tags, show_empty=True, resolve=args.resolve))
            print()
    
    if args.set:
        set_key_vals = [s.split(':') for s in args.set]
        set_key_vals = [(kv[0], ':'.join(kv[1:])) for kv in set_key_vals]
        
        fnames = _expand_files(args.files)
        for fname in fnames:
            mt_f = music_tag.load_file(fname)
            for kv in set_key_vals:
                key, val = kv[0], kv[1]
                if val:
                    mt_f[key] = val
                else:
                    del mt_f[key]
            mt_f.save()

    if args.to_csv:
        fnames = _expand_files(args.files)
        tags = [t.strip() for t in args.tags.split(':')]

        with open(args.to_csv, 'w', newline='') as fout:
            csvwriter = csv.writer(fout, delimiter=',', quotechar='"',
                                   dialect=args.csv_dialect,
                                   quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(tags + ['filename'])
            for fname in fnames:
                mt_f = music_tag.load_file(fname)
                if args.resolve:
                    row = [mt_f.resolve(k) for k in tags] + [fname]
                else:
                    row = [mt_f[k] for k in tags] + [fname]
                csvwriter.writerow(row)

    if args.from_csv:
        pth0 = ''
        if args.files and os.path.isdir(args.files[0]):
            pth0 = args.files[0]

        with open(args.from_csv, newline='') as fin:
            csvreader = csv.reader(fin, delimiter=',', quotechar='"',
                                   dialect=args.csv_dialect)
            tags = []
            for row in csvreader:
                if not tags:
                    tags = row[:-1]
                else:
                    fname = row[-1]
                    if pth0:
                        fname = os.path.join(pth0, fname)

                    if os.path.isfile(fname):
                        print('editing', fname)
                    else:
                        if args.ignore_missing:
                            print('missing file', fname, '; continuing anyway')
                            continue
                        else:
                            print('missing file', fname, '; stopping now')
                            return 1

                    mt_f = music_tag.load_file(fname)
                    for key, val in zip(tags, row[:-1]):
                        if val:
                            mt_f[key] = val
                        else:
                            del mt_f[key]
                    mt_f.save()

    return 0

if __name__ == "__main__":
    sys.exit(_main())

##
## EOF
##
