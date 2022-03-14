git add --all
git commit --am
git push origin feature-branch-pipeline-us02-test-creation-02:dev --force-with-lease
git push origin feature-branch-pipeline-us02-test-creation-02:master  --force-with-lease
git push origin feature-branch-pipeline-us02-test-creation-02:feature-branch-pipeline-us02-test-creation  --force-with-lease
python scripts/not_in_use_invoke_codebuild_for_generator_stack.py 
