"""Tests for docker-compose.yml configuration."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

COMPOSE_PATH = Path(__file__).resolve().parents[2] / "docker-compose.yml"


def _load_compose() -> dict:
    with open(COMPOSE_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture()
def compose() -> dict:
    return _load_compose()


@pytest.fixture()
def services(compose: dict) -> dict:
    return compose["services"]


class TestDockerComposeServices:
    def test_compose_file_exists(self) -> None:
        assert COMPOSE_PATH.exists(), f"{COMPOSE_PATH} does not exist"

    def test_compose_is_valid_yaml(self, compose: dict) -> None:
        assert "services" in compose

    def test_app_service_defined(self, services: dict) -> None:
        assert "app" in services

    def test_db_service_defined(self, services: dict) -> None:
        assert "db" in services

    def test_redis_service_defined(self, services: dict) -> None:
        assert "redis" in services

    def test_worker_service_defined(self, services: dict) -> None:
        assert "worker" in services

    def test_beat_service_defined(self, services: dict) -> None:
        assert "beat" in services

    def test_all_five_services_present(self, services: dict) -> None:
        expected = {"app", "db", "redis", "worker", "beat"}
        assert set(services.keys()) == expected


class TestDockerComposeHealthchecks:
    @staticmethod
    def _has_healthcheck(service: dict) -> bool:
        return "healthcheck" in service and "test" in service["healthcheck"]

    def test_db_has_healthcheck(self, services: dict) -> None:
        assert self._has_healthcheck(services["db"])

    def test_redis_has_healthcheck(self, services: dict) -> None:
        assert self._has_healthcheck(services["redis"])

    def test_worker_has_healthcheck(self, services: dict) -> None:
        assert self._has_healthcheck(services["worker"])

    def test_beat_has_healthcheck(self, services: dict) -> None:
        assert self._has_healthcheck(services["beat"])


class TestDockerComposeDependencies:
    def test_app_depends_on_db(self, services: dict) -> None:
        deps = services["app"].get("depends_on", {})
        assert "db" in deps

    def test_app_depends_on_redis(self, services: dict) -> None:
        deps = services["app"].get("depends_on", {})
        assert "redis" in deps

    def test_worker_depends_on_redis(self, services: dict) -> None:
        deps = services["worker"].get("depends_on", {})
        assert "redis" in deps

    def test_beat_depends_on_redis(self, services: dict) -> None:
        deps = services["beat"].get("depends_on", {})
        assert "redis" in deps

    def test_app_depends_on_healthy_db(self, services: dict) -> None:
        db_dep = services["app"]["depends_on"]["db"]
        assert db_dep.get("condition") == "service_healthy"

    def test_app_depends_on_healthy_redis(self, services: dict) -> None:
        redis_dep = services["app"]["depends_on"]["redis"]
        assert redis_dep.get("condition") == "service_healthy"


class TestDockerComposeVolumes:
    def test_postgres_data_volume_defined(self, compose: dict) -> None:
        volumes = compose.get("volumes", {})
        assert "postgres_data" in volumes

    def test_db_uses_postgres_data_volume(self, services: dict) -> None:
        db_volumes = services["db"].get("volumes", [])
        assert any("postgres_data:" in v for v in db_volumes)


class TestDockerComposeWorkerImage:
    def test_worker_uses_same_build_as_app(self, services: dict) -> None:
        assert "build" in services["worker"]

    def test_beat_uses_same_build_as_app(self, services: dict) -> None:
        assert "build" in services["beat"]
