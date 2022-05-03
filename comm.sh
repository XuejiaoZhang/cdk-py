hash1=$(git rev-parse origin/feature-branch-pipeline-us03-deploy-self-mutating-false); echo $hash1; hash2=$(git rev-parse origin/master); echo $hash2;
git diff-tree --stat $hash1 $hash2
