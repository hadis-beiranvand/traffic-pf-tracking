# Examples

- `two_cars.json` - the 2-car run whose MATLAB result is stored in `matlab_reference.json`
  (used by `tests/test_against_matlab.py`).
- `thesis_table_4_1.json` - the six cars of Table 4-1 of the thesis.

**Street numbers.** In the thesis figures the streets are numbered 1 = top, 2 = left, 3 = bottom,
4 = right. This code numbers the *heading* instead: 1 = moving left (enters from the right),
2 = moving right (from the left), 3 = moving down (from the top), 4 = moving up (from the bottom).
So thesis source street 1/2/3/4 is `street` 3/2/4/1 here, and thesis destination street 1/2/3/4 is
`goal_street` 4/1/3/2. `thesis_table_4_1.json` is already converted. The table gives no car size;
5 is assumed.
