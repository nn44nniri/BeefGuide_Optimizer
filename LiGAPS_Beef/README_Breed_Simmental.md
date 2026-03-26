ْQuestion: By searching articles published in official journals, search for the data, variables and values ​​required for this simulator for the Simmental cattle breed that are required in settings.json to define this breed in it and write it in a table with the reference by mentioning the reference. Finally, write the sections related to this breed in settings.json and write the reference as a comment in front of it.

Your current `settings.json` expects each breed to be defined under `breed Simmental` with `sex_libraries.male` and `sex_libraries.female`, and each sex library is an ordered vector of 27 numbers. 

The important limitation is that **not every one of those 27 slots has a directly published Simmental value in journal form**. LiGAPS-Beef itself uses a mix of measured values, fitted Gompertz/lactation parameters, assumptions, and even guesstimates for some breed-related slots; the supplement explicitly notes that some mature-body-weight and carcass-related items are hard to estimate or are guesstimates. So the most honest way to define Simmental is a **hybrid block**: use journal-backed Simmental values where available, and fill the remaining slots with the nearest LiGAPS Bos taurus defaults until you calibrate them with Simmental data.

## Recommended Simmental values for the 27-slot breed library

| #  | Variable in your settings comments         |   Male |  Female | Basis   |
| -- | ------------------------------------------ | -----: | ------: | ------- |
| 1  | reflectance_coat                           |   0.60 |    0.60 | L1      |
| 2  | coat_length_m                              |  0.012 |   0.012 | L1      |
| 3  | body_area_factor                           |   1.00 |    1.00 | L1      |
| 4  | core_skin_conductance_max_W_m2_K           |   64.1 |    64.1 | L1      |
| 5  | start_body_weight_kg                       |   39.8 |    36.8 | J1      |
| 6  | gompertz_max_adult_weight_kg               |  911.7 |   664.6 | I1      |
| 7  | birth_weight_kg                            |   39.8 |    36.8 | J1      |
| 8  | gompertz_c_parameter                       |    1.6 |     1.6 | L1      |
| 9  | gompertz_d_parameter                       |    1.1 |     1.1 | L1      |
| 10 | gompertz_e_parameter                       |  177.0 |   129.0 | I2      |
| 11 | lactation_curve_parameter_1                |    0.0 | 15.2317 | J2 / L2 |
| 12 | lactation_curve_parameter_2                | 0.1029 |  0.1029 | J2      |
| 13 | maximum_adult_weight_reference_kg          |  734.0 |   535.5 | I1 / J3 |
| 14 | sex_flag_0_male_1_female                   |      0 |       1 | Schema  |
| 15 | reproductive_energy_or_gestation_parameter |    8.0 |     8.0 | L1      |
| 16 | fattening_or_lactation_rate_parameter      |  0.068 |   0.068 | L1      |
| 17 | lower_weight_fraction_for_maintenance      |   0.55 |    0.55 | L1      |
| 18 | net_energy_maintenance_multiplier          |   1.00 |    1.00 | L1      |
| 19 | minimum_body_reserve_threshold             |   0.32 |    0.32 | L1      |
| 20 | bone_lipid_equation_parameter              |   11.6 |    11.8 | L1      |
| 21 | carcass_fraction                           |  0.584 |   0.560 | J4 / I3 |
| 22 | carcass_fat_polynomial_parameter           |   4.10 |    4.10 | L1      |
| 23 | minimum_core_skin_conductance_factor       |   1.00 |    1.00 | L1      |
| 24 | hide_or_coat_parameter_a                   |   3.08 |    3.08 | L1      |
| 25 | hide_or_coat_parameter_b                   |   1.73 |    1.73 | L1      |
| 26 | hide_or_coat_reference_temperature_c       |   35.3 |    35.3 | L1      |
| 27 | lactation_curve_parameter_3_or_legacy_fill | 0.0015 |  0.0015 | J2      |

### What the source labels mean

