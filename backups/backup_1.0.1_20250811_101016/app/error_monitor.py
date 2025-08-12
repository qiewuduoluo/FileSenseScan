"""
FileSenseScan 错误监控和自动恢复系统
监控AI处理代码的错误，自动回滚到稳定版本
"""

import os
import sys
import time
import signal
import threading
import traceback
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import psutil
import json
import queue
import subprocess

from version_manager import get_version_manager, VersionManager


class ErrorMonitor:
    """错误监控器主类"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.version_manager = get_version_manager(project_root)
        
        # 错误监控设置
        self.monitoring = False
        self.error_threshold = 3  # 连续错误次数阈值
        self.error_window = 300  # 错误窗口时间（秒）
        self.auto_rollback = True  # 自动回滚
        self.emergency_mode = False  # 紧急模式
        
        # 错误记录
        self.error_history = []
        self.error_counts = {}  # 按错误类型统计
        self.last_error_time = None
        
        # 监控线程
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        # 错误处理器队列
        self.error_queue = queue.Queue()
        self.error_handlers = {}
        
        # 设置日志
        self._setup_logging()
        
        # 注册信号处理器
        self._setup_signal_handlers()
        
        # 注册默认错误处理器
        self._register_default_handlers()
        
        self.logger.info("错误监控系统初始化完成")
    
    def _setup_logging(self):
        """设置日志系统"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"error_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            if hasattr(signal, 'SIGBREAK'):  # Windows
                signal.signal(signal.SIGBREAK, self._signal_handler)
        except Exception as e:
            self.logger.warning(f"设置信号处理器失败: {e}")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，正在停止监控...")
        self.stop_monitoring()
        sys.exit(0)
    
    def _register_default_handlers(self):
        """注册默认错误处理器"""
        # 注册AI处理错误处理器
        self.register_error_handler("ai_processing_error", self._handle_ai_error)
        
        # 注册系统崩溃处理器
        self.register_error_handler("system_crash", self._handle_system_crash)
        
        # 注册内存泄漏处理器
        self.register_error_handler("memory_leak", self._handle_memory_leak)
        
        # 注册文件损坏处理器
        self.register_error_handler("file_corruption", self._handle_file_corruption)
    
    def register_error_handler(self, error_type: str, handler: Callable):
        """注册错误处理器"""
        self.error_handlers[error_type] = handler
        self.logger.info(f"注册错误处理器: {error_type}")
    
    def start_monitoring(self):
        """开始错误监控"""
        if self.monitoring:
            self.logger.warning("错误监控已经在运行")
            return
        
        self.monitoring = True
        self.stop_event.clear()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # 启动错误处理线程
        self.error_handler_thread = threading.Thread(target=self._error_handler_loop, daemon=True)
        self.error_handler_thread.start()
        
        self.logger.info("错误监控已启动")
    
    def stop_monitoring(self):
        """停止错误监控"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        if hasattr(self, 'error_handler_thread') and self.error_handler_thread.is_alive():
            self.error_handler_thread.join(timeout=5)
        
        self.logger.info("错误监控已停止")
    
    def _monitor_loop(self):
        """监控主循环"""
        while not self.stop_event.is_set():
            try:
                # 检查系统状态
                self._check_system_health()
                
                # 检查进程状态
                self._check_process_health()
                
                # 检查文件完整性
                self._check_file_integrity()
                
                # 检查内存使用
                self._check_memory_usage()
                
                # 等待下一次检查
                time.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(30)  # 出错后等待30秒
    
    def _error_handler_loop(self):
        """错误处理循环"""
        while not self.stop_event.is_set():
            try:
                # 从队列获取错误
                try:
                    error_info = self.error_queue.get(timeout=1)
                    self._process_error(error_info)
                except queue.Empty:
                    continue
                    
            except Exception as e:
                self.logger.error(f"错误处理循环错误: {e}")
                time.sleep(5)
    
    def _check_system_health(self):
        """检查系统健康状态"""
        try:
            # 检查CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                self._record_error("high_cpu_usage", f"CPU使用率过高: {cpu_percent}%")
            
            # 检查磁盘空间
            disk_usage = psutil.disk_usage(self.project_root)
            if disk_usage.percent > 90:
                self._record_error("low_disk_space", f"磁盘空间不足: {disk_usage.percent}%")
                
        except Exception as e:
            self.logger.error(f"检查系统健康状态失败: {e}")
    
    def _check_process_health(self):
        """检查进程健康状态"""
        try:
            current_pid = os.getpid()
            current_process = psutil.Process(current_pid)
            
            # 检查进程状态
            if current_process.status() == psutil.STATUS_ZOMBIE:
                self._record_error("zombie_process", "进程处于僵尸状态")
            
            # 检查子进程
            children = current_process.children(recursive=True)
            for child in children:
                if child.status() == psutil.STATUS_ZOMBIE:
                    self._record_error("zombie_child_process", f"子进程 {child.pid} 处于僵尸状态")
                    
        except Exception as e:
            self.logger.error(f"检查进程健康状态失败: {e}")
    
    def _check_file_integrity(self):
        """检查文件完整性"""
        try:
            # 检查关键文件是否存在
            critical_files = [
                "app/gui_app_modern.py",
                "app/version_manager.py",
                "requirements.txt",
                "README.md"
            ]
            
            for file_path in critical_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    self._record_error("critical_file_missing", f"关键文件缺失: {file_path}")
                elif full_path.stat().st_size == 0:
                    self._record_error("file_empty", f"文件为空: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"检查文件完整性失败: {e}")
    
    def _check_memory_usage(self):
        """检查内存使用情况"""
        try:
            current_process = psutil.Process(os.getpid())
            memory_info = current_process.memory_info()
            
            # 检查内存使用量
            memory_mb = memory_info.rss / 1024 / 1024
            if memory_mb > 1000:  # 超过1GB
                self._record_error("high_memory_usage", f"内存使用量过高: {memory_mb:.1f}MB")
                
        except Exception as e:
            self.logger.error(f"检查内存使用情况失败: {e}")
    
    def record_error(self, error_type: str, error_message: str, 
                    error_details: Dict = None, severity: str = "medium"):
        """记录错误"""
        error_info = {
            "type": error_type,
            "message": error_message,
            "details": error_details or {},
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "stack_trace": traceback.format_exc(),
            "process_id": os.getpid(),
            "thread_id": threading.current_thread().ident
        }
        
        # 添加到错误历史
        self.error_history.append(error_info)
        
        # 更新错误计数
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # 记录到日志
        self.logger.error(f"错误记录: {error_type} - {error_message}")
        
        # 添加到处理队列
        self.error_queue.put(error_info)
        
        # 检查是否需要触发紧急模式
        self._check_emergency_mode()
        
        return error_info
    
    def _record_error(self, error_type: str, error_message: str):
        """内部错误记录方法"""
        self.record_error(error_type, error_message, severity="low")
    
    def _check_emergency_mode(self):
        """检查是否需要进入紧急模式"""
        if self.emergency_mode:
            return
        
        # 检查最近错误频率
        recent_errors = [
            error for error in self.error_history 
            if (datetime.now() - datetime.fromisoformat(error["timestamp"])).seconds < self.error_window
        ]
        
        if len(recent_errors) >= self.error_threshold:
            self.logger.warning(f"错误频率过高，进入紧急模式")
            self.emergency_mode = True
            self._trigger_emergency_response()
    
    def _trigger_emergency_response(self):
        """触发紧急响应"""
        try:
            self.logger.warning("执行紧急响应...")
            
            # 尝试自动回滚
            if self.auto_rollback:
                if self.version_manager.emergency_rollback():
                    self.logger.info("紧急回滚成功")
                    self.emergency_mode = False
                else:
                    self.logger.error("紧急回滚失败")
            
            # 如果回滚失败，尝试重启应用
            if self.emergency_mode:
                self._restart_application()
                
        except Exception as e:
            self.logger.error(f"紧急响应失败: {e}")
    
    def _restart_application(self):
        """重启应用程序"""
        try:
            self.logger.info("尝试重启应用程序...")
            
            # 获取当前脚本路径
            script_path = sys.argv[0]
            if script_path.endswith('.py'):
                # Python脚本
                subprocess.Popen([sys.executable, script_path] + sys.argv[1:])
            else:
                # 可执行文件
                subprocess.Popen([script_path] + sys.argv[1:])
            
            # 退出当前进程
            sys.exit(0)
            
        except Exception as e:
            self.logger.error(f"重启应用程序失败: {e}")
    
    def _process_error(self, error_info: Dict):
        """处理错误"""
        try:
            error_type = error_info["type"]
            
            # 查找对应的处理器
            if error_type in self.error_handlers:
                handler = self.error_handlers[error_type]
                handler(error_info)
            else:
                # 使用默认处理器
                self._handle_generic_error(error_info)
                
        except Exception as e:
            self.logger.error(f"处理错误失败: {e}")
    
    def _handle_ai_error(self, error_info: Dict):
        """处理AI处理错误"""
        try:
            self.logger.warning("检测到AI处理错误，正在评估影响...")
            
            # 检查错误严重程度
            severity = error_info.get("severity", "medium")
            
            if severity in ["high", "critical"]:
                # 严重错误，立即回滚
                self.logger.warning("AI错误严重，执行紧急回滚")
                if self.version_manager.emergency_rollback():
                    self.logger.info("AI错误回滚成功")
                else:
                    self.logger.error("AI错误回滚失败")
            else:
                # 轻微错误，记录并继续
                self.logger.info("AI错误轻微，继续运行")
                
        except Exception as e:
            self.logger.error(f"处理AI错误失败: {e}")
    
    def _handle_system_crash(self, error_info: Dict):
        """处理系统崩溃"""
        try:
            self.logger.error("检测到系统崩溃，正在恢复...")
            
            # 尝试回滚到稳定版本
            if self.version_manager.rollback_to_stable():
                self.logger.info("系统崩溃恢复成功")
            else:
                self.logger.error("系统崩溃恢复失败")
                
        except Exception as e:
            self.logger.error(f"处理系统崩溃失败: {e}")
    
    def _handle_memory_leak(self, error_info: Dict):
        """处理内存泄漏"""
        try:
            self.logger.warning("检测到内存泄漏，正在清理...")
            
            # 强制垃圾回收
            import gc
            gc.collect()
            
            # 检查内存使用情况
            current_process = psutil.Process(os.getpid())
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            self.logger.info(f"内存清理完成，当前使用: {memory_mb:.1f}MB")
            
        except Exception as e:
            self.logger.error(f"处理内存泄漏失败: {e}")
    
    def _handle_file_corruption(self, error_info: Dict):
        """处理文件损坏"""
        try:
            self.logger.error("检测到文件损坏，正在恢复...")
            
            # 尝试从备份恢复
            if self.version_manager.rollback_to_stable():
                self.logger.info("文件损坏恢复成功")
            else:
                self.logger.error("文件损坏恢复失败")
                
        except Exception as e:
            self.logger.error(f"处理文件损坏失败: {e}")
    
    def _handle_generic_error(self, error_info: Dict):
        """处理通用错误"""
        try:
            self.logger.info(f"处理通用错误: {error_info['type']}")
            
            # 根据错误类型和严重程度决定处理方式
            severity = error_info.get("severity", "medium")
            
            if severity == "critical":
                # 严重错误，尝试回滚
                self.logger.warning("严重错误，尝试回滚")
                self.version_manager.rollback_to_stable()
            elif severity == "high":
                # 高严重性错误，记录并监控
                self.logger.warning("高严重性错误，继续监控")
            else:
                # 低严重性错误，仅记录
                self.logger.info("低严重性错误，已记录")
                
        except Exception as e:
            self.logger.error(f"处理通用错误失败: {e}")
    
    def get_error_summary(self) -> Dict:
        """获取错误摘要"""
        try:
            summary = {
                "total_errors": len(self.error_history),
                "error_types": self.error_counts,
                "recent_errors": len([
                    error for error in self.error_history 
                    if (datetime.now() - datetime.fromisoformat(error["timestamp"])).seconds < 3600
                ]),
                "emergency_mode": self.emergency_mode,
                "monitoring_status": self.monitoring,
                "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"获取错误摘要失败: {e}")
            return {"error": str(e)}
    
    def clear_error_history(self):
        """清除错误历史"""
        try:
            self.error_history.clear()
            self.error_counts.clear()
            self.last_error_time = None
            self.logger.info("错误历史已清除")
        except Exception as e:
            self.logger.error(f"清除错误历史失败: {e}")
    
    def set_error_threshold(self, threshold: int):
        """设置错误阈值"""
        self.error_threshold = max(1, threshold)
        self.logger.info(f"错误阈值设置为: {self.error_threshold}")
    
    def set_auto_rollback(self, enabled: bool):
        """设置自动回滚"""
        self.auto_rollback = enabled
        self.logger.info(f"自动回滚设置为: {'启用' if enabled else '禁用'}")


# 全局错误监控器实例
_error_monitor = None

def get_error_monitor(project_root: str = None) -> ErrorMonitor:
    """获取全局错误监控器实例"""
    global _error_monitor
    if _error_monitor is None:
        _error_monitor = ErrorMonitor(project_root)
    return _error_monitor


def monitor_ai_processing(func: Callable) -> Callable:
    """AI处理监控装饰器"""
    def wrapper(*args, **kwargs):
        error_monitor = get_error_monitor()
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 执行AI处理
            result = func(*args, **kwargs)
            
            # 记录处理时间
            processing_time = time.time() - start_time
            
            # 检查处理时间是否过长
            if processing_time > 300:  # 超过5分钟
                error_monitor.record_error(
                    "ai_processing_slow",
                    f"AI处理时间过长: {processing_time:.1f}秒",
                    {"processing_time": processing_time},
                    "medium"
                )
            
            return result
            
        except Exception as e:
            # 记录AI处理错误
            error_monitor.record_error(
                "ai_processing_error",
                f"AI处理失败: {str(e)}",
                {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)},
                "high"
            )
            raise
    
    return wrapper


if __name__ == "__main__":
    # 测试代码
    monitor = ErrorMonitor()
    
    # 启动监控
    monitor.start_monitoring()
    
    try:
        # 模拟运行
        time.sleep(30)
    except KeyboardInterrupt:
        print("正在停止监控...")
    finally:
        monitor.stop_monitoring()
        
        # 显示错误摘要
        print("错误摘要:", json.dumps(monitor.get_error_summary(), indent=2, ensure_ascii=False)) 