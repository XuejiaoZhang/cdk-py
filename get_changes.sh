feature_branch=origin/feature-branch-pipeline-us03-deploy-self-mutating-false
feature_branch=$1
#TODO
git clone https://XuejiaoZhang:$token2@github.com/XuejiaoZhang/cdk-py-test.git

git remote add github https://XuejiaoZhang:$token@github.com/XuejiaoZhang/cdk-py.git
git fetch github
git branch -a
# git checkout -f github/development

hash1=$(git rev-parse $feature_branch)
echo $hash1
hash2=$(git rev-parse origin/development)
echo $hash2;
git diff-tree --name-only -r $hash1 $hash2 > file_changes.txt
