"""Tests for canvas repository ownership and mutation isolation."""

import asyncio

import pytest
from src.domain.models.canvas import CanvasState, ClassDefinition
from src.domain.repositories.canvas_repository import CanvasRepository


def test_repository_rejects_cross_workspace_reads_and_writes():
    repository = CanvasRepository()
    canvas = CanvasState(classes=[ClassDefinition(id="user", name="User")])
    asyncio.run(repository.save("workspace-a", "canvas-1", canvas))

    with pytest.raises(PermissionError, match="does not belong"):
        asyncio.run(repository.get("workspace-b", "canvas-1"))

    with pytest.raises(PermissionError, match="does not belong"):
        asyncio.run(repository.save("workspace-b", "canvas-1", CanvasState()))


def test_get_returns_copy_and_failed_mutation_does_not_change_stored_state():
    repository = CanvasRepository()
    asyncio.run(
        repository.save(
            "workspace-a",
            "canvas-1",
            CanvasState(classes=[ClassDefinition(id="user", name="User")]),
        )
    )

    fetched = asyncio.run(repository.get("workspace-a", "canvas-1"))
    fetched.classes[0].name = "MutatedOutsideRepository"

    stored = asyncio.run(repository.get("workspace-a", "canvas-1"))
    assert stored.classes[0].name == "User"


def test_get_all_canvases_filters_by_workspace():
    repository = CanvasRepository()
    asyncio.run(repository.save("workspace-a", "canvas-a", CanvasState()))
    asyncio.run(repository.save("workspace-b", "canvas-b", CanvasState()))

    workspace_a_canvases = asyncio.run(repository.get_all_canvases("workspace-a"))
    workspace_b_canvases = asyncio.run(repository.get_all_canvases("workspace-b"))

    assert len(workspace_a_canvases) == 1
    assert len(workspace_b_canvases) == 1
