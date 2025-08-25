import logging
import sys
from pathlib import Path


class LoggerService:
    """Simple logger service with console + file output."""

    _logger: logging.Logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger

    @classmethod
    def _setup_logger(cls):
        cls._logger = logging.getLogger("RAGPipeline")
        cls._logger.setLevel(logging.INFO)

        # Remove duplicate handlers
        cls._logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        cls._logger.addHandler(console_handler)

        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "rag_pipeline.log")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        cls._logger.addHandler(file_handler)

    # --- Logging shortcuts ---
    @classmethod
    def debug(cls, msg: str): cls.get_logger().debug(msg)
    @classmethod
    def info(cls, msg: str): cls.get_logger().info(msg)
    @classmethod
    def success(cls, msg: str): cls.get_logger().info(f"[SUCCESS] {msg}")
    @classmethod
    def warning(cls, msg: str): cls.get_logger().warning(msg)
    @classmethod
    def error(cls, msg: str): cls.get_logger().error(msg)
    @classmethod
    def critical(cls, msg: str): cls.get_logger().critical(msg)

    @classmethod
    def section(cls, title: str):
        sep = "=" * 50
        cls.info(f"\n{sep}\n{title}\n{sep}")

    @classmethod
    def progress(cls, current: int, total: int, desc: str = ""):
        pct = (current / total) * 100 if total else 0
        bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
        end = "\r" if current < total else "\n"
        print(f"{desc} [{bar}] {current}/{total} ({pct:.1f}%)", end=end)


# Global instance
logger = LoggerService
