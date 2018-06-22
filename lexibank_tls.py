# coding=utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict
import re

import attr
from dbfread import DBF
from clldutils.dsv import reader, UnicodeWriter
from clldutils.text import split_text
from clldutils.path import Path
from clldutils.misc import slug

from pylexibank.dataset import Metadata, Concept
from pylexibank.dataset import Dataset as BaseDataset


@attr.s
class TLSConcept(Concept):
    Swahili_gloss = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    concept_class = TLSConcept

    def cmd_download(self, **kw):
        with self.raw.temp_download(
                "http://www.cbold.ish-lyon.cnrs.fr/Load.aspx?"
                "Langue=TLS&Type=FoxPro&Fichier=TLS.NursePhillipson1975.dbf",
                'tls.dbf',
                log=self.log) as dbf:
            with UnicodeWriter(self.raw.joinpath('tls.txt')) as w:
                for i, rec in enumerate(DBF(dbf.as_posix(), encoding='latin1')):
                    if i == 0:
                        w.writerow(rec.keys())
                    if not rec['REFLEX'].strip() or not rec['GLOSS'].strip():
                        continue
                    row = []
                    for col in rec.values():
                        col = '' if col is None else col
                        row.append(col if isinstance(col, int) else col.strip())
                    w.writerow(row)

    def cmd_install(self, **kw):
        concept_map = {}
        for c in self.concepts:
            concept_map[c['GLOSS_IN_SOURCE']] = c['CONCEPTICON_ID'] or None

        words = list(map(normalized, reader(self.raw.joinpath('tls.txt'),
            dicts=True)))
        glosses = defaultdict(set)
        swas = defaultdict(set)

        with self.cldf as ds:
            for language in self.languages:
                ds.add_language(
                        ID=language['ID'],
                        Glottocode=language['GLOTTOCODE'],
                        Name=language['NAME'])

            for concept in self.concepts:
                ds.add_concept(
                    ID=slug(concept['GLOSS_IN_SOURCE']),
                    Name=concept['GLOSS_IN_SOURCE'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Concepticon_Gloss=concept['CONCEPTICON_GLOSS'])

            for i, word in enumerate(words):
                if word['LGABBR']:
                    # don't carry internal notes
                    if word['LGABBR'] == 'Note':
                        continue
                
                    for form in split_text(word['REFLEX'], separators=',;/'):
                        # remove any additional information (notes, plurals, etc.)
                        form = form.split('(')[0].strip()

                        if form:
                            for row in ds.add_lexemes(
                                    Language_ID=slug(word['LGABBR']),
                                    Parameter_ID=slug(word['GLOSS']),
                                    Value=word['REFLEX'],
                                    Form=form):
                                pass

SWAHILI_GLOSS = re.compile('\(=(?P<gloss>[^\)]+)\)')
def normalized(d):
    match = SWAHILI_GLOSS.search(d['GLOSS'])
    if match and not d['SWAHILI']:
        swa = match.group('gloss').strip()
        if swa in ['mbogo', 'tembo', 'moja', 'munyu', 'tisa', 'ndege', 'fumo']:
            d['GLOSS'] = SWAHILI_GLOSS.sub('', d['GLOSS']).strip()
            d['SWAHILI'] = swa
    return d
