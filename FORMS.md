## Specification of form manipulation


Specification of the value-to-form processing in Lexibank datasets:

The value-to-form processing is divided into two steps, implemented as methods:
- `FormSpec.split`: Splits a string into individual form chunks.
- `FormSpec.clean`: Normalizes a form chunk.

These methods use the attributes of a `FormSpec` instance to configure their behaviour.

- `brackets`: `{}`
  Pairs of strings that should be recognized as brackets, specified as `dict` mapping opening string to closing string
- `separators`: `,;/`
  Iterable of single character tokens that should be recognized as word separator
- `missing_data`: `('-',)`
  Iterable of strings that are used to mark missing data
- `strip_inside_brackets`: `True`
  Flag signaling whether to strip content in brackets (**and** strip leading and trailing whitespace)
- `replacements`: `[('(general)', ''), ('[general]', ''), ('(modern)', ''), ('(see below)', ''), ('(uncommon)', ''), (' ? ', ' '), ('(?)', ''), ('(!)', ''), ('(?!)', ''), ('(noun)', ''), ('(object)', ''), ('(pl)', ''), ('(s.)', ''), ('(s.+pl.)', ''), ('(sg)', ''), ('[+ poss.]', ''), ('[gen.]', ''), ('(sing.)', ''), ('(sing.oromambo)', ''), ('(adopted)', ''), ('(eng.)', ''), ('(swahili)', ''), ('(a?)', 'a'), ('(a)', 'a'), ('(y)', 'y'), ('(cha)', 'cha'), ('(e)', 'e'), ('(g)', 'g'), ('(gU)', 'gU'), ('(gu)', 'gu'), ('(h)', 'h'), ('(i)', 'i'), ('(k)', 'k'), ('(khu)', 'khu'), ('(ki)', 'ki'), ('(ko)', 'ko'), ('(ku)', 'ku'), ('(kU)', 'kU'), ('(kw)', 'kw'), ('(kwa)', 'kwa'), ('(kwe)', 'kwe'), ('(kwi)', 'kwi'), ('(l)', 'l'), ('(li)', 'li'), ('(ma-)', 'ma-'), ('(ma)', 'ma'), ('(mu)', 'mu'), ('(n)', 'n'), ('(na)', 'na'), ('(o)', 'o'), ('(oko)', 'oko'), ('(oku)', 'oku'), ('(okw)', 'okw'), ('(s)', 's'), ('(t)', 't'), ('(u)', 'u'), ('(uku)', 'uku'), ('(ukw)', 'ukw'), ('(w)', 'w'), ('(wa)', 'wa'), ('(ya)', 'ya'), ('(zi)', 'zi'), ('(verb of carrying the things and piling them)', ''), ('[b-i-l]', ''), ('[s-i-l]', ''), ('(animal)', ''), ('(animals)', ''), ('(banana tree)', ''), ('(belly)', ''), ('(big iron)', ''), ('(birds)', ''), ('(borrow)', ''), ('(boy)', ''), ('(boys)', ''), ('(brother in law)', ''), ('(cattle)', ''), ('(chin,jaw)', ''), ('(crust)', ''), ('(dying animals)', ''), ('(eyes)', ''), ('(father in law)', ''), ('(female)', ''), ('(for a person)', ''), ('(girl)', ''), ('(girls)', ''), ('(grandpa)', ''), ('(grass)', ''), ('(green)', ''), ('(groan)', ''), ('(grow up,ripen)', ''), ('(heat)', ''), ('[male]', ''), ('[female]', ''), ('(human)', ''), ('(hyena)', ''), ('(lend)', ''), ('(lion)', ''), ('(listen)', ''), ('(male)', ''), ('(mother)', ''), ('(mouth)', ''), ('(nest)', ''), ('(of church)', ''), ('(of house)', ''), ('(people)', ''), ('(-human)', ''), ('(person)', ''), ('(seed,grain)', ''), ('(sick person)', ''), ('(a sick person)', ''), ('(sister in law)', ''), ('(sister)', ''), ('(skin bark)', ''), ('(smoking)', ''), ('(snail)', ''), ('(arm)', ''), ('(hands)', ''), ('(hand)', ''), ('(-idi in counting)', ''), ('(biki=piece of wood)', ''), ('(unexpectedly)', ''), ('(spoil,destroy)', ''), ('(thick forest)', ''), ('(thick foest)', ''), ('(thing)', ''), ('(unripe)', ''), ('(woman)', '')]`
  List of pairs (`source`, `target`) used to replace occurrences of `source` in formswith `target` (before stripping content in brackets)
- `first_form_only`: `False`
  Flag signaling whether at most one form should be returned from `split` - effectively ignoring any spelling variants, etc.
- `normalize_whitespace`: `True`
  Flag signaling whether to normalize whitespace - stripping leading and trailing whitespace and collapsing multi-character whitespace to single spaces
- `normalize_unicode`: `None`
  UNICODE normalization form to use for input of `split` (`None`, 'NFD' or 'NFC')

### Replacement of invalid lexemes

Source lexemes may be impossible to interpret correctly. 579 such lexemes are listed
in [`etc/lexemes.csv`](etc/lexemes.csv) and replaced as specified in this file.
