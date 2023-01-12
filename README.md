# ruby-autograder

This is a Docker image made to autograde Ruby Faded Parsons Problems in Prairielearn.

## Quickstart

1) In your `info.json` of the question, include the following:
```json
"gradingMethod": "External",
"externalGradingOptions": {
    "enabled": true,
    "image" : "nasloon/rspec-autograder",
    "entrypoint": "/grader/run.py",
    "timeout" : 60
}
```
  
2) In the `tests/` directory in your question, create a file called `meta.json` that includes the following
```json
{
    "submission_file": "file/to/submit/to.rb",
    "submission_root": "location/to/submit/additional/files/",
    "submit_to_line" : 3,
    "pre-text" : "any lines to precede\n  the student's submission\n", 
    "post-text": "any lines to succeed\n  the student's submission\n",
    "grading_exclusions" : [
        "Any test names that should not be included in grading"
    ]
}
```

3) In the `tests/` directory in your question, include the complete application that the student submits to. Note: do not include the text included in `meta.json`'s `"pre-text"` and `"post-text"` fields as those will be inserted during grading.