J1 = peer-reviewed Simmental birth weights: 39.8 kg for males and 36.8 kg for females. ([Canadian Science Publishing][1])
J2 = peer-reviewed Wood-lactation parameters for dairy Simmental cows up to 305 days: a = 15.2317, b = 0.1029, c = 0.0015. ([PMC][2])
J3 = peer-reviewed South African Simmental mature-cow proxy: cow weight at calf weaning averaged 535.5 kg; cow weight at calving averaged 543.3 kg. I used **535.5 kg** as the female mature-weight reference because the paper says weight at weaning is the more practical mature-cow measure. ([SciELO][3])
J4 = peer-reviewed Simmental hot dressing percentage for young bulls: 58.4%, used here as the male carcass-fraction anchor. ([ResearchGate][4])
L1 = carried over from LiGAPS’ existing **Bos taurus / light-coat default pattern** because I did not find a one-to-one Simmental journal estimate for that exact slot in the LiGAPS parameterization. This is the safest no-surprise starting point.  
L2 = male lactation slot set to zero because males do not lactate; this follows the same pattern already used in your existing settings for Charolais and Boran males. 
I1 = inferred from J3 plus the sex scaling already embedded in LiGAPS Bos taurus breeds: male reference weight ≈ female reference × 1.37; Gompertz adult weight ≈ reference × 1.241. This is a modeler inference, not a directly published Simmental measurement.  ([SciELO][3])
I2 = inferred from the same LiGAPS Bos taurus ratio pattern used between slot 10 and slot 13 in the built-in breeds. 
I3 = female carcass fraction set slightly below the male value because the LiGAPS supplement notes that males are assumed to have higher carcass percentages than females. 

## `settings.json` section for Simmental

Use this as a **provisional Simmental block**. It is executable in the same structure as your current settings file, but some comments deliberately say “provisional” where the value is inherited or inferred rather than directly reported for Simmental.

```json
{
  // Simmental (provisional LiGAPS block: journal-backed where available, LiGAPS defaults elsewhere)
  "id": 6,
  "name": "Simmental",
  "sex_libraries": {
    "male": [
      0.60,   // 1 reflectance_coat — [L1] LiGAPS Bos taurus light-coat default
      0.012,  // 2 coat_length_m — [L1] LiGAPS default
      1.00,   // 3 body_area_factor — [L1] LiGAPS Bos taurus default
      64.1,   // 4 core_skin_conductance_max_W_m2_K — [L1] LiGAPS default
      39.8,   // 5 start_body_weight_kg — [J1] Simmental male calf birth weight
      911.7,  // 6 gompertz_max_adult_weight_kg — [I1] inferred from Simmental female mature weight + LiGAPS Bos taurus scaling
      39.8,   // 7 birth_weight_kg — [J1] Simmental male calf birth weight
      1.6,    // 8 gompertz_c_parameter — [L1] provisional LiGAPS Bos taurus default
      1.1,    // 9 gompertz_d_parameter — [L1] provisional LiGAPS Bos taurus default
      177.0,  // 10 gompertz_e_parameter — [I2] inferred from LiGAPS Bos taurus slot pattern
      0.0,    // 11 lactation_curve_parameter_1 — [L2] males do not lactate
      0.1029, // 12 lactation_curve_parameter_2 — [J2] kept aligned with Simmental Wood curve block
      734.0,  // 13 maximum_adult_weight_reference_kg — [I1] inferred male reference weight
      0,      // 14 sex_flag_0_male_1_female
      8.0,    // 15 reproductive_energy_or_gestation_parameter — [L1] provisional LiGAPS default
      0.068,  // 16 fattening_or_lactation_rate_parameter — [L1] provisional LiGAPS default
      0.55,   // 17 lower_weight_fraction_for_maintenance — [L1] provisional LiGAPS Bos taurus default
      1.00,   // 18 net_energy_maintenance_multiplier — [L1] Bos taurus default
      0.32,   // 19 minimum_body_reserve_threshold — [L1] provisional default
      11.6,   // 20 bone_lipid_equation_parameter — [L1] provisional default
      0.584,  // 21 carcass_fraction — [J4] Simmental young-bull hot dressing percentage
      4.10,   // 22 carcass_fat_polynomial_parameter — [L1] provisional default
      1.00,   // 23 minimum_core_skin_conductance_factor — [L1] Bos taurus default
      3.08,   // 24 hide_or_coat_parameter_a — [L1] LiGAPS default
      1.73,   // 25 hide_or_coat_parameter_b — [L1] LiGAPS default
      35.3,   // 26 hide_or_coat_reference_temperature_c — [L1] LiGAPS default
      0.0015  // 27 lactation_curve_parameter_3_or_legacy_fill — [J2] Wood c parameter
    ],
    "female": [
      0.60,    // 1 reflectance_coat — [L1] LiGAPS Bos taurus light-coat default
      0.012,   // 2 coat_length_m — [L1] LiGAPS default
      1.00,    // 3 body_area_factor — [L1] LiGAPS Bos taurus default
      64.1,    // 4 core_skin_conductance_max_W_m2_K — [L1] LiGAPS default
      36.8,    // 5 start_body_weight_kg — [J1] Simmental female calf birth weight
      664.6,   // 6 gompertz_max_adult_weight_kg — [I1] inferred from mature-cow reference × LiGAPS Bos taurus scaling
      36.8,    // 7 birth_weight_kg — [J1] Simmental female calf birth weight
      1.6,     // 8 gompertz_c_parameter — [L1] provisional LiGAPS Bos taurus default
      1.1,     // 9 gompertz_d_parameter — [L1] provisional LiGAPS Bos taurus default
      129.0,   // 10 gompertz_e_parameter — [I2] inferred from LiGAPS Bos taurus slot pattern
      15.2317, // 11 lactation_curve_parameter_1 — [J2] Wood a parameter for 305-day Simmental lactation
      0.1029,  // 12 lactation_curve_parameter_2 — [J2] Wood b parameter
      535.5,   // 13 maximum_adult_weight_reference_kg — [J3] mature cow weight at calf weaning
      1,       // 14 sex_flag_0_male_1_female
      8.0,     // 15 reproductive_energy_or_gestation_parameter — [L1] provisional LiGAPS default
      0.068,   // 16 fattening_or_lactation_rate_parameter — [L1] provisional LiGAPS default
      0.55,    // 17 lower_weight_fraction_for_maintenance — [L1] provisional Bos taurus default
      1.00,    // 18 net_energy_maintenance_multiplier — [L1] Bos taurus default
      0.32,    // 19 minimum_body_reserve_threshold — [L1] provisional default
      11.8,    // 20 bone_lipid_equation_parameter — [L1] provisional default
      0.560,   // 21 carcass_fraction — [I3] set slightly below male value
      4.10,    // 22 carcass_fat_polynomial_parameter — [L1] provisional default
      1.00,    // 23 minimum_core_skin_conductance_factor — [L1] Bos taurus default
      3.08,    // 24 hide_or_coat_parameter_a — [L1] LiGAPS default
      1.73,    // 25 hide_or_coat_parameter_b — [L1] LiGAPS default
      35.3,    // 26 hide_or_coat_reference_temperature_c — [L1] LiGAPS default
      0.0015   // 27 lactation_curve_parameter_3_or_legacy_fill — [J2] Wood c parameter
    ]
  }
}
```

