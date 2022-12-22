#!/usr/bin/python3
from typing import Dict
from json import loads as json_loads, dumps as json_dumps
import grading
import os

#dev imports;; remove before production
from pprint import pprint

ROOT_DIR = "/grade"

WORK_DIR = f"{ROOT_DIR}/working/"
APP_DIR = f"{ROOT_DIR}/tests/app/"

    
def write_to(content: str, to: str, line: int = 0) -> None:
    """Write `content` to line `line` of file `to`"""
    new_lines = [ l + '\n' for l in content.split('\n') ]
    with open(to, "r") as old:
        old_content = old.readlines()
    
    final_lines = old_content[:line] + new_lines + old_content[line:]

    with open(to, "w") as out:
        out.writelines(final_lines)

def run(content, grading_info, work_dir=WORK_DIR, app_dir=APP_DIR):
    os.system(f"rm -rf {work_dir}/*")
    os.system(f"cp -r {app_dir}/* {work_dir}")

    write_to(
        content,
        to=f"{work_dir}/{grading_info['submission_file']}",
        line=grading_info['submit_to_line']
    )

    return grading.execute()

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

    sub = run(
        grading_info.get('pre-text', '') + "\n" + 
            submission_data['submitted_answers']['student-parsons-solution'] + "\n" +
            grading_info.get('post-text', ''),
        grading_info
    )    

    sol = run(
        grading_info.get('pre-text', '') + "\n" + 
            solution + "\n" +
            grading_info.get('post-text', ''),
        grading_info
    )

    gradingData: Dict = {
        'gradable' : True,
        'tests' : grading.grade(
            sol, sub, 
            set(grading_info['grading_exclusions'])
        )
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
    main()