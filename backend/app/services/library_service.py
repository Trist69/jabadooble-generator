"""CRUD operations for Libraries and Symbols."""

from __future__ import annotations

from uuid import uuid4

from app.core import storage
from app.models.library import Library, LibraryCreate, Symbol, SymbolCreate

COLLECTION = "libraries"


def create_library(data: LibraryCreate) -> Library:
    lib = Library(id=uuid4(), name=data.name, theme=data.theme, symbols=[])
    storage.put(COLLECTION, str(lib.id), lib.model_dump())
    return lib


def list_libraries() -> list[Library]:
    return [Library(**raw) for raw in storage.all_values(COLLECTION)]


def get_library(library_id: str) -> Library | None:
    raw = storage.get(COLLECTION, library_id)
    return Library(**raw) if raw else None


def delete_library(library_id: str) -> bool:
    return storage.delete(COLLECTION, library_id)


def add_symbol(library_id: str, data: SymbolCreate) -> Symbol | None:
    lib = get_library(library_id)
    if lib is None:
        return None
    symbol = Symbol(id=uuid4(), label=data.label, url=data.url)
    lib.symbols.append(symbol)
    storage.put(COLLECTION, library_id, lib.model_dump())
    return symbol


def add_symbols_bulk(library_id: str, symbols: list[SymbolCreate]) -> Library | None:
    lib = get_library(library_id)
    if lib is None:
        return None
    new_symbols = [Symbol(id=uuid4(), label=s.label, url=s.url) for s in symbols]
    lib.symbols.extend(new_symbols)
    storage.put(COLLECTION, library_id, lib.model_dump())
    return lib


def remove_symbol(library_id: str, symbol_id: str) -> bool:
    lib = get_library(library_id)
    if lib is None:
        return False
    original_count = len(lib.symbols)
    lib.symbols = [s for s in lib.symbols if str(s.id) != symbol_id]
    if len(lib.symbols) == original_count:
        return False
    storage.put(COLLECTION, library_id, lib.model_dump())
    return True


def update_symbol_cartoonized(library_id: str, symbol_id: str, cartoonized_url: str) -> bool:
    lib = get_library(library_id)
    if lib is None:
        return False
    for sym in lib.symbols:
        if str(sym.id) == symbol_id:
            sym.cartoonized_url = cartoonized_url
            sym.cartoonized = True
            storage.put(COLLECTION, library_id, lib.model_dump())
            return True
    return False
