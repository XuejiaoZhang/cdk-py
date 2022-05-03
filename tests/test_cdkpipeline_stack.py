#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# - Standard Library Imports -------------------------------------------------------------------------------------------
import os
import sys
import unittest
import json

# - Third Party Imports ------------------------------------------------------------------------------------------------
import pytest
from aws_cdk import core

# - Local Application/Library Specific Imports -------------------------------------------------------------------------
FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../"))
if FOLDER not in sys.path:
    sys.path.append(FOLDER)

import cdkpipeline_stack

# - Defines ------------------------------------------------------------------------------------------------------------
CDK_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../../../cdk.json"))


# - Functions/Classes --------------------------------------------------------------------------------------------------
class TestCDKPipelineStack(unittest.TestCase):

    def test_create_stack_ok(self):

        # GIVEN
        with open(CDK_JSON) as json_file:
            cdk_json = json.load(json_file)
        app = core.App()
        
        # WHEN
        stack = cdkpipeline_stack.CDKPipelineStack(app, 
                                                    "test-cdkpipeline-stack",
                                                    branch_name="feature/CAE-5781/feature_branch_pipeline", #TODO: dev
                                                    creation_or_deletion="creation",
                                                    branch_name_queue="",
                                                    branch_prefix='feature-branch-pipeline-',
                                                    feature_pipeline_suffix="-FeatureBranchPipeline",
                                                    config=cdk_json["context"]["config"],
                                                )
    

        # THEN
        stack_artifact = app.synth().get_stack_artifact(stack.artifact_id)
        stack_art_dict = stack_artifact.template
        
        # CHECK
        self.assertEqual(True, isinstance(stack, cdkpipeline_stack.CDKPipelineStack))
        self.assertEqual(True, isinstance(stack, core.Stack))
        self.assertEqual(True, isinstance(stack_art_dict, dict))

# - Main ---------------------------------------------------------------------------------------------------------------

# - EOF -
