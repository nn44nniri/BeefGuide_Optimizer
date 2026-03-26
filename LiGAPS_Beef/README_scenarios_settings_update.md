LiGAPS-Beef settings update: scenarios and diet setup moved to settings.json

What changed
- Scenario execution is now controlled from settings.json via simulation.case_ids.
- The ten illustration scenarios are defined in settings.json under scenarios.
- Diet and feeding setup are now per-scenario fields in settings.json.
- You can run only one scenario (for example [1]) or any subset of scenarios.
- Core formulas and overall simulator behavior remain unchanged when using the packaged default settings.

Key settings structure
- simulation.case_ids: list of scenario ids to execute
- scenarios[].id: scenario id
- scenarios[].breed_id: breed id from breeds
- scenarios[].slaughter_weight: scenario slaughter weight
- scenarios[].location: FRANCE1 or AUSTRALIA1
- scenarios[].housing: three integers matching the original housing slots
- scenarios[].feed_availability.feed2 / feed3: feed availability values used by the simulator
- scenarios[].diet.*: feed names, quantities, and fractions

Supported feed names
- WHEAT
- BARLEY
- PASTURE1
- HAY

Example: run only scenario 1
{
  "simulation": {
    "case_ids": [1]
  }
}
