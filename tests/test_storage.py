"""Tests for storage module."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.storage import PresetStorage
from src.normalizer import NormalizationPreset


@pytest.fixture
def temp_storage_path():
    """Создает временный файл для хранения пресетов."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def storage(temp_storage_path):
    """Создает PresetStorage с временным файлом."""
    return PresetStorage(storage_path=temp_storage_path)


class TestPresetStorage:
    """Тесты для PresetStorage."""

    def test_create_empty_storage(self, storage, temp_storage_path):
        """Тест создания пустого хранилища."""
        assert storage.get_all_presets() == []
        assert storage.storage_path == temp_storage_path

    def test_add_preset(self, storage):
        """Тест добавления пресета."""
        preset = storage.add_preset(
            preset_id="test_1",
            name="Test Preset",
            process_name="TestApp",
            x=100,
            y=200,
            width=800,
            height=600,
            description="Test"
        )
        
        assert preset.id == "test_1"
        assert preset.name == "Test Preset"
        assert storage.get_preset("test_1") == preset

    def test_add_preset_persists_to_file(self, storage, temp_storage_path):
        """Тест сохранения пресета в файл."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        # Проверяем, что файл существует и содержит данные
        assert temp_storage_path.exists()
        with open(temp_storage_path, encoding="utf-8") as f:
            data = json.load(f)
        assert "test_1" in data
        assert data["test_1"]["name"] == "Test"

    def test_add_duplicate_preset_raises_error(self, storage):
        """Тест добавления дубликата пресета."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        with pytest.raises(ValueError, match="уже существует"):
            storage.add_preset(
                preset_id="test_1",
                name="Test 2",
                process_name="App2",
                x=0,
                y=0,
                width=100,
                height=100,
            )

    def test_remove_preset_success(self, storage):
        """Тест успешного удаления пресета."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        result = storage.remove_preset("test_1")
        
        assert result is True
        assert storage.get_preset("test_1") is None

    def test_remove_preset_not_found(self, storage):
        """Тест удаления несуществующего пресета."""
        result = storage.remove_preset("nonexistent")
        assert result is False

    def test_update_preset_success(self, storage):
        """Тест успешного обновления пресета."""
        storage.add_preset(
            preset_id="test_1",
            name="Original",
            process_name="OriginalApp",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        updated = storage.update_preset(
            preset_id="test_1",
            name="Updated",
            x=50,
        )
        
        assert updated is not None
        assert updated.name == "Updated"
        assert updated.process_name == "OriginalApp"  # Не изменилось
        assert updated.x == 50
        assert updated.y == 0  # Не изменилось

    def test_update_preset_not_found(self, storage):
        """Тест обновления несуществующего пресета."""
        result = storage.update_preset(
            preset_id="nonexistent",
            name="New Name",
        )
        assert result is None

    def test_get_preset_found(self, storage):
        """Тест получения существующего пресета."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        preset = storage.get_preset("test_1")
        
        assert preset is not None
        assert preset.name == "Test"

    def test_get_preset_not_found(self, storage):
        """Тест получения несуществующего пресета."""
        preset = storage.get_preset("nonexistent")
        assert preset is None

    def test_get_all_presets(self, storage):
        """Тест получения всех пресетов."""
        storage.add_preset(
            preset_id="test_1",
            name="Test 1",
            process_name="App1",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        storage.add_preset(
            preset_id="test_2",
            name="Test 2",
            process_name="App2",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        presets = storage.get_all_presets()
        
        assert len(presets) == 2
        preset_ids = {p.id for p in presets}
        assert "test_1" in preset_ids
        assert "test_2" in preset_ids

    def test_search_presets_empty_query(self, storage):
        """Тест поиска с пустым запросом."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        results = storage.search_presets("")
        
        assert len(results) == 1

    def test_search_presets_by_name(self, storage):
        """Тест поиска по имени."""
        storage.add_preset(
            preset_id="test_1",
            name="Browser Preset",
            process_name="Chrome",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        storage.add_preset(
            preset_id="test_2",
            name="Editor Preset",
            process_name="VSCode",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        results = storage.search_presets("Browser")
        
        assert len(results) == 1
        assert results[0].name == "Browser Preset"

    def test_search_presets_by_process_name(self, storage):
        """Тест поиска по имени процесса."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="Chrome",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        
        results = storage.search_presets("chrome")
        
        assert len(results) == 1
        assert results[0].process_name == "Chrome"

    def test_search_presets_by_description(self, storage):
        """Тест поиска по описанию."""
        storage.add_preset(
            preset_id="test_1",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
            description="Main workspace preset"
        )
        
        results = storage.search_presets("workspace")
        
        assert len(results) == 1
        assert results[0].description == "Main workspace preset"

    def test_load_from_existing_file(self, temp_storage_path):
        """Тест загрузки из существующего файла."""
        # Создаем файл с данными
        data = {
            "existing_preset": {
                "id": "existing_preset",
                "name": "Existing",
                "process_name": "ExistingApp",
                "x": 10,
                "y": 20,
                "width": 300,
                "height": 200,
                "description": "Loaded from file"
            }
        }
        with open(temp_storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        # Создаем хранилище с загрузкой из файла
        storage = PresetStorage(storage_path=temp_storage_path)
        
        preset = storage.get_preset("existing_preset")
        assert preset is not None
        assert preset.name == "Existing"
        assert preset.x == 10

    def test_load_from_invalid_file(self, temp_storage_path):
        """Тест загрузки из некорректного файла."""
        with open(temp_storage_path, 'w', encoding='utf-8') as f:
            f.write("invalid json {")
        
        # Не должно вызывать исключение
        storage = PresetStorage(storage_path=temp_storage_path)
        assert storage.get_all_presets() == []

    def test_load_from_nonexistent_file(self, temp_storage_path):
        """Тест загрузки из несуществующего файла."""
        # Удаляем файл если он есть
        temp_storage_path.unlink(missing_ok=True)
        
        # Не должно вызывать исключение
        storage = PresetStorage(storage_path=temp_storage_path)
        assert storage.get_all_presets() == []
