import re
from pathlib import Path

import attr
import pylexibank
from clldutils.misc import slug

# Define list of substring replacements for data cleaning
REPLACEMENTS = [
    ("(general)", ""),  # comment
    ("(modern)", ""),  # comment
    ("(see below)", ""),  # comment
    ("(uncommon)", ""),  # comment
    ("[general]", ""),  # comment
    (" ? ", " "),  # denotes uncertainty; note spaces
    ("(?)", ""),  # uncertainty
    ("(!)", ""),  # not clear -- surprising data?
    ("(?!)", ""),  # not clear -- surprising data?
    ("(noun)", ""),  # grammar
    ("(object)", ""),  # grammar
    ("(pl)", ""),  # grammar
    ("(s.)", ""),  # grammar
    ("(s.+pl.)", ""),  # grammar
    ("(sg)", ""),  # grammar
    ("(sing.)", ""),  # grammar
    ("(sing.oromambo)", ""),  # grammar
    ("[+ poss.]", ""),  # grammar
    ("[gen.]", ""),  # grammar
    ("(adopted)", ""),  # etymology
    ("(eng.)", ""),  # etymology
    ("(swahili)", ""),  # etymology
    ("(a?)", "a"),  # phonology
    ("(a)", "a"),  # phonology
    ("(cha)", "cha"),  # morpheme
    ("(e)", "e"),  # phonology
    ("(g)", "g"),  # morpheme
    ("(gU)", "gU"),  # morpheme
    ("(gu)", "gu"),  # phonology
    ("(h)", "h"),  # phonology
    ("(i)", "i"),  # phonology
    ("(y)", "y"),  # phonology
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
    ("(-human)", ""),  # gloss
    ("(-idi in counting)", ""),  # gloss
    ("(a sick person)", ""),  # gloss
    ("(anim.)", ""),  # gloss
    ("(animal)", ""),  # gloss
    ("(animals)", ""),  # gloss
    ("(arm)", ""),  # gloss
    ("(banana tree)", ""),  # gloss
    ("(belly)", ""),  # gloss
    ("(big iron)", ""),  # gloss
    ("(biki=piece of wood)", ""),  # gloss
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
    ("(fam.)", ""),  # gloss
    ("(father in law)", ""),  # gloss
    ("(female)", ""),  # gloss
    ("(fire)", ""),  # gloss
    ("(for a person)", ""),  # gloss
    ("(girl)", ""),  # gloss
    ("(girls)", ""),  # gloss
    ("(grandpa)", ""),  # gloss
    ("(grass)", ""),  # gloss
    ("(green)", ""),  # gloss
    ("(groan)", ""),  # gloss
    ("(grow up,ripen)", ""),  # gloss
    ("(hand)", ""),  # gloss
    ("(hands)", ""),  # gloss
    ("(heat)", ""),  # gloss
    ("(hole)", ""),  # gloss
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
    ("(person)", ""),  # gloss
    ("(seed,grain)", ""),  # gloss
    ("(sick person)", ""),  # gloss
    ("(sister in law)", ""),  # gloss
    ("(sister)", ""),  # gloss
    ("(skin bark)", ""),  # gloss
    ("(smoking)", ""),  # gloss
    ("(snail)", ""),  # gloss
    ("(spoil,destroy)", ""),  # gloss
    ("(thick foest)", ""),  # gloss
    ("(thick forest)", ""),  # gloss
    ("(thing)", ""),  # gloss
    ("(unexpectedly)", ""),  # gloss
    ("(unripe)", ""),  # gloss
    ("(verb of carrying the things and piling them)", ""),  # gloss
    ("(water)", ""),  # gloss
    ("(woman)", ""),  # gloss
    ("[b-i-l]", ""),  # gloss
    ("[female]", ""),  # gloss
    ("[male]", ""),  # gloss
    ("[s-i-l]", ""),  # gloss
    # Extra material, from automatic processing
    ("( before heavy rains-litulo)", ""),  #
    ("( trad. langi =kiriva)", ""),  #
    ("(-)", ""),  #
    ("(???)", ""),  #
    ("(??)", ""),  #
    ("(?Sw.)", ""),  #
    ("(..?)", ""),  #
    ("(...i)", ""),  #
    ("(+human)", ""),  #
    ("(= bundle)", ""),  #
    ("(= pombe)", ""),  #
    ("(=?)", ""),  #
    ("(=akula)", ""),  #
    ("(=aneko)", ""),  #
    ("(=be blown by the wind)", ""),  #
    ("(=cloth)", ""),  #
    ("(=collect)", ""),  #
    ("(=in?)", ""),  #
    ("(=kimeoza)", ""),  #
    ("(=kuliya)", ""),  #
    ("(143)", ""),  #
    ("(1a moto)", ""),  #
    ("(7)", ""),  #
    ("(9-10 mbisi)", ""),  #
    ("(a drink)", ""),  #
    ("(a guest)", ""),  #
    ("(a kind of snake)", ""),  #
    ("(abakori pl.)", ""),  #
    ("(action)", ""),  #
    ("(akEEma pl.)", ""),  #
    ("(always in plural)", ""),  #
    ("(always plural)", ""),  #
    ("(amakara pl.)", ""),  #
    ("(amareko pl.)", ""),  #
    ("(amatu pl.)", ""),  #
    ("(amavega pl.)", ""),  #
    ("(and kilema)", ""),  #
    ("(any alc.drink)", ""),  #
    ("(any other)", ""),  #
    ("(army)", ""),  #
    ("(arrow)", ""),  #
    ("(as a weapon)", ""),  #
    ("(as in : kumbwa)", ""),  #
    ("(as selling)", ""),  #
    ("(baby)", ""),  #
    ("(back hip)", ""),  #
    ("(banana wine)", ""),  #
    ("(bananas)", ""),  #
    ("(bask)", ""),  #
    ("(be hot)", ""),  #
    ("(be ill)", ""),  #
    ("(be sterile)", ""),  #
    ("(become weak)", ""),  #
    ("(beer)", ""),  #
    ("(beings)", ""),  #
    ("(bh? gh?)", ""),  #
    ("(blind)", ""),  #
    ("(both edged)", ""),  #
    ("(both)", ""),  #
    ("(br.)", ""),  #
    ("(breast milk)", ""),  #
    ("(breathe)", ""),  #
    ("(brother)", ""),  #
    ("(bury:clothe)", ""),  #
    ("(but in pairs)", ""),  #
    ("(but see vatangala)", ""),  #
    ("(cage)", ""),  #
    ("(calf)", ""),  #
    ("(can also mean to find-tafuta)", ""),  #
    ("(canoe)", ""),  #
    ("(carrier)", ""),  #
    ("(castrated bull)", ""),  #
    ("(chief)", ""),  #
    ("(child)", ""),  #
    ("(childish)", ""),  #
    ("(childran)", ""),  #
    ("(chongi sg.)", ""),  #
    ("(cl.1)", ""),  #
    ("(cl.9)", ""),  #
    ("(clan)", ""),  #
    ("(class 1)", ""),  #
    ("(climb:scrape)", ""),  #
    ("(close eyes)", ""),  #
    ("(close mouth)", ""),  #
    ("(cloth)", ""),  #
    ("(clothes)", ""),  #
    ("(coinage)", ""),  #
    ("(collect)", ""),  #
    ("(conn.to -sha?)", ""),  #
    ("(connected with sinning)", ""),  #
    ("(current use)", ""),  #
    ("(daylight)", ""),  #
    ("(depends on noun)", ""),  #
    ("(dirt)", ""),  #
    ("(dry grass)", ""),  #
    ("(dry skin -animal)", ""),  #
    ("(e?)", ""),  #
    ("(e.g.chief)", ""),  #
    ("(ebhigero pl.)", ""),  #
    ("(eg. bananas)", ""),  #
    ("(eg. beads)", ""),  #
    ("(eg. for hair)", ""),  #
    ("(eg.house)", ""),  #
    ("(eg.knife)", ""),  #
    ("(eg.rain)", ""),  #
    ("(eg.stick)", ""),  #
    ("(ekitoke sing.)", ""),  #
    ("(emikiria pl.)", ""),  #
    ("(esafari ?!)", ""),  #
    ("(esp. of wife)", ""),  #
    ("(ezitetere.pl.)", ""),  #
    ("(fear God)", ""),  #
    ("(fem.)", ""),  #
    ("(fem)", ""),  #
    ("(fetch)", ""),  #
    ("(fierce)", ""),  #
    ("(fina for things)", ""),  #
    ("(five and three)", ""),  #
    ("(flock)", ""),  #
    ("(flutter)", ""),  #
    ("(fly)", ""),  #
    ("(follow in order)", ""),  #
    ("(food)", ""),  #
    ("(foot)", ""),  #
    ("(for a boy)", ""),  #
    ("(for a cow)", ""),  #
    ("(for animals)", ""),  #
    ("(for any girl)", ""),  #
    ("(for any metal)", ""),  #
    ("(for anything unfeminine )", ""),  #
    ("(for axe)", ""),  #
    ("(for beer)", ""),  #
    ("(for creatures)", ""),  #
    ("(for fire)", ""),  #
    ("(for fruit)", ""),  #
    ("(for girl)", ""),  #
    ("(for heaven)", ""),  #
    ("(for hoe)", ""),  #
    ("(for human)", ""),  #
    ("(for iron ore)", ""),  #
    ("(for kitchen)", ""),  #
    ("(for large animals)", ""),  #
    ("(for men)", ""),  #
    ("(for mother's milk)", ""),  #
    ("(for mtu)", ""),  #
    ("(for ndizi)", ""),  #
    ("(for non-domestic animals)", ""),  #
    ("(for person-mbaha)", ""),  #
    ("(for specific inguiry)", ""),  #
    ("(for the old)", ""),  #
    ("(for thirsty)", ""),  #
    ("(for tunda)", ""),  #
    ("(for up)", ""),  #
    ("(for visitors)", ""),  #
    ("(for watu)", ""),  #
    ("(for women)", ""),  #
    ("(forehead)", ""),  #
    ("(forest)", ""),  #
    ("(fruit)", ""),  #
    ("(fruits)", ""),  #
    ("(general term)", ""),  #
    ("(general word)", ""),  #
    ("(good person)", ""),  #
    ("(guest)", ""),  #
    ("(h?)", ""),  #
    ("(h=k ?)", ""),  #
    ("(harvest)", ""),  #
    ("(hearth)", ""),  #
    ("(her)", ""),  #
    ("(herself)", ""),  #
    ("(his)", ""),  #
    ("(hook)", ""),  #
    ("(horizon)", ""),  #
    ("(house roof)", ""),  #
    ("(hut)", ""),  #
    ("(if a saucepan)", ""),  #
    ("(if it's meat)", ""),  #
    ("(if of maize)", ""),  #
    ("(if on electric chair)", ""),  #
    ("(in a river)", ""),  #
    ("(in ancient stories = aeroplane)", ""),  #
    ("(in case of disease-kutamba)", ""),  #
    ("(in nyonga)", ""),  #
    ("(in plural)", ""),  #
    ("(in polite language)", ""),  #
    ("(in water)", ""),  #
    ("(intr. v)", ""),  #
    ("(iron tools)", ""),  #
    ("(it never stands alone)", ""),  #
    ("(itch)", ""),  #
    ("(ivory)", ""),  #
    ("(jaw(=kireju)", ""),  #
    ("(jesus)", ""),  #
    ("(kanda-adopted now)", ""),  #
    ("(kubamba [for fish])", ""),  #
    ("(kufin..?)", ""),  #
    ("(kugwaala - to be)", ""),  #
    ("(kungo?-season)", ""),  #
    ("(kupumula ?)", ""),  #
    ("(kuura-house)", ""),  #
    ("(kwejuna -polite)", ""),  #
    ("(latent fire usually under ashes=orumota)", ""),  #
    ("(leaf)", ""),  #
    ("(lean)", ""),  #
    ("(leave(off)", ""),  #
    ("(leg and foot)", ""),  #
    ("(leg)", ""),  #
    ("(let off)", ""),  #
    ("(lift spell)", ""),  #
    ("(long)", ""),  #
    ("(look for)", ""),  #
    ("(mahuti?)", ""),  #
    ("(maize &beans)", ""),  #
    ("(maize)", ""),  #
    ("(male of animals)", ""),  #
    ("(man)", ""),  #
    ("(many)", ""),  #
    ("(maongi pl.)", ""),  #
    ("(masc. and fem.?)", ""),  #
    ("(masc)", ""),  #
    ("(maselege:pl.)", ""),  #
    ("(mayoyolo pl.)", ""),  #
    ("(meaning same as ku-pumzika)", ""),  #
    ("(means across the other side of)", ""),  #
    ("(meno pl.)", ""),  #
    ("(modern usage)", ""),  #
    ("(mole hill)", ""),  #
    ("(money)", ""),  #
    ("(mother in law)", ""),  #
    ("(mwitha(while being milked)", ""),  #
    ("(my brother in law)", ""),  #
    ("(my father in law)", ""),  #
    ("(my)", ""),  #
    ("(myself)", ""),  #
    ("(name of )", ""),  #
    ("(ngooya +)", ""),  #
    ("(njwili pl.)", ""),  #
    ("(no cattle)", ""),  #
    ("(no difference)", ""),  #
    ("(no pl.)", ""),  #
    ("(no plural)", ""),  #
    ("(no tomato)", ""),  #
    ("(not sure)", ""),  #
    ("(not=-shunda)", ""),  #
    ("(noun & verb)", ""),  #
    ("(noun- lihako)", ""),  #
    ("(noun:umudiido)", ""),  #
    ("(nyuka or -nyukuta)", ""),  #
    ("(nyumbu pl.)", ""),  #
    ("(o.s.)", ""),  #
    ("(o.s.agsinst)", ""),  #
    ("(obhotara?)", ""),  #
    ("(objects)", ""),  #
    ("(of 602)", ""),  #
    ("(of a trap)", ""),  #
    ("(of a tree)", ""),  #
    ("(of animals)", ""),  #
    ("(of birds)", ""),  #
    ("(of butter)", ""),  #
    ("(of child?)", ""),  #
    ("(of dead animal-orwamba)", ""),  #
    ("(of maize)", ""),  #
    ("(of mountain)", ""),  #
    ("(of parents)", ""),  #
    ("(of poles)", ""),  #
    ("(of soil)", ""),  #
    ("(of solutions)", ""),  #
    ("(of tobacco)", ""),  #
    ("(of tree)", ""),  #
    ("(old domestic animal past bearing)", ""),  #
    ("(old Haya-Butani)", ""),  #
    ("(old Haya-kuteeka)", ""),  #
    ("(old man)", ""),  #
    ("(old)", ""),  #
    ("(older than father)", ""),  #
    ("(omoghaka(old man)", ""),  #
    ("(omukama?)", ""),  #
    ("(omumwi-jua?)", ""),  #
    ("(on bed)", ""),  #
    ("(on its own)", ""),  #
    ("(on the back)", ""),  #
    ("(on the body)", ""),  #
    ("(on the head)", ""),  #
    ("(one)", ""),  #
    ("(only with the tongue)", ""),  #
    ("(opl.amabara)", ""),  #
    ("(opposite sex)", ""),  #
    ("(or akanwa-mouth cavity)", ""),  #
    ("(or ifwagilo)", ""),  #
    ("(or inzoka gwiba)", ""),  #
    ("(or kunoga)", ""),  #
    ("(or kuUnda)", ""),  #
    ("(or makuju)", ""),  #
    ("(or masiine)", ""),  #
    ("(or munjoro)", ""),  #
    ("(or nshaasha)", ""),  #
    ("(or ulukwe ulufupi)", ""),  #
    ("(order)", ""),  #
    ("(ordinary milk)", ""),  #
    ("(original)", ""),  #
    ("(oroheke sing.)", ""),  #
    ("(p?)", ""),  #
    ("(pass.)", ""),  #
    ("(pass)", ""),  #
    ("(people's)", ""),  #
    ("(pick up)", ""),  #
    ("(pl sengonge)", ""),  #
    ("(pl?)", ""),  #
    ("(Pl. amola)", ""),  #
    ("(Pl. matunda)", ""),  #
    ("(Pl. milongo)", ""),  #
    ("(plant)", ""),  #
    ("(playground)", ""),  #
    ("(polishing ma..)", ""),  #
    ("(preceded by qualifying noun)", ""),  #
    ("(pronounced nkhuni)", ""),  #
    ("(pronounciation)", ""),  #
    ("(pull out fishnets)", ""),  #
    ("(r? s?)", ""),  #
    ("(reflexive)", ""),  #
    ("(rely on)", ""),  #
    ("(repairing implement)", ""),  #
    ("(rera(tall)", ""),  #
    ("(respected)", ""),  #
    ("(row)", ""),  #
    ("(s +pl.)", ""),  #
    ("(s?)", ""),  #
    ("(s. +pl.)", ""),  #
    ("(s.eikala)", ""),  #
    ("(s.nene)", ""),  #
    ("(same sex)", ""),  #
    ("(sg & pl)", ""),  #
    ("(sg. chobo)", ""),  #
    ("(sg. iyoyo)", ""),  #
    ("(sg. linyahi)", ""),  #
    ("(sg. lUlezu)", ""),  #
    ("(sg. ukogoto)", ""),  #
    ("(sg.)", ""),  #
    ("(sharp)", ""),  #
    ("(shoulder)", ""),  #
    ("(si.)", ""),  #
    ("(si)", ""),  #
    ("(sib-in-law)", ""),  #
    ("(sick man)", ""),  #
    ("(sick)", ""),  #
    ("(side of the face)", ""),  #
    ("(sing & pl)", ""),  #
    ("(sing.ichyatsi)", ""),  #
    ("(sing.itako)", ""),  #
    ("(sing.lidako)", ""),  #
    ("(sing.likala)", ""),  #
    ("(sing)", ""),  #
    ("(single edged)", ""),  #
    ("(sis.)", ""),  #
    ("(sister-in-law of woman)", ""),  #
    ("(skin)", ""),  #
    ("(slug)", ""),  #
    ("(small ant sp.)", ""),  #
    ("(small finger)", ""),  #
    ("(small goat)", ""),  #
    ("(small stick)", ""),  #
    ("(small)", ""),  #
    ("(somebody)", ""),  #
    ("(something)", ""),  #
    ("(sow)", ""),  #
    ("(spirit of the dead)", ""),  #
    ("(stand up)", ""),  #
    ("(stative?)", ""),  #
    ("(sticks on surface)", ""),  #
    ("(stool)", ""),  #
    ("(stranger)", ""),  #
    ("(surpass)", ""),  #
    ("(Sw.?)", ""),  #
    ("(sw.)", ""),  #
    ("(Sw.)", ""),  #
    ("(sw.choka)", ""),  #
    ("(sw.chura)", ""),  #
    ("(sw.etu)", ""),  #
    ("(sw.kaanga)", ""),  #
    ("(sw.kichaka)", ""),  #
    ("(sw.kijiji)", ""),  #
    ("(sw.kilima)", ""),  #
    ("(sw.kuchakura)", ""),  #
    ("(sw.kuigawanya)", ""),  #
    ("(sw.kuimba)", ""),  #
    ("(sw.kuruka)", ""),  #
    ("(sw.kuteta)", ""),  #
    ("(sw.kuumba)", ""),  #
    ("(sw.maini)", ""),  #
    ("(sw.mzinga)", ""),  #
    ("(sw.nguo)", ""),  #
    ("(sw.tende)", ""),  #
    ("(sw.tundu)", ""),  #
    ("(sw.ubongo)", ""),  #
    ("(sw.ulozi)", ""),  #
    ("(sw.yenu)", ""),  #
    ("(swa)", ""),  #
    ("(sweat)", ""),  #
    ("(synonym)", ""),  #
    ("(take off(clothes)", ""),  #
    ("(teach)", ""),  #
    ("(the dance)", ""),  #
    ("(the other morrow)", ""),  #
    ("(things)", ""),  #
    ("(to be)", ""),  #
    ("(to boys)", ""),  #
    ("(to catch)", ""),  #
    ("(to close the eyes)", ""),  #
    ("(to fold)", ""),  #
    ("(to get permission)", ""),  #
    ("(to girls)", ""),  #
    ("(to judge)", ""),  #
    ("(to lie face downwards)", ""),  #
    ("(to look after cattle)", ""),  #
    ("(to make round)", ""),  #
    ("(to milk)", ""),  #
    ("(tree)", ""),  #
    ("(type of ng'au)", ""),  #
    ("(uncircumcized)", ""),  #
    ("(uncommon in my place)", ""),  #
    ("(uncooked)", ""),  #
    ("(unknown in my area)", ""),  #
    ("(urine)", ""),  #
    ("(use grass)", ""),  #
    ("(use hands)", ""),  #
    ("(use legs)", ""),  #
    ("(used for path)", ""),  #
    ("(using a hook)", ""),  #
    ("(V-length?)", ""),  #
    ("(v. kona)", ""),  #
    ("(various kinds)", ""),  #
    ("(vb.kuguma)", ""),  #
    ("(vb)", ""),  #
    ("(verb?)", ""),  #
    ("(verb)", ""),  #
    ("(wamweto -no fem. or masc.)", ""),  #
    ("(where women sleep)", ""),  #
    ("(white)", ""),  #
    ("(whitewash)", ""),  #
    ("(wide-mouth)", ""),  #
    ("(wild flower)", ""),  #
    ("(wild)", ""),  #
    ("(with earth)", ""),  #
    ("(without foreskin)", ""),  #
    ("(wooden ?)", ""),  #
    ("(wooden)", ""),  #
    ("(workers)", ""),  #
    ("(worn on the feet)", ""),  #
    ("(worn out)", ""),  #
    ("(younger)", ""),  #
    ("(your father)", ""),  #
    ("(your)", ""),  #
    ("(yours)", ""),  #
    ("(ziba call it katenyanja)", ""),  #
    ("(ziba ekitenge)", ""),  #
    ("(ziba nshanje)", ""),  #
    ("[at cock-crow]", ""),  # bracket info
    ("[bring]", ""),  # bracket info
    ("[close eyes]", ""),  # bracket info
    ("[eceka:le]", ""),  # bracket info
    ("[eceno*:nu]", ""),  # bracket info
    ("[fetch]", ""),  # bracket info
    ("[kolamba iko*:fi]", ""),  # bracket info
    ("[kote*:fja]", ""),  # bracket info
    ("[o:nde*:zi]", ""),  # bracket info
    ("[of tree]", ""),  # bracket info
    ("[olosi:ko]", ""),  # bracket info
    ("[omwe*:ne*]", ""),  # bracket info
    ("[oocelo:me*:]", ""),  # bracket info
    ("[oov*e:nu]", ""),  # bracket info
    ("[owa:ja]", ""),  # bracket info
    ("[Sw. njoo]", ""),  # bracket info
]


@attr.s
class CustomConcept(pylexibank.Concept):
    Swahili_Gloss = attr.ib(default=None)
    NUMBER = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "tls"
    concept_class = CustomConcept
    form_spec = pylexibank.FormSpec(
        brackets={},
        separators=",;/",
        missing_data=("-", "?", "???", "+"),
        replacements=REPLACEMENTS,
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

            if entry["SRCID"].endswith(".0"):
                src_idx = entry["SRCID"].strip(".0")
            elif entry["SRCID"].endswith(".5"):
                src_idx = entry["SRCID"].replace(".5", "a")
            else:
                src_idx = entry["SRCID"]

            # Fix values if possible (for common problems not in lexemes.csv)
            value = entry["REFLEX"]

            # Delete all brackets
            value = re.sub(r"\[[^]]*\]", "", value)

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

            # Remove the many final question marks
            value = re.sub(r"\?$", "", value)

            if src_idx not in concepts:
                continue

            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["LGABBR"]],
                Parameter_ID=concepts[src_idx],
                Value=value,
                Source=["Nurse1975", "Nurse1979", "Nurse1980", "TLS1999"],
            )
