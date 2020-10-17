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
            ("(general)", ""),  # comment
            ("[general]", ""),  # comment
            ("(modern)", ""),  # comment
            ("(see below)", ""),  # comment
            ("(uncommon)", ""),  # comment
            (" ? ", " "),  # denotes uncertainty; note spaces
            ("(?)", ""),  # uncertainty
            ("(!)", ""),  # not clear -- surprising data?
            ("(?!)", ""),  # not clear -- surprising data?
            ("(noun)", ""), # grammar
            ("(object)", ""), # grammar
            ("(pl)", ""), # grammar
            ("(s.)", ""), # grammar
            ("(s.+pl.)", ""), # grammar
            ("(sg)", ""), # grammar
            ("[+ poss.]", ""), # grammar
            ("[gen.]", ""), # grammar
            ("(sing.)", ""), # grammar
            ("(sing.oromambo)", ""), # grammar
            ("(adopted)", ""), # etymology
            ("(eng.)", ""), # etymology
            ("(swahili)", ""), # etymology

            ("(a?)", "a"),  # phonology
            ("(a)", "a"),  # phonology
            ("(y)", "y"),  # phonology
            ("(cha)", "cha"),  # morpheme
            ("(e)", "e"),  # phonology
            ("(g)", "g"),  # morpheme
            ("(gU)", "gU"),  # morpheme
            ("(gu)", "gu"),  # phonology
            ("(h)", "h"),  # phonology
            ("(i)", "i"),  # phonology
            ("(k)", "k"),  # morpheme
            ("(khu)", "khu"),  # morpheme
            ("(ki)", "ki"),  # phonology
            ("(ko)", "ko"),  # morpheme
            ("(ku)", "ku"),  # morpheme
            ("(kU)", "kU"),  # morpheme
            ("(kw)", "kw"),  # morpheme
            ("(kwa)", "kwa"),  # phonology
            ("(kwe)", "kwe"),  # phonology
            ("(kwi)", "kwi"),  # morpheme
            ("(l)", "l"),  # phonology
            ("(li)", "li"),  # morpheme
            ("(ma-)", "ma-"),  # morpheme
            ("(ma)", "ma"),  # morpheme
            ("(mu)", "mu"),  # morpheme
            ("(n)", "n"),  # phonology
            ("(na)", "na"),  # morpheme
            ("(o)", "o"),  # phonology
            ("(oko)", "oko"),  # morpheme
            ("(oku)", "oku"),  # morpheme
            ("(okw)", "okw"),  # morpheme
            ("(s)", "s"),  # phonology
            ("(t)", "t"),  # morpheme
            ("(u)", "u"),  # phonology
            ("(uku)", "uku"),  # morpheme
            ("(ukw)", "ukw"),  # morpheme
            ("(w)", "w"),  # phonology
            ("(wa)", "wa"),  # morpheme
            ("(ya)", "ya"),  # morpheme
            ("(zi)", "zi"),  # morpheme

            ('(verb of carrying the things and piling them)', ""), # gloss
            ("[b-i-l]", ""), # gloss
            ("[s-i-l]", ""), # gloss
            ("(animal)", ""),  # gloss
            ("(animals)", ""),  # gloss
            ("(banana tree)", ""),  # gloss
            ("(belly)", ""),  # gloss
            ("(big iron)", ""),  # gloss
            ("(birds)", ""),  # gloss
            ("(borrow)", ""),  # gloss
            ("(boy)", ""),  # gloss
            ("(boys)", ""),  # gloss
            ("(brother in law)", ""),  # gloss
            ("(cattle)", ""),  # gloss
            ("(chin,jaw)", ""),  # gloss
            ("(crust)", ""),  # gloss
            ("(dying animals)", ""),  # gloss
            ("(eyes)", ""),  # gloss
            ("(father in law)", ""),  # gloss
            ("(female)", ""),  # gloss
            ("(for a person)", ""),  # gloss
            ("(girl)", ""),  # gloss
            ("(girls)", ""),  # gloss
            ("(grandpa)", ""),  # gloss
            ("(grass)", ""),  # gloss
            ("(green)", ""),  # gloss
            ("(groan)", ""),  # gloss
            ("(grow up,ripen)", ""),  # gloss
            ("(heat)", ""),  # gloss
            ("[male]", ""),  # gloss
            ("[female]", ""),  # gloss
            ("(human)", ""),  # gloss
            ("(hyena)", ""),  # gloss
            ("(lend)", ""),  # gloss
            ("(lion)", ""),  # gloss
            ("(listen)", ""),  # gloss
            ("(male)", ""),  # gloss
            ("(mother)", ""),  # gloss
            ("(mouth)", ""),  # gloss
            ("(nest)", ""),  # gloss
            ("(of church)", ""),  # gloss
            ("(of house)", ""),  # gloss
            ("(people)", ""),  # gloss
            ("(-human)", ""),  # gloss
            ("(person)", ""),  # gloss
            ("(seed,grain)", ""),  # gloss
            ("(sick person)", ""),  # gloss
            ("(a sick person)", ""),  # gloss
            ("(sister in law)", ""),  # gloss
            ("(sister)", ""),  # gloss
            ("(skin bark)", ""),  # gloss
            ("(smoking)", ""),  # gloss
            ("(snail)", ""),  # gloss
            ("(arm)", ""),  # gloss
            ("(hands)", ""),  # gloss
            ("(hand)", ""),  # gloss
            ("(-idi in counting)", ""),  # gloss
            ("(biki=piece of wood)", ""),  # gloss
            ("(unexpectedly)", ""),  # gloss
            ("(spoil,destroy)", ""),  # gloss
            ("(thick forest)", ""),  # gloss
            ("(thick foest)", ""),  # gloss
            ("(thing)", ""),  # gloss
            ("(unripe)", ""),  # gloss
            ("(woman)", ""),  # gloss
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
