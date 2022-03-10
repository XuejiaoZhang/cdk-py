git add --all
git commit --am
git push origin dev --force-with-lease
git push origin dev:master  --force-with-lease
git push origin dev:feature-branch-pipeline-us01  --force-with-lease
python scripts/invoke_codebuild_for_generator_stack.py 
