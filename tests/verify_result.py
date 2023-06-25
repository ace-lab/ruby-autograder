from json import loads as json_loads
from typing import Dict, Union, List
import sys

assert len(sys.argv) > 2, "usage: verify_out.py <path/to/expected.json> <path/to/produced.json>"
EXP_PATH = sys.argv[1]
RES_PATH = sys.argv[2]

class GradabilityError(Exception):
    pass

class GraderMismatchError(Exception):
    pass

class PLTest:

    def __init__(self, name: str, output:str, points:int, max_points:int = 1):
        self.name = name
        self.output = output
        self.points = points
        self.max_points = max_points

    def __eq__(self, __value: object) -> bool:
        same_name = self.name == __value.name
        similar_out = set(self.output.split('\n')) == set(__value.output.split('\n'))
        same_points = self.points == __value.points
        same_max_points = self.max_points == __value.max_points

        return same_name and same_points and same_max_points and similar_out

    def __str__(self) -> str:
        return f"PLTest(name={self.name}, points={self.points}, max_points={self.max_points}\n" + \
               f'       output="""{self.output}""")'

class GraderRun:

    def __init__(self, *argv: List[Union[PLTest, str]], gradable: bool = True) -> None:
        self.gradable = gradable
        self.tests = {}
        self.messages = []

        if self.gradable:
            for tst in argv:
                self.tests[tst.name] = tst
        else:
            self.messages.extend(argv)

    def __eq__(self, other: object) -> bool:

        expected_run = other
        resulted_run = self

        if expected_run.gradable is not resulted_run.gradable:
            raise GradabilityError(
                f"This run is expected to be {'not ' if expected_run.gradable else ''}gradable" + \
                 " but returns {'not ' if resulted_run.gradable else ''}"
            )

        if not expected_run.gradable:
            return expected_run.messages == resulted_run.messages

        expected_tests = []
        unexpected_tests = []
        different_tests = []

        for test, grades in expected_run.tests.items():
            if test not in resulted_run.tests:
                expected_tests.append((test, grades))
            elif resulted_run.tests.get(test) != grades:
                different_tests.append((test, grades, resulted_run.tests.get(test)))

        for test, grades in resulted_run.tests.items():
            if test not in expected_run.tests.keys():
                unexpected_tests.append((test, grades))

        if len(expected_tests) + len(unexpected_tests) + len(different_tests) > 0:
            raise GraderMismatchError("The test results do not match", 
                                      { "expected"   : expected_tests, 
                                        "unexpected" : unexpected_tests, 
                                        "different"  : different_tests   })
        return True

def parse_json(path: str) -> GraderRun:

    with open(path, 'r') as f:
        data: Dict = json_loads(f.read())

        if data['gradable']:
            tests = [ PLTest(**tst) for tst in data['tests'] ]
            return GraderRun(*tests, gradable=data['gradable'])
        elif isinstance(data['format_errors'], list):
            return GraderRun(*data['format_errors'], gradable=data['gradable'])
        return GraderRun(data['format_errors'], gradable=data['gradable'])

result: GraderRun = parse_json(RES_PATH)
expected: GraderRun = parse_json(EXP_PATH)

try:
    matched = result == expected
except GraderMismatchError as mismatch:
    exp   = mismatch.args[1]['expected']
    unexp = mismatch.args[1]['unexpected']
    diff  = mismatch.args[1]['different']

    print(f"{len(exp)} expected tests not found")
    print(f"{len(unexp)} unexpected tests found")
    print(f"{len(diff)} differing grades found")

    if len(sys.argv) > 3:
        import code
        code.interact(local=locals())
    sys.exit(1)
except GradabilityError as err:
    print(*err.args)
    sys.exit(1)

print("No difference found")
