"""Модуль UI для приложения Automizer."""

from src.ui.app import MainWindow, run_app

# Алиасы для обратной совместимости
NormalizerApp = MainWindow
main = run_app

__all__ = ["MainWindow", "run_app", "NormalizerApp", "main"]
