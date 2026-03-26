ْQuestion: By searching articles published in official journals, search for the data, variables and values ​​required for this simulator for the Holstein cattle breed that are required in settings.json to define this breed in it and write it in a table with the reference by mentioning the reference. Finally, write the sections related to this breed in settings.json and write the reference as a comment in front of it.

Yes—but only **part** of the 27-slot LiGAPS breed block can be filled from Holstein journal data directly. The simulator needs a full breed/sex parameter set for thermoregulation, growth, lactation, maintenance, and carcass partitioning, and the LiGAPS papers make clear that these breed-specific inputs are part of the model’s required inputs and Table S2-style library structure.

For **Holstein**, the strongest journal-backed values I found are for:

* birth/start body weight,
* mature female weight,
* mature male weight by inference from a bull growth paper,
* female Wood lactation-curve parameters `a, b, c`,
* and carcass/dressing percentage anchors. ([PubMed][1])

For several LiGAPS-specific slots—especially coat/skin heat-transfer constants and some carcass partitioning coefficients—I did **not** find Holstein-specific journal estimates that map one-to-one onto the LiGAPS parameterization. For those, the safest starting point is to keep the **Bos taurus / LiGAPS carryover values** until you calibrate Holstein specifically.

## Recommended Holstein entry for `settings.json`

### A. Direct journal-backed or tightly journal-anchored values

| `settings.json` field                 |   Male | Female | Basis                                                                                                                                                                                                                                  |
| ------------------------------------- | -----: | -----: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `start_body_weight_kg`                |   43.1 |   39.7 | Derived from Holstein calf mean birth weight 41.4 kg with males 8.5% heavier than females. ([PubMed][1])                                                                                                                               |
| `birth_weight_kg`                     |   43.1 |   39.7 | Same as above; LiGAPS uses birth weight explicitly in the Gompertz initialization. ([PubMed][1])                                                                                                                                       |
| `maximum_adult_weight_reference_kg`   | 1043.5 |  705.0 | Female: 705 kg estimated mature BW for Holsteins; male: inferred from Holstein-Friesian bulls being 480 kg at 15 months = 46% of mature weight, giving about 1043.5 kg mature weight. ([PMC][2])                                       |
| `lactation_curve_parameter_a`         |    0.0 |  16.62 | Female value from Holstein Wood-model means; male kept at 0 because males do not lactate, matching LiGAPS structure. ([PMC][3])                                                                                                        |
| `lactation_curve_parameter_b`         |   0.27 |   0.27 | Holstein Wood-model mean. ([PMC][3])                                                                                                                                                                                                   |
| `lactation_curve_parameter_c`         |  0.003 |  0.003 | Holstein Wood-model mean. ([PMC][3])                                                                                                                                                                                                   |
| `milk_available_for_calf_parameter_a` |  16.62 |  16.62 | Best practical proxy is the same Holstein lactation-curve `a`; LiGAPS uses a separate milk-available-to-calf slot but journal Holstein values for that exact LiGAPS slot were not found. This is a model-compatible proxy. ([PMC][3])  |
| `milk_available_for_calf_parameter_b` |   0.27 |   0.27 | Same proxy logic as above. ([PMC][3])                                                                                                                                                                                                  |
| `maximum_carcass_fraction`            |  0.557 |  0.491 | Male: review reports Holstein steers at 55.7% dressing percentage; female: fed Holstein market cows averaged 49.1% DP in JDS 2024. ([PMC][4])                                                                                          |

### B. LiGAPS-compatible values derived from the journal-backed weights

LiGAPS stores both `maximum_adult_weight_reference_kg` and a larger `gompertz_max_adult_weight_kg`; in the shipped LiGAPS breeds, `gompertz_max_adult_weight_kg ≈ 1.242 × maximum_adult_weight_reference_kg`, and `gompertz_reduction_kg_tbw` is the difference between them. That pattern is visible in the current library/settings structure.

