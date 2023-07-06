REMOTE="saasbook"
IMAGE="pl-fpp-ruby-autograder"

build() { sudo docker build -t $REMOTE/$IMAGE . ; }
push() { sudo docker push $REMOTE/$IMAGE:latest ; }
buildPush() { build && push ; }

buildImage() { # build $IMAGE:dev
    # only report errors
    hash="$(sudo docker build -q -t $IMAGE:dev .  | cut -d: -f2)"
    echo \> Image name/hash: $IMAGE:dev / $hash
}

deleteImage() { # delete $IMAGE:dev locally
    echo -n Deleting image ...
    sudo docker image rm $IMAGE:dev > /dev/null
    echo done.
}

runImage() { # run $IMAGE:dev as `autograder_test`
    # silence both stderr and stdout 
    deleteCont &> /dev/null

    echo Running Image ...
    ( sudo docker run --name autograder_test --network none --mount type=bind,source=`pwd`/.container_mount/grade,target=/grade $IMAGE:dev /grader/run.py \
            2>.container_mount/stderr \
            1>.container_mount/stdout & )
    sleep 1
    docker container ls
    code="$(docker container wait autograder_test)"
    echo \> Container exited with code $code
    if [[ $code != "0" ]]; then 
        echo \> Stdout:
        cat .container_mount/stdout

        echo \> Stderr:
        cat .container_mount/stderr
    fi
    rm .container_mount/stdout
    rm .container_mount/stderr
    #echo ==============================================================
    return $code
}

deleteCont() { # delete the container named `autograder_test`
    sudo docker container rm autograder_test
}

prep_mount() { # assuming $1 is the variants_dir (the question/tests/ directory)

    which jq > /dev/null
    if [[ $? != "0" ]]; then 
        echo "jq is required to run this script, please install and add it to your \$PATH"
        return 1
    fi

    echo "Preparing mount files ... "

    sudo rm -rf .container_mount

    # make all the necessary dirs
    mkdir .container_mount

    mkdir .container_mount/grade
    mkdir .container_mount/grade/data
    mkdir .container_mount/grade/serverFilesCourse
    mkdir .container_mount/grade/student
    mkdir .container_mount/grade/tests

    # load the variants
    # script_dir="$(pwd)/${0::-18}"
    variant_dir="$(pwd)/$1/"
    cp -r $variant_dir/* .container_mount/grade/tests/
    rm .container_mount/grade/tests/data.json
    rm .container_mount/grade/tests/expected.json

    # load submission files
    if [[ -f $variant_dir/data.json ]]; then
        cp $variant_dir/data.json .container_mount/grade/data/
    elif [[ -d $variant_dir/submission ]]; then
        cp -r $variant_dir/submission/* .container_mount/grade/student

        echo {\"submitted_answers\": {\"student-parsons-solution\": `jq -Rs . < .container_mount/grade/student/_submission_file`}} \
            > .container_mount/grade/data/data.json
        ## double-check that _submission_file isn't in /grade/student
        rm .container_mount/grade/student/_submission_file
    else 
        echo "No submission found: Exiting"
        return 1
    fi

    # now that the files are in place, install the packages
    pd=`pwd`
    rvm use 2.6.10
    if [[ $? != "0" ]]; then return 1; fi
    
    cd .container_mount/grade/tests/app
    bundle package --all --all-platforms --quiet > /dev/null
    # bundle install --local > /dev/null
    cd $pd

    echo done.
}

clean() {
    sudo chown -R $USER .container_mount/grade/
    rm -r .container_mount/
    return
}

clean_up() { # Remove .container_mount/ and delete $IMAGE:dev and $IMAGE:latest locally
    clean
    deleteImage
}

compare() { # assuming $1 is the variant directory, $2 is the script directory
    # compare the result
    echo ========================= COMPARISON =========================
    echo
    output_loc="`pwd`/.container_mount/grade/results/results.json"
    python3 $2/tests/verify_result.py $1/expected.json $output_loc
    exit_code=$?
    echo
    echo ======================= END COMPARISON =======================

    return $exit_code
}

run_test() { # $1 is variant_dir (the question/tests/ directory)

    if [[ $1 == "" ]]; then 
        echo Test not provided, assuming \`run_tests\`
        run_tests
        if [[ $? != "0" ]]; then return 1; fi
    fi

    # basically remove "run_test.sh" from the script call to get the directory
    script_dir=`pwd`

    prep_mount $1
    if [[ $? != "0" ]]; then return 1; fi

    echo Running the grader
    buildImage
    runImage

    if [[ $? == 0 ]]; then
        deleteCont > /dev/null
        if [[ $? != "0" ]]; then return 1; fi

        deleteImage
        if [[ $? != "0" ]]; then return 1; fi
    else return 1; fi

    compare $1 $script_dir

    return $?
}

run_tests() { # run all tests in tests/
    tests=`ls -d tests/*/`
    script_dir=`pwd`

    failures=0
    failed=""

    buildImage

    while IFS= read -r variant_dir; do
        
        echo Running test $variant_dir

        prep_mount $variant_dir
        if [[ $? != "0" ]]; then return 1; fi

        runImage
        if [[ $? != "0" ]]; then 
            failures=$((failures+1)); 
            failed="$failed\n> $variant_dir"
        else
            compare $variant_dir $script_dir
            if [[ $? != "0" ]]; then 
                failures=$((failures+1)); 
                failed="$failed\n> $variant_dir"
            fi
        fi

    done  <<< "$tests"

    if [[ $failures == "0" ]]; then deleteImage; fi

    echo -e "Failures: $failures $failed"
    return $((1 - ($failures == 0)))
}

new_test() { # $1 is the new test name (must be a valid filename)

    if [[ $1 == "" ]]; then 
        echo Error: Please supply a test name that is a valid filename
        return 1
    fi

    # make the base folders and files
    cd tests/
    mkdir $1
    mkdir $1/app
    mkdir $1/app/spec

    touch $1/app/script.rb
    touch $1/app/Gemfile
    touch $1/solution

    # initialize the spec file
    echo -e "require_relative '../script.rb'\n" > $1/app/spec/script_spec.rb

    # populate the json objects with filler
    meta_content="{\n    \"submission_file\": \"script.rb\",\n    \"submission_root\": \"\"\n}\n"
    expected_content="{\n    \"gradable\":true,\n    \"tests\":[],\n    \"score\":0.0\n}\n"
    data_content="{\n    \"submitted_answers\" : {\n        \"student-parsons-solution\": \"\"\n    },\n    \"gradable\": true\n}\n"
    echo -e "$meta_content" >> $1/meta.json
    echo -e "$expected_content" >> $1/expected.json
    echo -e "$data_content" >> $1/data.json


    # return to base directory
    cd ../
    return
}

debug() {
    sudo docker run -it --rm \
        --mount type=bind,source=`pwd`/.container_mount/grade,target=/grade \
        --mount type=bind,source=`pwd`/debug_tools.sh,target=/tools.sh \
        $IMAGE:dev
    return
}
