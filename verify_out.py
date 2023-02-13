from json import loads as json_loads
from sys import argv, exit

assert len(argv) > 2, "usage: verify_out.py <path/to/expected.json> <path/to/produced.json>"
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
    for test, grades in exp_parsed.items():
        if test not in res_parsed.items():
            expected.append((test, grades))
        elif res_parsed[test] != grades:
            different.append(test)

    for test, grades in res_parsed.items():
        if test not in exp_parsed.items():
            unexpected.append((test, grades))
    print(f"{len(expected)} expected tests not found")
    print(f"{len(unexpected)} unexpected tests found")
    print(f"{len(different)} expected tests with differing grades found")
    print("Run with python -i to inspect `expected`, `unexpected`, and `different`")


