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

import github_webhook_api_stack

# - Defines ------------------------------------------------------------------------------------------------------------
CDK_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../../../cdk.json"))


# - Functions/Classes --------------------------------------------------------------------------------------------------
class TestGithubWebhookApiStack(unittest.TestCase):

    def test_create_stack_ok(self):

        # GIVEN
        with open(CDK_JSON) as json_file:
            cdk_json = json.load(json_file)
        app = core.App()

        # WHEN
        stack = github_webhook_api_stack.GithubWebhookAPIStack(app, 
                                                            "test-github-webhook-api-stack",
                                                            config=cdk_json["context"]["config"],
                                                            branch_prefix="^CAE-[0-9]+/[feature|bug|hotfix]",
                                                            feature_pipeline_suffix="-FeatureBranchPipeline",
                                                        )
   


        # THEN
        stack_artifact = app.synth().get_stack_artifact(stack.artifact_id)
        stack_art_dict = stack_artifact.template
        
        # CHECK
        self.assertEqual(True, isinstance(stack, github_webhook_api_stack.GithubWebhookAPIStack))
        self.assertEqual(True, isinstance(stack, core.Stack))
        self.assertEqual(True, isinstance(stack_art_dict, dict))

# - Main ---------------------------------------------------------------------------------------------------------------

# - EOF -
