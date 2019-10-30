import attr
from pathlib import Path
import re

from pylexibank import Concept
from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "tls"

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

        # TODO: add STEM and PREFIX? (pay attention to multiple forms)
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

