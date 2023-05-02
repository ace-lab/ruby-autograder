from os import popen
from json import loads as json_loads
from json.decoder import JSONDecodeError
from typing import Callable, Dict, List, Set, Union
from dataclasses import dataclass

GRADING_SCRIPT: str = " && ".join([
    'cd {work}',
    # 'bundle config path /grader/vendor/bundle',
    'bundle install --local --without production --quiet',
    'rspec --format json' 
])

@dataclass
class Failure:
    exception: str
    err_msg: str
    backtrace: List[str]

    def __eq__(self, o) -> bool:
        if o is None:
            return False
        
        same_ex = self.exception == o.exception

        backtrace_lens = len(self.backtrace) == len(o.backtrace)
        same_stack = backtrace_lens and all(
            [ stack_1 == stack_2 for stack_1, stack_2 in zip(self.backtrace, o.backtrace) ])
        
        return same_ex and same_stack

@dataclass
class Test:
    name: str
    failure: Failure = None

    def __eq__(self, o) -> bool:
        return self.failure == o.failure

@dataclass
class Suite:
    tests: Dict[str, Test]

    def get_test(self, test_name: str) -> Test:
        return self.tests.get(test_name, None)

    def grade(self, failure_case : Callable[[Test], Union[str, None]], exclude: Set[str]=set({})
                ) -> List[Dict[str, Union[str, int]]]:
        """Return a list of json objects representing the student's performance
        on the tests provided in the solution test suite."""
        out = []
        
        for name, test in self.tests.items():
            if name in exclude:
                continue
            
            points = 0
            max_pts = 1

            if test.failure is not None:
                msg = failure_case(test)
                # raise Exception(f"The test '{name}' did not pass on the solution system under test!")
                # msg = f"Failed: \n{test.failure.err_msg} \n"
            elif test.failure is None:
                msg = f"Passed."
                points = max_pts

            out.append({
                "name" : name,
                "output" : msg,
                "points" : points,
                "max_points" : max_pts
            })

        return out


def run(work_dir: str) -> str:
    """Run a test suite and return stdout"""
    return popen(f"cd {work_dir} && {GRADING_SCRIPT.format(work=work_dir)}").read()

def verifyOutput(output: str) -> bool:
    """Returns if the passed string is a valid output"""
    try:
        data = json_loads(output)
    except JSONDecodeError:
        return False
    return data['summary']['errors_outside_of_examples_count'] == 0

def parse(stdout: str) -> Suite:
    """Produce a summary of a run test suite"""
    json = json_loads(stdout)
    tests: Dict[str, Test] = {}
    for rspec_test in json['examples']:
        
        if rspec_test['status'] == 'passed':
            failure = None
        else:
            ex = rspec_test['exception']

            failure = Failure(
                exception=ex['class'], 
                err_msg=ex['message'], 
                backtrace=ex['backtrace']
            )

        test_name: str = rspec_test['full_description']

        tests[test_name] = Test(
            name=test_name,
            failure=failure
        )
    
    return Suite(tests)

def execute(solution: bool, work_dir: str) -> Suite:
    """Run a test suite and return a summary of it"""
    
    stdout = run(work_dir)

    if not verifyOutput(stdout):
        suite = "instructor" if solution else "student"
        print(f"Error when running {suite} test suite. Output:")
        print(f"> {stdout}")
        exit(1)
    
    return parse(stdout)

