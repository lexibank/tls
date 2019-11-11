from pathlib import Path

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
            id_factory=lambda x: "%s_%s" % (x.id.split("-")[-1], slug(x.gloss)),
            lookup_factory="Name",
        )

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
