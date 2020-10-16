from pathlib import Path
import re

from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import FormSpec

from clldutils.misc import slug


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "tls"
    form_spec = FormSpec(
        brackets={},
        separators=",;/",
        missing_data=("-",),
        replacements=[
            ("(see below)", ""),  # comment
            (" ? ", " "),  # denotes uncertainty; note spaces
            ("(?)", ""),  # uncertainty
            ("(!)", ""),  # not clear -- surprising data?
            
            ("(i)", "i"),  # phonology
            ("(u)", "u"),  # phonology
            ("(ku)", "ku"),  # morpheme
            ("(li)", "li"),  # morpheme
            ("(uku)", "uku"),  # morpheme

            ("(belly)", ""),  # gloss
            ("(chin,jaw)", ""),  # gloss
            ("(crust)", ""),  # gloss
            ("(grandpa)", ""),  # gloss
            ("(green)", ""),  # gloss
            ("(grow up,ripen)", ""),  # gloss
            ("(heat)", ""),  # gloss
            ("(hyena)", ""),  # gloss
            ("(mother)", ""),  # gloss
            ("(seed,grain)", ""),  # gloss
            ("(skin bark)", ""),  # gloss
            ("(spoil,destroy)", ""),  # gloss
        ],
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

            # Fix values if possible (for common problems not in lexemes.csv)
            value = entry["REFLEX"]

            # Delete plural annotations of the type "(pl. <form>)", which might be
            # preceded by stray commas and spaces, like "lihamba, (pl. mahamba)"
            value = re.sub(r",?\s*\(pl\.[^)]*\)", "", value)

            # Delete "cf." notations in parentheses -- note the dot or spaces
            value = re.sub(r"\(cf\.[^)]*\)", "", value)
            value = re.sub(r"\(cf\s[^)]*\)", "", value)

            # Delete "see ", "also ", and "from " notations in parentheses
            # -- note the spaces
            value = re.sub(r"\(see\s[^)]*\)", "", value)
            value = re.sub(r"\(also\s[^)]*\)", "", value)
            value = re.sub(r"\(from\s[^)]*\)", "", value)

            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LGABBR"]],
                Parameter_ID=concept_lookup[entry["GLOSS"]],
                Value=value,
                Source=["Nurse1975", "Nurse1979", "Nurse1980", "TLS1999"],
            )
