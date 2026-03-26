This package updates LiGAPSBeef_herd.py so breed libraries are loaded dynamically from settings.json.

Additional compatibility fix in this revision:
- If settings.json defines only one breed and does not define `case_breed_ids`, the built-in
  10 illustration cases automatically reuse that single configured breed for every case.
- If you want specific breeds per case, add `case_breed_ids` as a list of 10 breed ids in settings.json.
- If multiple breeds are defined and `case_breed_ids` is omitted, the original default case-breed
  mapping is preserved.

This keeps existing single-breed settings files runnable without changing the core model logic.
