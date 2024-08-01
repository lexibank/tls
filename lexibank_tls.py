import re
from pathlib import Path

import attr
import pylexibank
from clldutils.misc import slug

# Define list of substring replacements for data cleaning
REPLACEMENTS = []


@attr.s
class CustomConcept(pylexibank.Concept):
    Swahili_Gloss = attr.ib(default=None)
    NUMBER = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "tls"
    writer_options = dict(keep_languages=False, keep_parameters=False)

    concept_class = CustomConcept
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")", "[": "]"},
        separators=",;/",
        missing_data=("-", "?", "???", "+", "_", "--_", "!"),
        replacements=[
            ("(kU)d\x97s\x87 ? +", ""),
            ("\x88", ""),
            ("\x87", ""),
            ("\x97", ""),
            (" ", "_"),
            ("#__#_pencil_only_#", ""),
            ('"', ""),
            ("kuwuka_kimus#", "kuwaka_kimus"),
            ("__#_note_2nd_hand_here", ""),
            ("never_stands_alone", "-"),
            ("depends_on_what_is_sacrificed", "-"),
            ("kunuka_akisa_|_bukomu", "kunuka_akisa"),
            ("kufwila_|_kutema_matye", "kufwila"),
            ("ekyora__pl.____also_eghekere", "ekyora"),
            ("see__412", "-"),
            ("e.g.construct_a_boat", "-"),
            ("see_935", "-"),
            ("ku_see_#528", "ku"),
            ("397", "-"),
            ("clans", "-"),
            ("right_person", "-"),
            ("shitere_shi_shilenj..", "shitere"),
            ("#", ""),
        ],
        first_form_only=True,
    )

    def cmd_makecldf(self, args):
        concepts = {}

        for concept in self.conceptlists[0].concepts.values():
            idx = concept.id.split("-")[-1] + "_" + slug(concept.english)
            concepts[concept.number] = idx
            args.writer.add_concept(
                ID=idx,
                Name=concept.english,
                NUMBER=concept.number,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
                Swahili_Gloss=concept.attributes["swahili"],
            )

        # Add sources
        args.writer.add_sources()

        # Add languages
        language_lookup = args.writer.add_languages(lookup_factory="Name")

        # TODO: add STEM and PREFIX? (pay attention to multiple forms)
        for entry in pylexibank.progressbar(self.raw_dir.read_csv("tls.txt", dicts=True)):
            # Skip over when language is "Note" (internal comments) or
            # "Gweno1" (a copy of "Gweno")
            if entry["LGABBR"] in ["Note", "Gweno1"]:
                continue

            src_idx = entry["SRCID"].replace(".0", "").replace(".5", "a")

            # Fix values if possible (for common problems not in lexemes.csv)
            value = entry["REFLEX"]

            if src_idx not in concepts:
                continue

            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LGABBR"]],
                Parameter_ID=concepts[src_idx],
                Value=value,
                Source=["Nurse1975", "Nurse1979", "Nurse1980", "TLS1999"],
            )
