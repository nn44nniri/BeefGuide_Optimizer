This update makes breed genotype values in settings.json explicit by pairing each used value with a named parameter.

What changed
- sex_libraries.male and sex_libraries.female in settings.json are now written as named parameter objects instead of anonymous numeric arrays.
- LiGAPSBeef_herd.py was updated to accept both forms:
  1) named parameter objects (new preferred format)
  2) legacy 26/27-value arrays (backward compatibility)
- The code internally reconstructs the original LIBRARY order, so simulator behavior is preserved.

Why this was done
- The original arrays relied on position only.
- The updated format makes each value self-describing and easier to edit safely.
- Parameter names were chosen from the existing code comments and the LiGAPS-Beef supplementary Table S2 terminology.

Behavior
- No mechanistic formulas were changed.
- No existing comments in the library were removed.
- Legacy settings remain supported.


`case_ids = [1, 3, 5, 7, 9, 10]` means the current script is configured to run only the **France illustration cases** out of the full 10 benchmark scenarios, instead of all cases 1–10. 

Here is a compact summary of the 10 illustration scenarios used in LiGAPS-Beef, combining the paper’s case descriptions with the code’s genotype, location, housing, and diet mappings.  

| Case | Abbrev.                         | Production level         | Breed                   | Country   | Housing                         | Diet / feeding setup                                                     | Notes                                                                                                               |
| ---- | ------------------------------- | ------------------------ | ----------------------- | --------- | ------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| 1    | Pot Ch Fr                       | Potential                | Charolais               | France    | Stable Dec–Mar, grazing Apr–Nov | 65% wheat + 35% good hay, ad libitum                                     | Herd-level benchmark case in France.                                                                                |
| 2    | Pot Ch Au                       | Potential                | Charolais               | Australia | Grazing year-round              | 65% wheat + 35% hay, ad libitum                                          | Animal-level case exists; herd-level no result because reproductive Charolais cows could not cope with heat stress. |
| 3    | Pot B×S Fr                      | Potential                | ¾ Brahman × ¼ Shorthorn | France    | Stable Dec–Mar, grazing Apr–Nov | 65% wheat + 35% good hay, ad libitum                                     | France potential case for the heat-adapted crossbreed.                                                              |
| 4    | Pot B×S Au                      | Potential                | ¾ Brahman × ¼ Shorthorn | Australia | Grazing year-round              | 65% wheat + 35% hay, ad libitum                                          | Australia potential case for the crossbreed.                                                                        |
| 5    | FQlty Ch Fr                     | Feed-quality limited     | Charolais               | France    | Stable Dec–Mar, grazing Apr–Nov | 5% barley + 95% grass when grazing / hay when housed                     | Grass-based/hay-based diet with small barley share.                                                                 |
| 6    | FQlty Ch Au                     | Feed-quality limited     | Charolais               | Australia | Grazing year-round              | 5% barley + 95% grass                                                    | Animal-level case exists; herd-level no result because reproductive Charolais cows failed under heat stress.        |
| 7    | FQlty B×S Fr                    | Feed-quality limited     | ¾ Brahman × ¼ Shorthorn | France    | Stable Dec–Mar, grazing Apr–Nov | 5% barley + 95% grass when grazing / hay when housed                     | France feed-quality-limited crossbreed case.                                                                        |
| 8    | FQlty B×S Au                    | Feed-quality limited     | ¾ Brahman × ¼ Shorthorn | Australia | Grazing year-round              | 5% barley + 95% grass                                                    | Australia feed-quality-limited crossbreed case.                                                                     |
| 9    | FQlty Ch Fr (1 kg barley)       | Feed-quality limited     | Charolais               | France    | Stable Dec–Mar, grazing Apr–Nov | Fixed 1 kg DM barley/day, rest grass when grazing or hay when housed     | This case raised the reproductive cow’s share of herd feed to 84%.                                                  |
| 10   | Feed-limited Ch Fr (max 2% TBW) | Feed-limited by quantity | Charolais               | France    | Stable Dec–Mar, grazing Apr–Nov | 5% barley + 95% grass/hay, but capped at max 2% of total body weight/day | Designed to show quantity limitation and energy deficiency effects.                                                 |

A useful way to read the 10 cases is:
cases **1–4** = potential production, cases **5–9** = feed-quality-limited production, and case **10** = feed-quantity-limited production; the two genotypes are Charolais and ¾ Brahman × ¼ Shorthorn, tested across France and Australia.
