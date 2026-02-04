import enum
import logging

import docker


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
        """True if any running container uses the given image (name:tag). Uses list API only."""
        try:
            return any(
                self._container_list_image_matches(c, image_name) and (c.get("State") == STATUS.RUNNING.value)
                for c in (self.client.api.containers(all=True) if self.client else [])
            )
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False

    def _container_list_image_matches(self, list_item: dict, image_name: str) -> bool:
        """Return True if a container list item (from API) uses the given image."""
        # List API returns "Image" as name:tag (e.g. postgres:alpine3.18) or image ID
        list_image = (list_item.get("Image") or "").strip()
        if list_image == image_name:
            return True
        # If Image is a sha, resolve tags (skip if we can't to avoid 404s on stale refs)
        if list_image.startswith("sha256:") and self.client:
            try:
                img = self.client.images.get(list_image)
                return image_name in (getattr(img, "tags", None) or [])
            except Exception:
                pass
        return False

    def containers_with_image(self, image_name: str) -> list[str]:
        if not self.client:
            logging.warning("Docker client not initialized")
            return []

        try:
            # Use low-level API to avoid container.get() 404s on stale/other-context containers
            raw = self.client.api.containers(all=True)
            return [
                (c["Names"][0].lstrip("/") if c.get("Names") else c["Id"][:12])
                for c in raw
                if self._container_list_image_matches(c, image_name)
            ]
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []

    def _get_client(self) -> docker.client.DockerClient:
        try:
            # Connect to Docker using the default socket or the configuration specified in the environment
            # For Windows, it will automatically use the named pipe by default.
            # For Linux, it uses the Unix socket by default.
            client = docker.from_env()
            client.ping()  # Validates if Docker daemon is responsive
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
