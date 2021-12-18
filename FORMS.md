## Specification of form manipulation


Specification of the value-to-form processing in Lexibank datasets:

The value-to-form processing is divided into two steps, implemented as methods:
- `FormSpec.split`: Splits a string into individual form chunks.
- `FormSpec.clean`: Normalizes a form chunk.

These methods use the attributes of a `FormSpec` instance to configure their behaviour.

- `brackets`: `{'(': ')', '[': ']'}`
  Pairs of strings that should be recognized as brackets, specified as `dict` mapping opening string to closing string
- `separators`: `,;/`
  Iterable of single character tokens that should be recognized as word separator
- `missing_data`: `('-', '?', '???', '+', '_', '--_', '!')`
  Iterable of strings that are used to mark missing data
- `strip_inside_brackets`: `True`
  Flag signaling whether to strip content in brackets (**and** strip leading and trailing whitespace)
- `replacements`: `[('(kU)d\x97s\x87 ? +', ''), ('\x88', ''), ('\x87', ''), ('\x97', ''), (' ', '_'), ('#__#_pencil_only_#', ''), ('"', ''), ('kuwuka_kimus#', 'kuwaka_kimus'), ('__#_note_2nd_hand_here', ''), ('never_stands_alone', '-'), ('depends_on_what_is_sacrificed', '-'), ('kunuka_akisa_|_bukomu', 'kunuka_akisa'), ('kufwila_|_kutema_matye', 'kufwila'), ('ekyora__pl.____also_eghekere', 'ekyora'), ('see__412', '-'), ('e.g.construct_a_boat', '-'), ('see_935', '-'), ('ku_see_#528', 'ku'), ('397', '-'), ('clans', '-'), ('right_person', '-'), ('shitere_shi_shilenj..', 'shitere'), ('#', '')]`
  List of pairs (`source`, `target`) used to replace occurrences of `source` in formswith `target` (before stripping content in brackets)
- `first_form_only`: `True`
  Flag signaling whether at most one form should be returned from `split` - effectively ignoring any spelling variants, etc.
- `normalize_whitespace`: `True`
  Flag signaling whether to normalize whitespace - stripping leading and trailing whitespace and collapsing multi-character whitespace to single spaces
- `normalize_unicode`: `None`
  UNICODE normalization form to use for input of `split` (`None`, 'NFD' or 'NFC')

### Replacement of invalid lexemes

Source lexemes may be impossible to interpret correctly. 2034 such lexemes are listed
in [`etc/lexemes.csv`](etc/lexemes.csv) and replaced as specified in this file.
