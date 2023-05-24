from json import loads as json_loads
from sys import argv, exit

assert len(argv) > 2, "usage: verify_result.py <path/to/expected.json> <path/to/produced.json>"
exp_path = argv[1]
res_path = argv[2]

with open(exp_path, 'r') as f:
    exp = json_loads(f.read())

with open(res_path, 'r') as f:
    res = json_loads(f.read())

res_parsed = {}
for test in res['tests']:
    res_parsed[test['name']] = test
exp_parsed = {}
for test in exp['tests']:
    exp_parsed[test['name']] = test


if exp_parsed == res_parsed:
    print(f"No difference found")
    exit()
else:
    expected = []
    unexpected = []
    different = []

    def matching_results(result1, result2) -> bool:
        # return result1 != result2
        matching = True
        for field in ['name', 'points', 'max_points']:
            matching = matching and ( result1[field] == result2[field] )
        return matching

    for test, grades in exp_parsed.items():
        if test not in res_parsed.keys():
            expected.append((test, grades))
        elif not matching_results(res_parsed[test], grades):
            different.append(test)

    for test, grades in res_parsed.items():
        if test not in exp_parsed.keys():
            unexpected.append((test, grades))
    print(f"{len(expected)} expected tests not found")
    print(f"{len(unexpected)} unexpected tests found")
    print(f"{len(different)} differing grades found")
    print("Run with python -i to inspect `expected`, `unexpected`, and `different`")
    if (len(unexpected) + len(different)) > 0:
        exit(1)
    else:
        print("Difference in (unchecked) outputs")


