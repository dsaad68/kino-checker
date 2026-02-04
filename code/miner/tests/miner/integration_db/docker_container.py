# %%
import enum

import docker
from loguru import logger

# %%


class STATUS(enum.Enum):
    RUNNING = "running"


class Docker:
    def __init__(self):
        self.client = self._get_client()

    def is_container_running(self, container_name: str) -> bool:
        """Verify the status of a container by it's name

        :param container_name: the name of the container
        :return: boolean
        """

        if not self.client:
            logger.warning("Docker client not initialized")
            return False

        try:
            container = self.client.containers.get(container_name)
            return container.status == STATUS.RUNNING.value
        except docker.errors.NotFound:
            logger.info(f"Container '{container_name}' not found.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    def is_image_running(self, image_name: str) -> bool:
        try:
            container_list = self.containers_with_image(image_name)
            return any(self.is_container_running(container) for container in container_list)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    def containers_with_image(self, image_name: str) -> list[str]:
        if not self.client:
            logger.warning("Docker client not initialized")
            return []

        result = []
        try:
            # Use the low-level API to avoid issues with stale container references
            containers = self.client.api.containers(all=True)
            for c in containers:
                try:
                    # Get image from the list API (doesn't require fetching container details)
                    container_image = c.get("Image", "")
                    if container_image == image_name:
                        # Get container name from Names field
                        names = c.get("Names", [])
                        if names:
                            # Remove leading slash from name
                            result.append(names[0].lstrip("/"))
                except Exception as e:
                    # Skip containers that cause errors
                    logger.debug(f"Skipping container due to error: {e}")
                    continue
        except Exception as e:
            logger.error(f"Unexpected error listing containers: {e}")

        return result

    def _get_client(self) -> docker.client.DockerClient:
        try:
            # Connect to Docker using the default socket or the configuration specified in the environment
            # For Windows, it will automatically use the named pipe by default.
            # For Linux, it uses the Unix socket by default.
            client = docker.from_env()
            client.ping()  # Validates if Docker daemon is responsive
            return client
        except Exception as e:
            logger.warning("Docker daemon is not responsive.")
            logger.error(f"Error: {e}")
            return None


if __name__ == "__main__":
    dckr = Docker()
    container_name = "postgres:16-bookworm"
    result = dckr.is_image_running(container_name)
    logger.info("%s", result)
