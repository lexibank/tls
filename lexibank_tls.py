import attr
from pathlib import Path
import re

from pylexibank import Concept
from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset


SWAHILI_GLOSS = re.compile(r"(=(?P<gloss>[^)]+))")


def normalized(d):
    match = SWAHILI_GLOSS.search(d["GLOSS"])
    if match and not d["SWAHILI"]:
        swa = match.group("gloss").strip()
        if swa in ["mbogo", "tembo", "moja", "munyu", "tisa", "ndege", "fumo"]:
            d["GLOSS"] = SWAHILI_GLOSS.sub("", d["GLOSS"]).strip()
            d["SWAHILI"] = swa
    return d


@attr.s
class TLSConcept(Concept):
    Swahili_gloss = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "tls"
    concept_class = TLSConcept

    # TODO: work on the download
    def cmd_download(self, args):
        with self.raw.temp_download(
            "http://www.cbold.ish-lyon.cnrs.fr/Load.aspx?"
            "Langue=TLS&Type=FoxPro&Fichier=TLS.NursePhillipson1975.dbf",
            "tls.dbf",
            log=self.log,
        ) as dbf:
            with UnicodeWriter(self.raw.joinpath("tls.txt")) as w:
                for i, rec in enumerate(DBF(dbf.as_posix(), encoding="latin1")):
                    if i == 0:
                        w.writerow(rec.keys())
                    if not rec["REFLEX"].strip() or not rec["GLOSS"].strip():
                        continue
                    row = []
                    for col in rec.values():
                        col = "" if col is None else col
                        row.append(col if isinstance(col, int) else col.strip())
                    w.writerow(row)

    def cmd_makecldf(self, args):
        # Add sources
        args.writer.add_sources()

        # Add languages
        language_lookup = args.writer.add_languages(lookup_factory="Name")

        # Add concepts
        concept_lookup = args.writer.add_concepts(lookup_factory="Name")

        # TODO: add STEM and PREFIX (pay attention to multiple forms)
        for entry in progressbar(self.raw_dir.read_csv("tls.txt", dicts=True)):
            # Skip over when language is "Note" (internal comments) or
            # "Gweno1" (a copy of "Gweno")
            if entry["LGABBR"] in ["Note", "Gweno1"]:
                continue

            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LGABBR"]],
                Parameter_ID=concept_lookup[entry["GLOSS"]],
                Value=entry["REFLEX"],
                Source=["Nurse1975", "Nurse1979", "Nurse1980", "TLS1999"],
            )

        return

        print(words)
        return

        with self.cldf as ds:
            ds.add_sources(self.raw.read("sources.bib"))
            ds.add_languages()
            ds.add_concepts(id_factory=lambda c: slug(c.label))

            for i, word in pb(enumerate(words), desc="add words"):
                if word["LGABBR"]:
                    # don't carry internal notes
                    if word["LGABBR"] == "Note":
                        continue

                    for form in split_text(word["REFLEX"], separators=",;/"):
                        # remove any additional information (notes, plurals, etc.)
                        form = strip_brackets(
                            form, brackets={"[": "]", "{": "}", "(": ")"}
                        )

                        if form and form != "-":
                            ds.add_lexemes(
                                Language_ID=slug(word["LGABBR"]),
                                Parameter_ID=slug(word["GLOSS"]),
                                Value=word["REFLEX"],
                                Source=[
                                    "Nurse1975",
                                    "Nurse1979",
                                    "Nurse1980",
                                    "TLS1999",
                                ],
                                Form=form,
                            )
