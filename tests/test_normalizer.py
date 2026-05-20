"""Tests for normalizer module."""

import pytest
from unittest.mock import Mock, MagicMock

from src.normalizer import ProcessNormalizer, NormalizationPreset
from src.window_manager import WindowInfo


@pytest.fixture
def mock_window_manager():
    """Создает мок WindowManager для тестов."""
    wm = Mock()
    wm.get_windows = Mock(return_value=[
        WindowInfo(window_id=100, title="Test Window", pid=1234, x=0, y=0, width=800, height=600),
        WindowInfo(window_id=101, title="Another Window", pid=5678, x=100, y=100, width=400, height=300),
    ])
    wm.set_window_position_and_size = Mock(return_value=True)
    return wm


@pytest.fixture
def normalizer(mock_window_manager):
    """Создает ProcessNormalizer с моком WindowManager."""
    return ProcessNormalizer(window_manager=mock_window_manager)


class TestNormalizationPreset:
    """Тесты для NormalizationPreset."""

    def test_create_preset(self):
        """Тест создания пресета."""
        preset = NormalizationPreset(
            id="test_1",
            name="Test Preset",
            process_name="TestApp",
            x=100,
            y=200,
            width=800,
            height=600,
            description="Test description"
        )
        
        assert preset.id == "test_1"
        assert preset.name == "Test Preset"
        assert preset.process_name == "TestApp"
        assert preset.x == 100
        assert preset.y == 200
        assert preset.width == 800
        assert preset.height == 600
        assert preset.description == "Test description"

    def test_preset_default_description(self):
        """Тест значения описания по умолчанию."""
        preset = NormalizationPreset(
            id="test_2",
            name="Test",
            process_name="App",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        assert preset.description == ""

    def test_preset_repr(self):
        """Тест строкового представления."""
        preset = NormalizationPreset(
            id="test_3",
            name="My Preset",
            process_name="MyApp",
            x=0,
            y=0,
            width=100,
            height=100,
        )
        repr_str = repr(preset)
        assert "test_3" in repr_str
        assert "My Preset" in repr_str
        assert "MyApp" in repr_str


class TestProcessNormalizer:
    """Тесты для ProcessNormalizer."""

    def test_normalize_window(self, normalizer, mock_window_manager):
        """Тест нормализации окна."""
        result = normalizer.normalize_window(100, 50, 60, 400, 300)
        
        assert result is True
        mock_window_manager.set_window_position_and_size.assert_called_once_with(
            window_id=100,
            x=50,
            y=60,
            width=400,
            height=300,
        )

    def test_apply_preset_success(self, normalizer, mock_window_manager):
        """Тест успешного применения пресета."""
        preset = NormalizationPreset(
            id="preset_1",
            name="Test",
            process_name="Test Window",
            x=10,
            y=20,
            width=500,
            height=400,
        )
        
        result = normalizer.apply_preset(preset)
        
        assert result is True
        mock_window_manager.set_window_position_and_size.assert_called_once_with(
            window_id=100,
            x=10,
            y=20,
            width=500,
            height=400,
        )

    def test_apply_preset_window_not_found(self, normalizer, mock_window_manager):
        """Тест применения пресета к несуществующему окну."""
        preset = NormalizationPreset(
            id="preset_2",
            name="Test",
            process_name="NonExistent",
            x=10,
            y=20,
            width=500,
            height=400,
        )
        
        result = normalizer.apply_preset(preset)
        
        assert result is False
        mock_window_manager.set_window_position_and_size.assert_not_called()

    def test_find_window_by_process_found(self, normalizer, mock_window_manager):
        """Тест поиска окна - найдено."""
        window = normalizer.find_window_by_process("Test")
        
        assert window is not None
        assert window.window_id == 100
        assert window.title == "Test Window"

    def test_find_window_by_process_not_found(self, normalizer, mock_window_manager):
        """Тест поиска окна - не найдено."""
        window = normalizer.find_window_by_process("NonExistent")
        
        assert window is None

    def test_find_window_by_process_case_insensitive(self, normalizer, mock_window_manager):
        """Тест регистронезависимого поиска."""
        window = normalizer.find_window_by_process("test WINDOW")
        
        assert window is not None
        assert window.window_id == 100

    def test_search_windows_empty_query(self, normalizer, mock_window_manager):
        """Тест поиска с пустым запросом."""
        windows = normalizer.search_windows("")
        
        assert len(windows) == 2
        mock_window_manager.get_windows.assert_called()

    def test_search_windows_with_query(self, normalizer, mock_window_manager):
        """Тест поиска с запросом."""
        windows = normalizer.search_windows("Another")
        
        assert len(windows) == 1
        assert windows[0].title == "Another Window"

    def test_search_windows_no_results(self, normalizer, mock_window_manager):
        """Тест поиска без результатов."""
        windows = normalizer.search_windows("NotFound")
        
        assert len(windows) == 0
