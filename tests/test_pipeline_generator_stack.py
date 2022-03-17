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
from aws_cdk.core import DefaultStackSynthesizer

# - Local Application/Library Specific Imports -------------------------------------------------------------------------
FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../"))
if FOLDER not in sys.path:
    sys.path.append(FOLDER)

import pipeline_generator_stack

# - Defines ------------------------------------------------------------------------------------------------------------
CDK_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../../../cdk.json"))


# - Functions/Classes --------------------------------------------------------------------------------------------------
class TestPipelineGeneratorStack(unittest.TestCase):

    def test_create_stack_ok(self):

        # GIVEN
        with open(CDK_JSON) as json_file:
            cdk_json = json.load(json_file)
        app = core.App()

        config = cdk_json["context"]["config"]
        region: str = cdk_json["context"]["config"]["accounts"]["tooling"]["region"]
        toolchain_account: str = cdk_json["context"]["config"]["accounts"]["tooling"]["account"]


        # WHEN
        stack = pipeline_generator_stack.PipelineGeneratorStack(app, 
                                                            "test-feature-branch-pipeline-generator",
                                                            branch_name="feature/CAE-5781/feature_branch_pipeline", #TODO: dev
                                                            branch_prefix="^CAE-[0-9]+/[feature|bug|hotfix]",
                                                            feature_pipeline_suffix="-FeatureBranchPipeline",
                                                            config=cdk_json["context"]["config"],
                                                            env={'account': toolchain_account, 'region': region},
                                                            synthesizer=DefaultStackSynthesizer(),
                                                        )

        # THEN
        stack_artifact = app.synth().get_stack_artifact(stack.artifact_id)
        stack_art_dict = stack_artifact.template
        
        # CHECK
        self.assertEqual(True, isinstance(stack, pipeline_generator_stack.PipelineGeneratorStack))
        self.assertEqual(True, isinstance(stack, core.Stack))
        self.assertEqual(True, isinstance(stack_art_dict, dict))

# - Main ---------------------------------------------------------------------------------------------------------------

# - EOF -