| `settings.json` field          |   Male | Female | Basis                                                                                     |
| ------------------------------ | -----: | -----: | ----------------------------------------------------------------------------------------- |
| `gompertz_max_adult_weight_kg` | 1296.0 |  875.6 | Derived with LiGAPS internal ratio ≈ 1.242 × mature reference weight. ([PMC][2])          |
| `gompertz_reduction_kg_tbw`    |  252.5 |  170.6 | Derived as `gompertz_max_adult_weight_kg - maximum_adult_weight_reference_kg`. ([PMC][2]) |

### C. Provisional LiGAPS/Bos taurus carryovers

These are required by the simulator, but I did **not** find clean Holstein-specific journal estimates that match the LiGAPS slot definitions. Keeping Bos taurus carryovers is the lowest-risk starting point.

| `settings.json` field                         |  Male | Female | Recommended value |
| --------------------------------------------- | ----: | -----: | ----------------: |
| `reflectance_coat`                            |  0.60 |   0.60 |              0.60 |
| `coat_length_m`                               | 0.012 |  0.012 |             0.012 |
| `body_area_factor`                            |  1.00 |   1.00 |              1.00 |
| `core_skin_conductance_max_W_m2_K`            |  64.1 |   64.1 |              64.1 |
| `gompertz_integration_constant`               |   1.6 |    1.6 |               1.6 |
| `gompertz_rate_constant`                      |   1.1 |    1.1 |               1.1 |
| `sex_flag_0_male_1_female`                    |     0 |      1 |        structural |
| `minimum_fraction_mature_tbw_for_gestation`   |  0.60 |   0.60 |              0.60 |
| `maintenance_correction_factor`               |  1.00 |   1.00 |              1.00 |
| `minimum_fat_tissue_fraction_for_gestation`   |  0.32 |   0.32 |              0.32 |
| `lipid_bone_parameter`                        |  11.6 |   11.8 |       11.6 / 11.8 |
| `maximum_muscle_bone_ratio`                   |   4.0 |    4.0 |               4.0 |
| `minimum_core_skin_conductance_factor`        |  1.00 |   1.00 |              1.00 |
| `latent_heat_release_parameter_1`             |  3.08 |   3.08 |              3.08 |
| `latent_heat_release_parameter_2`             |  1.73 |   1.73 |              1.73 |
| `latent_heat_release_reference_temperature_c` |  35.3 |   35.3 |              35.3 |

## `settings.json` block for Holstein

Below is a JSON-with-comments style block using short reference tags in the comments. The full reference legend comes right after it.

```json
{
  // Holstein
  "id": 6,
  "name": "Holstein",
  "sex_libraries": {
    "male": {
      "reflectance_coat": 0.60, // L1
      "coat_length_m": 0.012, // L1
      "body_area_factor": 1.00, // L1
      "core_skin_conductance_max_W_m2_K": 64.1, // L1
      "start_body_weight_kg": 43.1, // J1
      "gompertz_max_adult_weight_kg": 1296.0, // I1
      "birth_weight_kg": 43.1, // J1
      "gompertz_integration_constant": 1.6, // L1
      "gompertz_rate_constant": 1.1, // L1
      "gompertz_reduction_kg_tbw": 252.5, // I1
      "lactation_curve_parameter_a": 0.0, // L2
      "lactation_curve_parameter_b": 0.27, // J3
      "maximum_adult_weight_reference_kg": 1043.5, // J2
      "sex_flag_0_male_1_female": 0, // S
      "milk_available_for_calf_parameter_a": 16.62, // J3
      "milk_available_for_calf_parameter_b": 0.27, // J3
      "minimum_fraction_mature_tbw_for_gestation": 0.60, // L1
      "maintenance_correction_factor": 1.00, // L1
      "minimum_fat_tissue_fraction_for_gestation": 0.32, // L1
      "lipid_bone_parameter": 11.6, // L1
      "maximum_carcass_fraction": 0.557, // J4
      "maximum_muscle_bone_ratio": 4.0, // L1
      "minimum_core_skin_conductance_factor": 1.00, // L1
      "latent_heat_release_parameter_1": 3.08, // L1
      "latent_heat_release_parameter_2": 1.73, // L1
      "latent_heat_release_reference_temperature_c": 35.3, // L1
      "lactation_curve_parameter_c": 0.003 // J3
    },
    "female": {
      "reflectance_coat": 0.60, // L1
      "coat_length_m": 0.012, // L1
      "body_area_factor": 1.00, // L1
      "core_skin_conductance_max_W_m2_K": 64.1, // L1
      "start_body_weight_kg": 39.7, // J1
      "gompertz_max_adult_weight_kg": 875.6, // I1
      "birth_weight_kg": 39.7, // J1
      "gompertz_integration_constant": 1.6, // L1
      "gompertz_rate_constant": 1.1, // L1
      "gompertz_reduction_kg_tbw": 170.6, // I1
      "lactation_curve_parameter_a": 16.62, // J3
      "lactation_curve_parameter_b": 0.27, // J3
      "maximum_adult_weight_reference_kg": 705.0, // J2
      "sex_flag_0_male_1_female": 1, // S
      "milk_available_for_calf_parameter_a": 16.62, // J3
      "milk_available_for_calf_parameter_b": 0.27, // J3
      "minimum_fraction_mature_tbw_for_gestation": 0.60, // L1
      "maintenance_correction_factor": 1.00, // L1
      "minimum_fat_tissue_fraction_for_gestation": 0.32, // L1
      "lipid_bone_parameter": 11.8, // L1
      "maximum_carcass_fraction": 0.491, // J5
      "maximum_muscle_bone_ratio": 4.0, // L1
      "minimum_core_skin_conductance_factor": 1.00, // L1
      "latent_heat_release_parameter_1": 3.08, // L1
      "latent_heat_release_parameter_2": 1.73, // L1
      "latent_heat_release_reference_temperature_c": 35.3, // L1
      "lactation_curve_parameter_c": 0.003 // J3
    }
  }
}
```

