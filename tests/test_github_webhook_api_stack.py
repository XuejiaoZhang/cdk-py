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
FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../cdk_py")) ## TODO
if FOLDER not in sys.path:
    sys.path.append(FOLDER)

import github_webhook_api_stack
# import route53_stack

# - Defines ------------------------------------------------------------------------------------------------------------
CDK_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../cdk.json")) ##TODO


# - Functions/Classes --------------------------------------------------------------------------------------------------
class TestGithubWebhookApiStack(unittest.TestCase):

    #@pytest.mark.skip(reason="not a unit test, requires authenticated API calls")
    def test_create_stack_ok(self):

        # GIVEN
        with open(CDK_JSON) as json_file:
            cdk_json = json.load(json_file)
        app = core.App()
        
        # config = cdk_json["context"]["config"]
        # region: str = cdk_json["context"]["config"]["accounts"]["dev"]["region"]        
        # dev_account: str = cdk_json["context"]["config"]["accounts"]["dev"]["account"]
        # cdk_json["context"]["config"]["stage"] = "dev"
        
        # r53stack = route53_stack.Route53Stack(app, 
        #                                       "test-route53-stack",
        #                                       config=cdk_json["context"]["config"],
        #                                       env={'account': dev_account,'region': region})
                                              
        
        # print(cdk_json)
        
        # WHEN
        stack = github_webhook_api_stack.GithubWebhookApiStack(app, 
                                                        "test-github-webhook-api-stack",
                                                        config=cdk_json["context"]["config"],
                                                        # hosted_zone_id=r53stack.hosted_zone.hosted_zone_id,
                                                        # hosted_zone_name=r53stack.hosted_zone.zone_name,
                                                        # env={'account': dev_account,'region': region}
                                                        synthesizer=DefaultStackSynthesizer(),
                                                        )
        
        # THEN
        stack_artifact = app.synth().get_stack_artifact(stack.artifact_id)
        stack_art_dict = stack_artifact.template
        
        # CHECK
        self.assertEqual(True, isinstance(stack, github_webhook_api_stack.GithubWebhookApiStack))
        self.assertEqual(True, isinstance(stack, core.Stack))
        self.assertEqual(True, isinstance(stack_art_dict, dict))

# - Main ---------------------------------------------------------------------------------------------------------------

# - EOF -
