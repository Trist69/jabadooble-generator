"""Tests for library CRUD and symbol management (in-memory via temp dir)."""

import os
import tempfile
import pytest

# Redirect storage to a temp dir so tests don't touch /app/data
@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    # Clear module-level cache in storage
    import app.core.storage as store
    store._locks.clear()
    yield


from app.models.library import LibraryCreate, SymbolCreate
from app.services import library_service


def test_create_and_retrieve_library():
    lib = library_service.create_library(LibraryCreate(name="HP", theme="harry-potter"))
    assert lib.name == "HP"
    fetched = library_service.get_library(str(lib.id))
    assert fetched is not None
    assert fetched.id == lib.id


def test_list_libraries():
    library_service.create_library(LibraryCreate(name="A", theme="a"))
    library_service.create_library(LibraryCreate(name="B", theme="b"))
    libs = library_service.list_libraries()
    assert len(libs) == 2


def test_delete_library():
    lib = library_service.create_library(LibraryCreate(name="Del", theme="d"))
    assert library_service.delete_library(str(lib.id))
    assert library_service.get_library(str(lib.id)) is None


def test_add_and_remove_symbol():
    lib = library_service.create_library(LibraryCreate(name="Sym", theme="s"))
    sym = library_service.add_symbol(str(lib.id), SymbolCreate(label="Cat", url="http://x.com/cat.png"))
    assert sym is not None
    assert sym.label == "Cat"
    fetched = library_service.get_library(str(lib.id))
    assert fetched is not None
    assert len(fetched.symbols) == 1
    assert library_service.remove_symbol(str(lib.id), str(sym.id))
    fetched2 = library_service.get_library(str(lib.id))
    assert fetched2 is not None
    assert len(fetched2.symbols) == 0


def test_add_symbols_bulk():
    lib = library_service.create_library(LibraryCreate(name="Bulk", theme="b"))
    symbols = [SymbolCreate(label=f"Sym{i}", url=f"http://x.com/{i}.png") for i in range(5)]
    updated = library_service.add_symbols_bulk(str(lib.id), symbols)
    assert updated is not None
    assert len(updated.symbols) == 5
