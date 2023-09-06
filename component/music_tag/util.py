from collections import namedtuple
import re
import struct


try:
    string_types = basestring
except NameError:
    string_types = str


def as_str(value):
    if isinstance(value, (list, tuple)):
        value = ', '.join(value)
    return str(value)

def sanitize_year(year):
    try:
        if ',' in year:
            year = year.split(',')[0]
            # TODO: warn that we're dropping a 2nd year
    except TypeError:
        pass
    
    try:
        year = int(year)
    except ValueError:
        if re.match(r'^[0-9]{4}[-\s][0-9]{2}[-\s][0-9]{2}$', year):
            year = int(year[:4])
        elif re.match(r'^[0-9]{2}[-/\s][0-9]{2}[-/\s][0-9]{4}$', year):
            year = int(year[-4:])
        else:
            raise ValueError("Could not extract year from: {0}".format(year))
    return year

def sanitize_int(val):
    try:
        ret = int(val)
    except ValueError:
        m = re.match(r'^.*?([0-9]+).*?$', val)
        if m:
            ret = int(m.group(1))
        else:
            raise ValueError('int contains no in {0}'.format(val))
    return ret

def sanitize_bool(val):
    val = str(val).strip().lower()
    if val in ('true', '1'):
        return True
    elif val in ('false', '0', ''):
        return False
    else:
        return int(val) !=0

def get_easy_tracknum(afile, norm_key, _tag_name='tracknumber'):
    tracknumber = str(afile.mfile.get(_tag_name, None))
    if tracknumber in (None, 'None'):
        tracknumber = None
    else:
        tracknumber = tracknumber.split('/')[0]
    return tracknumber

def set_easy_tracknum(afile, norm_key, val, _tag_name='tracknumber'):
    tracknumber = [i for i in str(afile.mfile.get(_tag_name, '0/0')).split('/')]
    tracknumber += [0] * (2 - len(tracknumber))
    tracknumber[0] = val
    afile.set_raw(norm_key, _tag_name,
                  '/'.join(str(i) for i in tracknumber),
                  appendable=False)

def get_easy_totaltracks(afile, norm_key, _tag_name='tracknumber'):
    tracknumber = str(afile.mfile.get(_tag_name, None))
    if tracknumber in (None, 'None'):
        tracknumber = None
    else:
        try:
            tracknumber = tracknumber.split('/')[1]
        except IndexError:
            tracknumber = None
    return tracknumber

def set_easy_totaltracks(afile, norm_key, val, _tag_name='tracknumber'):
    tracknumber = [i for i in str(afile.mfile.get(_tag_name, '0/0')).split('/')]
    tracknumber += [0] * (2 - len(tracknumber))
    tracknumber[1] = val
    afile.set_raw(norm_key, _tag_name,
                  '/'.join(str(i) for i in tracknumber),
                  appendable=False)

def get_easy_discnum(afile, norm_key, _tag_name='discnumber'):
    discnumber = str(afile.mfile.get(_tag_name, None))
    if discnumber in (None, 'None'):
        discnumber = None
    else:
        discnumber = discnumber.split('/')[0]
    return discnumber

def set_easy_discnum(afile, norm_key, val, _tag_name='discnumber'):
    discnumber = [i for i in str(afile.mfile.get(_tag_name, '0/0')).split('/')]
    discnumber += [0] * (2 - len(discnumber))
    discnumber[0] = val
    afile.set_raw(norm_key, _tag_name,
                  '/'.join(str(i) for i in discnumber),
                  appendable=False)

def get_easy_totaldiscs(afile, norm_key, _tag_name='discnumber'):
    discnumber = str(afile.mfile.get(_tag_name, None))
    if discnumber in (None, 'None'):
        discnumber = None
    else:
        try:
            discnumber = discnumber.split('/')[1]
        except IndexError:
            discnumber = None
    return discnumber

def set_easy_totaldiscs(afile, norm_key, val, _tag_name='discnumber'):
    discnumber = [i for i in str(afile.mfile.get(_tag_name, '0/0')).split('/')]
    discnumber += [0] * (2 - len(discnumber))
    discnumber[1] = val
    afile.set_raw(norm_key, _tag_name,
                  '/'.join(str(i) for i in discnumber),
                  appendable=False)

PicBlock = namedtuple('PicBlock', ('typeid', 'picturetype', 'mime', 'format',
                                   'descr', 'width', 'height', 'color_depth',
                                   'colors_indexed', 'data'))
PICTURE_TYPE_LUT = {0: 'other', 1: 'icon', 2: 'other icon', 3: 'front cover',
                    4: 'back cover', 5: 'leaflet', 6: 'media', 7: 'lead artist',
                    8: 'artist', 9: 'conductor', 10: 'band', 11: 'composer',
                    12: 'lyricist', 13: 'recording location',
                    14: 'during recording', 15: 'during performance',
                    16: 'screen capture', 17: 'coloured fish', 18: 'illustration',
                    19: 'artist logo', 20: 'publisher logo'}

def _split(it, i):
    return it[:i], it[i:]

def parse_picture_block(dat):
    head, rest = _split(dat, 2 * 4)
    typeid, mime_len = struct.unpack('>ii', head)
    mime, rest = _split(rest, mime_len)
    mime = mime.decode('ascii').lower()
    head, rest = _split(rest, 1 * 4)
    descr_len, = struct.unpack('>i', head)
    descr, rest = _split(rest, descr_len)
    descr = descr.decode('utf-8')
    head, rest = _split(rest, 5 * 4)
    width, height, cdepth, cidx, dat_len = struct.unpack('>iiiii', head)
    dat = rest
    pic = PicBlock(typeid=typeid, picturetype=PICTURE_TYPE_LUT[typeid],
                   mime=mime, format=mime.split('/')[1],
                   descr=descr, width=width, height=height, color_depth=cdepth,
                   colors_indexed=cidx, data=dat)
    assert len(dat) == dat_len
    return pic
