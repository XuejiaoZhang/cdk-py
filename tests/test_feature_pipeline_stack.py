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

import feature_pipeline_stack

# - Defines ------------------------------------------------------------------------------------------------------------
CDK_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../../../cdk.json"))


# - Functions/Classes --------------------------------------------------------------------------------------------------
class TestFeaturePipelineStack(unittest.TestCase):

    def test_create_stack_ok(self):

        # GIVEN
        with open(CDK_JSON) as json_file:
            cdk_json = json.load(json_file)
        app = core.App()
        
        # WHEN
        stack = feature_pipeline_stack.FeaturePipelineStack(app, 
                                                "test-feature-pipeline-stack",
                                                feature_branch_name="feature/CAE-5781/feature_branch_pipeline", #TODO: dev
                                                config=cdk_json["context"]["config"],
                                            )

        # THEN
        stack_artifact = app.synth().get_stack_artifact(stack.artifact_id)
        stack_art_dict = stack_artifact.template
        
        # CHECK
        self.assertEqual(True, isinstance(stack, feature_pipeline_stack.FeaturePipelineStack))
        self.assertEqual(True, isinstance(stack, core.Stack))
        self.assertEqual(True, isinstance(stack_art_dict, dict))

# - Main ---------------------------------------------------------------------------------------------------------------

# - EOF -
