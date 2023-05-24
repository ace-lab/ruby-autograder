#!/usr/bin/python3
from time import perf_counter
start_time = perf_counter()
from typing import Dict, Set, Union
from json import loads as json_loads, dumps as json_dumps
import grading
import os

#dev imports;; remove before production
from pprint import pprint


ROOT_DIR = "/grade"

WORK_DIR = f"{ROOT_DIR}/working/"
APP_DIR = f"{ROOT_DIR}/tests/app/"

    
def write_to(content: str, to: str, line: int = -1) -> None:
    """Write `content` to line `line` of file `to`"""
    new_lines = [ l + '\n' for l in content.split('\n') ]
    with open(to, "r") as old:
        old_content = old.readlines()
        old_content += ["\n"]
    
    final_lines = old_content[:line] + new_lines + old_content[line:]

    with open(to, "w") as out:
        out.writelines(final_lines)

def run(submission_content: str, grading_info: Dict, solution: bool, work_dir: str = WORK_DIR, 
        app_dir: str = APP_DIR) -> grading.Suite:
    os.system(f"rm -rf {work_dir}/*")
    os.system(f"cp -r {app_dir}/* {work_dir}")

    write_to(
        submission_content,
        to=f"{work_dir}/{grading_info['submission_file']}",
        line=grading_info['submit_to_line']
    )

    print("    <run> file ops done", perf_counter() - start_time)

    return grading.execute(solution=solution, work_dir=WORK_DIR)

def verify_valid_solution(sol: grading.Suite, exclusions: Set[str]=set({})) -> None:
    def failed_solution_test(test: grading.Test) -> None:
        raise Exception(f"The test '{test.name}' did not pass on the solution system under test!")

    sol_report = sol.grade(
        failure_case=failed_solution_test, 
        exclude=exclusions
    ) 
    sol_points = sum(map(lambda report: report['points'], sol_report))
    max_points = sum(map(lambda report: report['max_points'], sol_report))
    if sol_points != max_points:
        raise Exception(f"The solution does not score 100%!")


def main():

    if not os.path.exists(f"{ROOT_DIR}"):
        raise Exception(f"ERROR: {ROOT_DIR} not found! Mounting may have failed.")

    with open(f"{ROOT_DIR}/tests/meta.json", 'r') as info:
        grading_info = json_loads(info.read())
    with open(f"{ROOT_DIR}/data/data.json", 'r') as data:
        submission_data = json_loads(data.read())
    with open(f"{ROOT_DIR}/tests/solution", 'r') as sol:
        solution = sol.read()

    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)

    print("Assertions and setup done", perf_counter() - start_time)

    sol: grading.Suite = run(
        grading_info.get('pre-text', '') + "\n" + 
            solution + "\n" +
            grading_info.get('post-text', ''),
        grading_info,
        solution=True
    )

    print("Solution run", perf_counter() - start_time)

    try:
        verify_valid_solution(sol, set(grading_info['grading_exclusions']))
    except Exception as e:
        print(*e.args)

    print("Solution verified", perf_counter() - start_time)

    sub: grading.Suite = run(
        grading_info.get('pre-text', '') + "\n" + 
            submission_data['submitted_answers']['student-parsons-solution'] + "\n" +
            grading_info.get('post-text', ''),
        grading_info,
        solution=False
    )

    print("Submission run", perf_counter() - start_time)
    
    sub_report = sub.grade(
        failure_case=(lambda test: f"Failed: \n{test.failure.err_msg} \n"),
        exclude=set(grading_info['grading_exclusions'])
    )

    print("Submission graded", perf_counter() - start_time)

    gradingData: Dict = {
        'gradable' : True,
        'tests' : sub_report
    }

    pts = sum([ test['points'] for test in gradingData['tests'] ])
    max_pts = sum([ test['max_points'] for test in gradingData['tests'] ])
    gradingData['score'] = pts / max_pts

    if not os.path.exists(out_path := f"{ROOT_DIR}/results"):
        os.mkdir(out_path)
    with open(f'{ROOT_DIR}/results/results.json', 'w+') as results:
        json_data: str = json_dumps(gradingData)
        pprint(gradingData)
        results.write(json_data)

if __name__ == '__main__':
    print("Imports and definitions done:", perf_counter() - start_time)
    main()
else:
    ###############################
    ###     DEBUG FUNCTIONS     ###
    ###############################

    def load_system(content: str, solution: bool = False):

        if not os.path.exists(f"{ROOT_DIR}"):
            raise Exception(f"ERROR: {ROOT_DIR} not found! Mounting may have failed.")
        with open(f"{ROOT_DIR}/tests/meta.json", 'r') as info:
            grading_info = json_loads(info.read())
        if not os.path.exists(WORK_DIR):
            os.mkdir(WORK_DIR)
        
        os.system(f"rm -rf {WORK_DIR}/*")
        os.system(f"cp -r {APP_DIR}/* {WORK_DIR}")

        write_to(
            content,
            to=f"{WORK_DIR}/{grading_info['submission_file']}",
            line=grading_info['submit_to_line']
        )

    def load_sol():
        if not os.path.exists(f"{ROOT_DIR}"):
            raise Exception(f"ERROR: {ROOT_DIR} not found! Mounting may have failed.")
        with open(f"{ROOT_DIR}/tests/meta.json", 'r') as info:
            grading_info = json_loads(info.read())
        with open(f"{ROOT_DIR}/tests/solution", 'r') as sol:
            solution = sol.read()

        load_system(
            grading_info.get('pre-text', '') + "\n" + 
                solution + "\n" +
                grading_info.get('post-text', ''), 
            solution=True
        )

    def load_sub():
        if not os.path.exists(f"{ROOT_DIR}"):
            raise Exception(f"ERROR: {ROOT_DIR} not found! Mounting may have failed.")
        with open(f"{ROOT_DIR}/tests/meta.json", 'r') as info:
            grading_info = json_loads(info.read())
        with open(f"{ROOT_DIR}/data/data.json", 'r') as data:
            submission_data = json_loads(data.read())

        load_system(
            grading_info.get('pre-text', '') + "\n" + 
                submission_data['submitted_answers']['student-parsons-solution'] + "\n" +
                grading_info.get('post-text', ''),
            solution=False
        )
    
    