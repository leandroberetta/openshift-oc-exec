#!/usr/bin/env bash

coverage3 run openshift_oc_exec_test.py
coverage3 html --omit openshift_oc_exec_test.py