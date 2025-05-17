#!/bin/bash
# Example script for creating work units inside a BOINC project directory.
# Run this after `make_project agiNet` and copy the contents of `server/` there.

set -e

for skill in vision language memory planner; do
    ./bin/sched_create_work \
        --appname "$skill" \
        --wu_name "${skill}_wu" \
        --wu_template ./wu_template.xml \
        --result_template ./result_template.xml
done
