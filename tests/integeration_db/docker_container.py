import enum
import logging
import docker

class STATUS(enum.Enum):
    RUNNING = "running"

class Docker():

    def __init__(self):
        self.client = self._get_client()

    def is_container_running(self, container_name: str) -> bool:
        """Verify the status of a container by it's name

        :param container_name: the name of the container
        :return: boolean
        """

        if not self.client:
            logging.warning("Docker client not initialized")
            return False

        try:
            container = self.client.containers.get(container_name)
            return container.status == STATUS.RUNNING.value
        except docker.errors.NotFound:
            logging.info(f"Container '{container_name}' not found.")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False

    def is_image_running(self, image_name: str) -> bool:
        try:
            container_list = self.containers_with_image(image_name)
            return any(self.is_container_running(container) for container in container_list)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False

    def containers_with_image(self, image_name: str) -> list[str]:

        if not self.client:
            logging.warning("Docker client not initialized")
            return []

        try:
            # get all containers including the ones not running
            containers = self.client.containers.list(all=True)
            return [ container.name for container in containers if container.attrs['Config']['Image'] == image_name ]
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []

    def _get_client(self) -> docker.client.DockerClient:
        try:
            # Connect to Docker using the default socket or the configuration specified in the environment
            # For Windows, it will automatically use the named pipe by default.
            # For Linux, it uses the Unix socket by default.
            client = docker.from_env()
            client.ping() # Validates if Docker daemon is responsive
            return client
        except Exception as e:
            logging.warning("Docker daemon is not responsive.")
            logging.error(f"Error: {e}")
            return None

if __name__ == "__main__":
    dckr = Docker()
    container_name = "postgres:16-bookworm"
    result = dckr.is_image_running(container_name)
    print(result)
