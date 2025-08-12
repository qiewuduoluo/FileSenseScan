# 核心功能模块
from .version_manager import get_version_manager, VersionManager
from .error_monitor import get_error_monitor, ErrorMonitor
from .pdf_utils import extract_pdf_pages

__all__ = [
    'get_version_manager',
    'VersionManager', 
    'get_error_monitor',
    'ErrorMonitor',
    'extract_pdf_pages'
] 