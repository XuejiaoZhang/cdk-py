import docker
import boto3
import logging
import base64
import time
import os

LOGGER = logging.getLogger(__name__)


docker_client = docker.from_env()
ecr_client = boto3.client("ecr", region_name="us-west-2")
ecr_token = ecr_client.get_authorization_token()
ecr_username, ecr_password = (
    base64.b64decode(ecr_token["authorizationData"][0]["authorizationToken"])
    .decode()
    .split(":")
)
ecr_registry = ecr_token["authorizationData"][0]["proxyEndpoint"]

TOOLING_ACCOUNT_ID="320185343352"
REGION="us-west-2"
name="build_cache"

def _build_docker_image(name: str, image_tag: str, docker_build_path: str):

    ecr_image_repo = f"{TOOLING_ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/{name}"
    # commit_hash = os.getenv("CODEBUILD_RESOLVED_SOURCE_VERSION", "NA")[0:7]

    LOGGER.info(
        f"About to start Docker build for image {ecr_image_repo}:{image_tag} at {time.ctime()}."
    )
    (image, build_logs) = docker_client.images.build(
        path=docker_build_path,
        tag=f"{ecr_image_repo}:{image_tag}",
        cache_from=[f"{ecr_image_repo}:latest"],
        buildargs={"BUILDKIT_INLINE_CACHE": 1} 
        # labels={
        #     "git-commit": commit_hash,
        #     "build-url": os.getenv("CODEBUILD_SOURCE_REPO_URL", "NA"),
        # },
        # buildargs={"artifactory_token": ARTIFACTORY_TOKEN},
    )
    docker_client.images.push(
        repository=ecr_image_repo,
        tag=f"{ecr_image_repo}:{image_tag}",
        auth_config={
            "username": ecr_client.ecr_username,
            "password": ecr_client.ecr_password,
        },
    )
    docker_client.images.push(
        repository=ecr_image_repo,
        tag=f"{ecr_image_repo}:latest",
        auth_config={
            "username": ecr_client.ecr_username,
            "password": ecr_client.ecr_password,
        },
    )

    for chunk in build_logs:
        if "stream" in chunk:
            for line in chunk["stream"].splitlines():
                LOGGER.debug(line)

    LOGGER.info(
        f"End Docker build for image {ecr_image_repo}:{image_tag} at {time.ctime()}."
    )

    return ecr_image_repo, image_tag


version_hashed="111"
docker_build_path="docker_build_path1/"
ecr_image_repo, image_tag = _build_docker_image(
    sensor, version_hashed, docker_build_path
)