## Reference key for the comments in the JSON block

[J1] Tong et al., *Canadian Journal of Animal Science* (Simmental birth weights). ([Canadian Science Publishing][1])
[J2] Kopec et al., *Animal Bioscience* / PMC article on Wood’s model in dairy Simmental cows. ([PMC][2])
[J3] Crook et al., *South African Journal of Animal Science* (mature-cow weights in South African Simmental cattle). ([SciELO][3])
[J4] Özbeyaz et al., Simmental young-bull slaughter paper reporting 58.4% hot dressing percentage. ([ResearchGate][4])
[L1/L2] inherited from the current LiGAPS settings structure and the LiGAPS supplement’s Bos taurus defaults/guesstimates.  

The block above is the safest research-based starting point. The slots I would prioritize for later calibration are **6, 8, 9, 10, 15, 16, 20, 21, and 22**, because those have the biggest chance of being model-sensitive while not being directly available as Simmental journal measurements.

[1]: https://cdnsciencepub.com/doi/pdf/10.4141/cjas83-002?utm_source=chatgpt.com "breed averages and age of dam adjustment factors for"
[2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8100486/ "
            The effect of extended lactation on parameters of Wood’s model of lactation curve in dairy Simmental cows - PMC
        "
[3]: https://www.scielo.org.za/pdf/sajas/v40n2/v40n2a06.pdf "Genetic parameters for cow weight at calving and cow weight at calf weaning in South African Simmental cattle"
[4]: https://www.researchgate.net/publication/233799448_Certain_fattening_and_slaughter_characteristics_of_simmental_young-bulls "(PDF) Certain fattening and slaughter characteristics of simmental young-bulls"
