import attr
from pathlib import Path
import re

from pylexibank import Concept
from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import FormSpec

from clldutils.misc import slug


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "tls"
    form_spec = FormSpec(
        brackets={"[": "]", "{": "}", "(": ")"},
        separators=",;/",
        missing_data=("-",),
        replacements=[(" ? ", " ")],  # denotes uncertainty; note spaces
    )

    def cmd_makecldf(self, args):
        # Add sources
        args.writer.add_sources()

        # Add languages
        language_lookup = args.writer.add_languages(lookup_factory="Name")

        # Add concepts
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: "%s_%s" % (x.number, slug(x.gloss)),
            lookup_factory="Name",
        )

        # TODO: add STEM and PREFIX? (pay attention to multiple forms)
        for entry in progressbar(self.raw_dir.read_csv("tls.txt", dicts=True)):
            # Skip over when language is "Note" (internal comments) or
            # "Gweno1" (a copy of "Gweno")
            if entry["LGABBR"] in ["Note", "Gweno1"]:
                continue

            # Skip over cross-references; it was manually checked that
            # all entries beginning with "see " are indeed cross-references
            if entry["REFLEX"].startswith("see "):
                continue

            # There are also cross-references with page/entry number at the
            # end of the string, but these entries contain data. The easieast
            # way to strip it is to use a regular expression directly on
            # the raw string, as those cannot be used in FormSpec
            # The regular expression matches a number of spaces, plus a
            # reference (composed of digits and dashes), at the end of
            # the string.
            ref_re = re.compile(
                r"""\s+     # at least one space
                    [0-9-]+ # followed by at least one digit/dash
                    $       # at the end of the string""",
                re.VERBOSE)
            entry["REFLEX"] = re.sub(ref_re, "", entry["REFLEX"])

            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LGABBR"]],
                Parameter_ID=concept_lookup[entry["GLOSS"]],
                Value=entry["REFLEX"],
                Source=["Nurse1975", "Nurse1979", "Nurse1980", "TLS1999"],
            )