### Reference legend for the comments

* **J1**: Holstein calf birth-weight anchor from Kertz et al.; mean birth weight 41.4 kg and males 8.5% heavier than females, giving about 43.1 kg male and 39.7 kg female by back-calculation. ([PubMed][1])
* **J2**: Mature-weight anchors: Holstein mature female BW 705 kg; Holstein-Friesian bulls 480 kg at 15 months = 46% of mature weight, implying about 1043.5 kg mature male BW. ([PMC][2])
* **J3**: Holstein Wood-lactation means `a = 16.62`, `b = 0.27`, `c = 0.003`. ([PMC][3])
* **J4**: Holstein steer dressing-percentage anchor 55.7% from a peer-reviewed review summarizing Holstein steer carcass performance. ([PMC][4])
* **J5**: Holstein market-cow dressing percentage 49.1% in fed cows from *Journal of Dairy Science* 2024. ([ScienceDirect][5])
* **I1**: LiGAPS-compatible inference from the shipped breed libraries: `gompertz_max_adult_weight_kg ≈ 1.242 × maximum_adult_weight_reference_kg`, and `gompertz_reduction_kg_tbw` is the difference.
* **L1**: LiGAPS/Bos taurus carryover where no clean Holstein-specific journal value was found for the exact slot definition.
* **L2**: Structural LiGAPS convention: males do not lactate, so `lactation_curve_parameter_a = 0.0`. 
* **S**: Structural sex flag required by the simulator. 

The main caution is that this will make Holstein **runnable** in the simulator, but it is still a **first-pass parameterization**, not a full Holstein calibration. The most uncertainty sits in the thermoregulation coefficients and carcass tissue-partitioning slots, because those are LiGAPS-specific and not commonly reported for Holstein in journal form.

[1]: https://pubmed.ncbi.nlm.nih.gov/9098803/?utm_source=chatgpt.com "Body weight, body condition score, and wither height of ..."
[2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12848261/ "
            Are the recommended proportions of mature body weight being achieved in different stages of growth in Brazilian Holstein and Jersey dairy cattle? - PMC
        "
[3]: https://pmc.ncbi.nlm.nih.gov/articles/PMC4761201/ "
            Effects of season and age at first calving on genetic and phenotypic characteristics of lactation curve parameters in Holstein cows - PMC
        "
[4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8989152/?utm_source=chatgpt.com "Board Invited Review: Crossbreeding beef × dairy cattle for ..."
[5]: https://www.sciencedirect.com/science/article/pii/S0022030224010713 "Improving market (cull) dairy cows' carcass traits and meat quality - ScienceDirect"
