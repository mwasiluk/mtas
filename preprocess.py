#!/usr/bin/env python

import sys
import os.path
import re
# from xml.etree.ElementTree import ElementTree
# import xml.etree.cElementTree as ET
from lxml.etree import ElementTree
import lxml.etree as ET
import traceback
import logging

from optparse import OptionParser
import json
import io
import math

class Proc:
    def __init__(self, header_filename, text_strucutre_file_name='text.xml', load_pages=False, load_foreign=False, load_gaps=False, morphosyntax_filename ='ann_morphosyntax.xml', segmentation_filename='ann_segmentation.xml', segmentation_orig_filename='ann_segmentation.xml', load_foreign_from_seg_only=False):
        self.header_filename = header_filename
        self.morphosyntax_filename = morphosyntax_filename
        self.segmentation_filename = segmentation_filename
        self.segmentation_orig_filename = segmentation_orig_filename
        self.current_page = None
        self.prev_page = None
        self.text_strucutre_file_name = text_strucutre_file_name
        self.main_lang = None
        self.ns =  {'tei': 'http://www.tei-c.org/ns/1.0', 'xml': 'http://www.w3.org/XML/1998/namespace', "re": "http://exslt.org/regular-expressions", 'nkjp': "http://www.nkjp.pl/ns/1.0"}
        self.root = ET.Element("root")
        self.out_doc = ET.SubElement(self.root, "doc")

        self.load_pages = load_pages
        self.load_foreign = load_foreign
        self.load_gaps = load_gaps
        self.load_foreign_from_seg_only = load_foreign_from_seg_only

        self.pages = []
        self.foreigns = {}

        self.prevElem = None
        self.prevSeg = None

        self.is_after_gap = False
        self.gaps = {
            'left': set(),
            'right': set()
        }
        self.notes = set()
        self.fws = set()

        self.rejected = set()


        self.p_begins = set()
        self.ab_begins = set()

        self.p_begin = None
        self.ab_begin = None

        self.debug = False
        pass


    def find_corresp_morph_seg(self, ann_segmentation_seg_id):
        res = self.morph_doc.xpath(".//tei:seg[@corresp='%s#%s']" % (self.segmentation_orig_filename, ann_segmentation_seg_id),
                                   namespaces=self.ns)
        if len(res):
            return res[0]
        return None

    def find_corresp_segmentation_seg(self, ann_segmentation_seg_id):
        regex = self.get_corresp_seg_regex(ann_segmentation_seg_id)
        xpath = (".//tei:seg[re:match(@corresp,'" + regex + "')]")

        seg_parent_elem = self.seg_doc

        return self.seg_doc.xpath(xpath, namespaces=self.ns)


    def get_corresp_seg_regex(self, ann_segmentation_seg_id):
        return "%s#string-range\(%s,([0-9]+),([0-9]+)\)" % (
            self.text_strucutre_file_name, ann_segmentation_seg_id)

    def get_id(self, elem):
        if elem is None:
            return None

        id_attr_name = '{http://www.w3.org/XML/1998/namespace}id'
        if id_attr_name in elem.attrib:
            return elem.attrib[id_attr_name]
        return None

    def preprocess(self):
        ns = self.ns


        dirname = os.path.dirname(self.header_filename)
        # ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
        ET.register_namespace('xml', "http://www.w3.org/XML/1998/namespace")
        ET.register_namespace('nkjp', "http://www.nkjp.pl/ns/1.0")
        ET.register_namespace('xi', "http://www.w3.org/2001/XInclude")


        self.morph_doc = morph_doc = ET.parse(os.path.join(dirname, self.morphosyntax_filename), ET.XMLParser(huge_tree=True, recover=True, dtd_validation=False, load_dtd=False))
        self.txt_doc = txt_doc = ET.parse(os.path.join(dirname, self.text_strucutre_file_name), ET.XMLParser(huge_tree=True, recover=True, dtd_validation=False, load_dtd=False))
        self.seg_doc = seg_doc = ET.parse(os.path.join(dirname, self.segmentation_filename), ET.XMLParser(huge_tree=True, recover=True, dtd_validation=False, load_dtd=False))

        text_elem = morph_doc.find('.//tei:text', namespaces=ns)
        pages_elem = ET.Element('pages')
        text_elem.insert(0, pages_elem)

        body = txt_doc.find('.//tei:text', namespaces=ns)




        lang_attrib_name = '{http://www.w3.org/XML/1998/namespace}lang'
        try:
            self.main_lang = seg_doc.find('.//tei:text', namespaces=ns).attrib[lang_attrib_name]
        except:
            self.main_lang = ""


        if self.load_foreign_from_seg_only:
            xpath = ''
            for f_seg in seg_doc.xpath(".//tei:seg[@type='foreign']", namespaces=ns):

                if len(xpath):
                    xpath += ' or '
                id = self.get_id(f_seg)
                xpath += "@corresp='ann_segmentation.xml#%s'" % id


                # f_seg_id = self.get_id(f_seg)
                # m_seg = self.find_corresp_morph_seg(f_seg_id)
                # if m_seg is not None:
                #     m_seg.attrib['foreign'] = "true"

            if len(xpath):
                for s in self.morph_doc.xpath(".//tei:seg[%s]" % xpath, namespaces=self.ns):
                    s.attrib['foreign'] = "true"


        if self.load_pages or self.load_foreign or self.load_gaps:

            self.proc_elem(body)


            if self.current_page is not None and self.prevSeg is not None:
                self.current_page['to'] = self.get_id(self.prevSeg)




            pattern = re.compile('.*segm_((?:(?:[0-9]+)\.?)+).*')
            # print(self.pages)

            next_page_idx = 0
            next_page = None

            curr_page = None
            last_s = None

            pages_from_seg = {}
            if self.load_pages:
                if self.debug:
                    print(self.pages)

                if len(self.pages):
                    next_page = self.pages[next_page_idx]

                for p in self.pages:
                    if p['from']:
                        m = pattern.match(p['from'])
                        p['from_position'] = [int(i) for i in m.groups()[0].split('.')]
                        pages_from_seg["%s#%s" % (self.segmentation_orig_filename, p['from'])] = p
                    else:
                        p['from_position'] = False


            for s in morph_doc.xpath(".//tei:seg", namespaces=ns):
                # if next_page and "ann_segmentation.xml#%s" % (next_page['from_morph']) == s.attrib['corresp']:
                s_id = self.get_id(s)
                corresp_id = s.attrib['corresp'].replace(self.segmentation_orig_filename+'#', '')
                if next_page:
                    is_next_page_start = "%s#%s" % (self.segmentation_orig_filename, next_page['from']) == s.attrib['corresp']
                    if not is_next_page_start and s.attrib['corresp'] in pages_from_seg:

                        next_page = pages_from_seg[s.attrib['corresp']]
                        print('next page start',next_page['n'])
                        next_page_idx = self.pages.index(next_page)


                    if not is_next_page_start and next_page['from_position']:
                        m = pattern.match(s.attrib['corresp'])
                        if m:
                            position = [int(i) for i in m.groups()[0].split('.')]
                            is_next_page_start = position >= next_page['from_position']


                    if is_next_page_start:

                # if next_page and next_page['from_morph'] == self.get_id(s):
                        if self.debug:
                            print ('page', next_page['n'], self.get_id(s))
                        next_page_idx+=1


                        curr_page = next_page
                        curr_page['from_morph'] = s_id
                        if next_page_idx < len(self.pages):
                            next_page = self.pages[next_page_idx]
                        else:
                            next_page = None
                if curr_page:
                    s.attrib['pn'] = curr_page['n']

                for lang in self.foreigns:
                    if corresp_id in self.foreigns[lang]:
                        s.attrib['foreign'] = lang

                for g_type in self.gaps:
                    gl = self.gaps[g_type]

                    if corresp_id in gl:
                        s.attrib['gap_' + g_type] = 'true'

                if corresp_id in self.rejected:
                    s.attrib['rejected'] = 'true'
                else:
                    if corresp_id in self.p_begins:
                        s.attrib['p_begin'] = 'true'

                    if corresp_id in self.ab_begins:
                        s.attrib['ab_begin'] = 'true'

                if corresp_id in self.notes:
                    s.attrib['note'] = 'true'
                if corresp_id in self.fws:
                    s.attrib['fw'] = 'true'

                last_s = s

            if curr_page and curr_page['to_morph'] is None:
                curr_page['to_morph'] = self.get_id(last_s)

            if self.load_pages:
                print('found pages/total', next_page_idx, len(self.pages))

                for p in self.pages:

                    attrs = {'from': p['from_morph'], 'to': p['to_morph']}
                    for a in attrs:
                        if attrs[a] is None:
                            attrs[a]= ''
                        else:
                            attrs[a] = '#'+attrs[a]
                    attrs['n'] = p['n']

                    pages_elem.append(ET.Element('page', attrib=attrs))

        morph_doc.write(os.path.join(dirname, 'mtas_tei.xml'), encoding='utf-8', xml_declaration=True)
        # seg_doc.write(os.path.join(dirname, 'mtas_tei_seg.xml'), encoding='utf-8', xml_declaration=True)

    def is_empty_txt(self, txt):
        return not txt or not txt.strip()

    def is_empty_text_elem(self, elem):
        return self.is_empty_txt(elem.text) and self.is_empty_txt(elem.tail)

    def update_current_seg(self, seg, update_morph = False, foreign=None, fw=None, note=None):

        id = self.get_id(seg)
        rejected = False
        if "{http://www.nkjp.pl/ns/1.0}rejected" in seg.attrib:
            rejected = True
            self.rejected.add(id)

        cur_morph_seg = None
        #  and fw is None and not rejected
        if self.current_page is not None and self.current_page['from'] is None and fw is None :
            if self.debug:
                print(self.current_page['n'], id, seg.find('tei:w', namespaces=self.ns).text)
            self.current_page['from'] = id

        if update_morph and self.current_page is not None and self.current_page['from_morph'] is None:

            cur_morph_seg = self.find_corresp_morph_seg(id)
            if cur_morph_seg is not None:
                self.current_page['from_morph'] = self.get_id(cur_morph_seg)

        if self.prev_page is not None and self.prev_page['to'] is None and self.prevSeg is not None and fw is None:
            self.prev_page['to'] = self.get_id(self.prevSeg)

        if update_morph and self.prev_page is not None and self.prev_page['to_morph'] is None and self.prevSeg is not None:
            morph_seg = self.find_corresp_morph_seg(self.get_id(self.prevSeg))
            if morph_seg is not None:
                self.prev_page['to_morph'] = self.get_id(morph_seg)

        if self.current_page is not None:
            seg.attrib['pn'] = self.current_page['n']

        # if update_morph:
        #     morph_seg = self.find_corresp_morph_seg(id)
        #     if morph_seg:
        #         morph_seg.attrib['pn'] = self.current_page['n']

        if self.load_foreign and foreign is not None:
            # if not cur_morph_seg:
                # cur_morph_seg = self.find_corresp_morph_seg(id)
            try:

                self.foreigns[foreign].add(id)
            except KeyError:
                self.foreigns[foreign] = {id}
            seg.attrib['lang'] = foreign

        if self.is_after_gap:
            seg.attrib['gap_left'] = 'true'
            self.gaps['left'].add(id)
            self.is_after_gap = False


        if not rejected:
            if self.p_begin:
                seg.attrib['p_begin'] = 'true'
                self.p_begins.add(id)

            if self.ab_begin:
                seg.attrib['ab_begin'] = 'true'
                self.ab_begins.add(id)
            self.p_begin = None
            self.ab_begin = None

        if note:
            self.notes.add(id)

        if fw:
            self.fws.add(id)

        self.prevSeg = seg

    def proc_elem(self, elem, parent_trailing_segments=None, parent_text_len=0, parent_foreign=None, parent_fw=None, parent_note=None):


        current_id = self.get_id(elem)

        foreign = parent_foreign
        fw = parent_fw
        note = parent_note


        if elem.tag == '{http://www.tei-c.org/ns/1.0}pb':

                page_n = ""
                if 'n' in elem.attrib:
                    page_n = elem.attrib['n']
                    # if page_n == '54':
                    #     exit(0)

                self.prev_page = self.current_page

                self.current_page = {
                    'n': page_n,
                    'from': None,
                    'from_morph': None,
                    'to': None,
                    'to_morph': None
                }

                self.pages.append(self.current_page)

                if self.debug:
                    print(self.current_page)
        elif elem.tag == '{http://www.tei-c.org/ns/1.0}gap':

            if self.prevSeg is not None:
                self.prevSeg.attrib['gap_right'] = 'true'
                if 'reason' in elem.attrib:
                    self.prevSeg.attrib['gap_reason'] = elem.attrib['reason']
                if 'extent' in elem.attrib:
                    self.prevSeg.attrib['extent'] = elem.attrib['extent']
            self.gaps['right'].add(self.get_id(self.prevSeg))
            self.is_after_gap = True
        elif elem.tag == '{http://www.tei-c.org/ns/1.0}foreign':
            try:
                foreign = elem.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            except KeyError:
                foreign = ''

        elif elem.tag == '{http://www.tei-c.org/ns/1.0}fw':
            try:
                fw = elem.attrib['type']
            except KeyError:
                fw = None
        elif elem.tag == '{http://www.tei-c.org/ns/1.0}note':
            try:
                note = elem.attrib['place']
            except KeyError:
                note = None
        elif elem.tag == '{http://www.tei-c.org/ns/1.0}p':
            self.p_begin = current_id
        elif elem.tag == '{http://www.tei-c.org/ns/1.0}ab':
            self.ab_begin = current_id

        # if elem.tag and elem.tag.endswith('foreign'):
        #     f_lang = elem.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        #
        #     print(f_lang)


        current_elem_segments = None
        if current_id:
            current_elem_segments = self.find_corresp_segmentation_seg(current_id)
        has_segments = current_elem_segments is not None and len(current_elem_segments)

        trailing_segments = None

        tail_segments_start = None
        tail_segment = None

        corresp_seg_regex = self.get_corresp_seg_regex(current_id)
        pattern = re.compile(corresp_seg_regex)
        current_text_len = 0
        # if not fw and has_segments:
        if has_segments:
            if self.is_empty_text_elem(elem):
                if self.debug:
                    print(current_id, len(current_elem_segments))


            if not self.is_empty_txt(elem.text):
                if self.debug:
                    print('----------------------------------------------------------')
                # print (elem.text, len(elem.text))
                str = ''
                text_len = len(elem.text)
                nps = False
                for i, s in enumerate(current_elem_segments):
                    if i==0:
                        nps = '{http://www.nkjp.pl/ns/1.0}nps' in s.attrib

                    m = pattern.match(s.attrib['corresp'])
                    if m and len(m.groups()) == 2:
                        # print(m.groups(), s.find('tei:w', namespaces=self.ns).text)
                        # len_tail_len - s_end + s_len * 0.3 >= 0:
                        s_len = int(m.groups()[1])
                        if int(m.groups()[0]) + s_len <= text_len + s_len * 0.15:
                            current_text_len = max(current_text_len, int(m.groups()[0]) + s_len)
                            #here
                            self.update_current_seg(s, foreign=foreign, fw=fw, note=note)

                        else:
                            tail_segments_start = i
                            tail_segment = s
                            if self.debug:
                                print(tail_segments_start, tail_segment)
                            trailing_segments = current_elem_segments[tail_segments_start:]

                            break
                    else:
                        if self.debug:
                            print('pattern errror !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    # print(s)

                    if self.debug:
                        nps = '{http://www.nkjp.pl/ns/1.0}nps' in s.attrib
                        if not nps:
                            str += ' '
                        str += s.find('tei:w', namespaces=self.ns).text
                # if nps:
                #     current_text_len+=1
                if self.debug and current_text_len < text_len:
                    print('current_text_len < text_len', current_text_len, text_len)
                # current_text_len = text_len
                if self.debug:
                    print(str)
            else:
                trailing_segments = current_elem_segments


            # if not self.is_empty_txt(elem.tail):
            #     print('tail', current_id,  len(current_elem_segments), elem.tail)

            if tail_segment is not None and tail_segments_start < len(current_elem_segments):
                if self.debug:
                    print(tail_segments_start, len(current_elem_segments))

        if not has_segments and not self.is_empty_txt(elem.text):
            if self.debug:
                print('!!!!elem.text with no segs!!!!!!', elem.text)


        # print(elem.text)

        # parent_text_len += current_text_len
        parent_text_len += current_text_len

        for c in elem:
            if c is None:
                continue
            trailing_segments, current_text_len = self.proc_elem(c, trailing_segments, current_text_len, parent_foreign=foreign, parent_fw=fw, parent_note=note)

        if trailing_segments is not None and len(trailing_segments):
            if self.debug:
                print('*********************...........................trailing_segments not empty!!!!!!!!!!!', len(trailing_segments), current_id)
            for i, s in enumerate(trailing_segments):
                self.update_current_seg(s, foreign=parent_foreign, fw=parent_fw, note=note)


        if not self.is_empty_txt(elem.tail):
            if not parent_trailing_segments:
                if self.debug:
                    print('!!!!!!elem.tail with no parent segs!!!!!!', current_id, elem.tail)
            else:
                if self.debug:
                    print(' ----------------- parent_trailing segments + tail', len(parent_trailing_segments), len(elem.tail), parent_text_len)
                # print (elem.text, len(elem.text))
                corresp_seg_regex = self.get_corresp_seg_regex(self.get_id(elem.getparent()))
                pattern = re.compile(corresp_seg_regex)
                str = ''
                txt_len = parent_text_len
                parent_start_idx = 0
                tail_len = len(elem.tail)
                nps = False
                for i, s in enumerate(parent_trailing_segments):
                    m = pattern.match(s.attrib['corresp'])
                    if m and len(m.groups()) == 2:
                        len_tail_len = txt_len + tail_len
                        s_len = int(m.groups()[1])
                        s_end = int(m.groups()[0]) + s_len
                        if len_tail_len - s_end + s_len*0.5 >= 0:
                            parent_start_idx=i+1
                            parent_text_len=max(parent_text_len, s_end)
                            if self.debug:
                                text = s.find('tei:w', namespaces=self.ns).text
                                str += '/(%s,%s,%s)'%(m.groups()[0], m.groups()[1], len_tail_len) + text
                            # matching segment detected here !!!!
                            self.update_current_seg(s, foreign=parent_foreign, fw=parent_fw, note=parent_note)
                        else:
                            break
                    else:
                        if self.debug:
                            print('regex not matched !!!!!! tail')
                        continue

                parent_trailing_segments=parent_trailing_segments[parent_start_idx:]
                if self.debug:
                    print(str)
        # print(elem.tail)
        return parent_trailing_segments,parent_text_len

def read_bibl(elem, res, ns, attr_prefix='', date_int=False):


    # res[attr_prefix + 'title'] = ''
    title_sub = []

    title_by_level = {}
    for idx, title_elem in enumerate(elem.findall("tei:title", namespaces=ns)):


        try:
            level = title_elem.attrib['level']
        except:
            level = 'n/a'

        title_by_level[level] = title_elem.text
        if idx > 0:
            title_sub.append(title_elem.text)

    title = None
    if len(title_sub):
        res[attr_prefix + 'title_sub'] = title_sub

    if 'n/a' in title_by_level:
        title = title_by_level['n/a']

    if 'a' in title_by_level:
        title = title_by_level['a']
        if 'm' in title_by_level:
            res[attr_prefix + 'book_title'] = title_by_level['m']
    elif 'm' in title_by_level:
        title = title_by_level['m']

    if title:
        res[attr_prefix + 'title'] = title

    if 'j' in title_by_level:
        res[attr_prefix + 'series_title'] = title_by_level['j']

    try:
        res[attr_prefix+'author'] = elem.find('tei:author', namespaces=ns).text
    except:
        # res[attr_prefix+'author'] = ''
        pass
    try:
        res[attr_prefix+'editor'] = elem.find("tei:editor[@role='editor']", namespaces=ns).text
    except:
        # res[attr_prefix+'editor'] = ''
        pass

    try:
        res[attr_prefix+'translator'] = elem.find("tei:editor[@role='translator']", namespaces=ns).text
    except:
        # res[attr_prefix+'translator'] = ''
        pass
    try:
        res[attr_prefix+'publisher'] = elem.find('tei:publisher', namespaces=ns).text
    except:
        pass
        # res[attr_prefix+'publisher'] = ''

    try:
        res[attr_prefix+'place'] = elem.find("tei:pubPlace[@role='place']", namespaces=ns).text
    except:
        if not attr_prefix:
            res[attr_prefix+'place'] = 'nieznane'
    try:
        res[attr_prefix+'region'] = elem.find("tei:pubPlace[@role='region']", namespaces=ns).text
    except:
        if not attr_prefix:
            res[attr_prefix+'region'] = 'nieznane'

    for scope_elem in elem.findall("tei:biblScope", namespaces=ns):
        if 'unit' in scope_elem.attrib:
            res[attr_prefix + scope_elem.attrib['unit']] = scope_elem.text

    try:
        res[attr_prefix + 'text_origin'] = elem.find("tei:note[@type='text_origin']", namespaces=ns).text
    except:
        pass

    try:
        d = elem.find('tei:date', namespaces=ns)
        date_str = d.text
        res[attr_prefix + 'date'] = date_str

        if not date_int:
            not_before = None
            not_after = None

            if d is not None:

                if 'when' in d.attrib:
                    not_after = not_before = int(d.attrib['when'])
                if 'notBefore' in d.attrib:
                    not_before = int(d.attrib['notBefore'])
                if 'notAfter' in d.attrib:
                    not_after = int(d.attrib['notAfter'])

            if not_after is None and not_before is not None:
                not_after = int(math.ceil(not_before/50.0)) * 50

            if not_before is None and not_after is not None:
                not_before = int(math.floor(not_after / 50.0)) * 50 + 1

            res[attr_prefix + 'not_after'] = not_after
            res[attr_prefix + 'not_before'] = not_before
        elif date_str:
            try:
                if 'when' in d.attrib:
                    date_int_val = int(d.attrib['when'])
                else:
                    date_int_val = int(date_str)
                res[attr_prefix + 'date_int'] = date_int_val
            except:
                pass

    except:
        # res[attr_prefix+'date'] = ''
        pass

    refs = [e.attrib['target'] for e in elem.findall("tei:ref", namespaces=ns) if 'target' in e.attrib]
    if len(refs):
        res[attr_prefix + 'link'] = refs

    child_bibl = elem.find("tei:bibl[@type]", namespaces=ns)

    if child_bibl is not None:
        read_bibl(child_bibl, res, ns, attr_prefix+child_bibl.attrib['type']+'_', date_int)



def get_metadata(filename, prefix='', date_int=False, preprocessing=False, morphosyntax_filename='ann_morphosyntax.xml'):

    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    doc = ElementTree(file = filename)
    if preprocessing:
        mtas_file_name = 'mtas_tei.xml'
    else:
        mtas_file_name = morphosyntax_filename
    res = {
        'type': 'tei',
        'text_data': prefix+os.path.join(os.path.dirname(filename), mtas_file_name)
    }

    bibl_elem = doc.find(".//tei:sourceDesc/tei:bibl[@type='original']", namespaces=ns)
    read_bibl(bibl_elem, res, ns, '', date_int)

    modernized_elem = bibl_elem.find("tei:bibl[@type='modernized']", namespaces=ns)

    if modernized_elem is not None:
        res['modernized'] = True
        monogr_elem = modernized_elem.find("tei:bibl[@type='monogr']", namespaces=ns)
        read_bibl(modernized_elem, res, ns, 'modernized_', date_int)
    else:
        res['modernized'] = False

    try:
        res['id'] = doc.find('.//tei:sourceDesc/tei:bibl/tei:idno', namespaces=ns).text
    except:
        res['id'] = os.path.basename(os.path.dirname(filename))

    try:
        res['availability'] = doc.find('.//tei:publicationStmt/tei:availability', namespaces=ns).attrib['status']
    except:
        res['availability'] = 'unknown'



    text_class_elem = doc.find('.//tei:profileDesc/tei:textClass', namespaces=ns)

    for c in ('text', 'genre', 'kind', 'subject', 'ironic'):
        try:

            res[c] = text_class_elem.find('tei:catRef[@scheme="#%s"]' % c, namespaces=ns).attrib['target']
            arr = re.findall(r"#([^#]+)", res[c])
            if len(arr) > 0:
                res[c] = [s.strip() for s in arr]
            else:
                res[c] = [res[c].strip()]
        except:
            pass


    return [res]



if not sys.argv[1:]:
    print("Usage:", sys.argv[0], " file_to_convert ...")
    print()
    sys.exit(1)


def go():
    parser = OptionParser(usage="Tool for converting tei header to json with solr document metadata")
    parser.add_option('-p', '--prefix', type='string', action='store', default="",
                      dest='prefix',
                      help='file name prefix')
    parser.add_option('-t', '--text-name', type='string', action='store', default="text.xml",
                      dest='text_name',
                      help='text structure file name, default: text.xml')
    parser.add_option('--morph', '--morph-name', type='string', action='store', default="ann_morphosyntax.xml",
                      dest='morph_name',
                      help='ann_morphosyntax file name, default: ann_morphosyntax.xml')
    parser.add_option('--seg', '--seg-name', type='string', action='store', default="ann_segmentation.xml",
                      dest='seg_name',
                      help='segmentation file name, default: ann_segmentation.xml')
    parser.add_option('--seg-orig', '--seg-orig-name', type='string', action='store', default="ann_segmentation.xml",
                      dest='seg_orig_name',
                      help='original segmentation file name (used in text structure references), default: ann_segmentation.xml')
    parser.add_option('--pages', action='store_true',
                      dest='load_pages',
                      help='load pages from text structure')
    parser.add_option('--foreign', action='store_true',
                      dest='load_foreign',
                      help='load foreign lang from text structure')
    parser.add_option('--foreign-seg', action='store_true',
                      dest='load_foreign_from_seg',
                      help='load foreign lang from segmentation file only')
    parser.add_option('--date-int', action='store_true',
                      dest='date_int',
                      help='do not create date ranges (not_before and not_after) - create date_int instead')
    parser.add_option('--gaps', action='store_true',
                      dest='load_gaps',
                      help='load gaps')
    (options, args) = parser.parse_args()

    if len(args) < 1:
        print('Need to provide input')

        print('See --help for details.')
        sys.exit(1)
    for i, filename in enumerate(args):
        print('%3d/%d: %s' % (i + 1, len(args), filename))

        try:
            preprocessing = options.load_pages or options.load_foreign or options.load_foreign_from_seg or options.load_gaps

            meta = get_metadata(filename, options.prefix, options.date_int, preprocessing)

            if preprocessing:
                p = Proc(filename, text_strucutre_file_name = options.text_name, load_pages=options.load_pages, load_foreign=options.load_foreign,
                         load_gaps=options.load_gaps, morphosyntax_filename=options.morph_name, segmentation_filename=options.seg_name, segmentation_orig_filename=options.seg_orig_name,
                         load_foreign_from_seg_only = options.load_foreign_from_seg)
                p.preprocess()
                meta[0]['lang'] = p.main_lang

            with io.open(os.path.join(os.path.dirname(filename), 'doc.json'), 'w', encoding='UTF-8') as f:
                json.dump(meta, f)

        except Exception as e:
            print("error processing", filename)
            logging.error(traceback.format_exc())



if __name__ == '__main__':
    go()