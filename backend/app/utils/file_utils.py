# backend/app/utils/file_utils.py
"""
📁 أدوات التعامل مع الملفات - File Utilities

توفر وظائف مساعدة للتعامل مع الملفات والمجلدات
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import mimetypes
import magic

from app.core.config import settings
from app.utils.logger import logger


class FileUtils:
    """
    أدوات التعامل مع الملفات
    
    توفر وظائف مساعدة للتعامل مع الملفات والمجلدات
    """
    
    # الامتدادات المسموحة
    ALLOWED_EXTENSIONS = {
        '.txt': 'text/plain',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.rtf': 'application/rtf',
        '.md': 'text/markdown',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.html': 'text/html'
    }
    
    # أحجام الملفات بالبايت
    FILE_SIZE_UNITS = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        الحصول على امتداد الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            امتداد الملف
        """
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_file_name(file_path: str) -> str:
        """
        الحصول على اسم الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            اسم الملف
        """
        return Path(file_path).name
    
    @staticmethod
    def get_file_name_without_extension(file_path: str) -> str:
        """
        الحصول على اسم الملف بدون امتداد
        
        Args:
            file_path: مسار الملف
            
        Returns:
            اسم الملف بدون امتداد
        """
        return Path(file_path).stem
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        الحصول على حجم الملف بالبايت
        
        Args:
            file_path: مسار الملف
            
        Returns:
            حجم الملف بالبايت
        """
        try:
            return Path(file_path).stat().st_size
        except Exception as e:
            logger.error(f"❌ Error getting file size: {str(e)}")
            return 0
    
    @staticmethod
    def get_file_size_formatted(file_path: str) -> str:
        """
        الحصول على حجم الملف بصيغة مقروءة
        
        Args:
            file_path: مسار الملف
            
        Returns:
            حجم الملف بصيغة مقروءة
        """
        size = FileUtils.get_file_size(file_path)
        return FileUtils.format_file_size(size)
    
    @staticmethod
    def format_file_size(size: int) -> str:
        """
        تنسيق حجم الملف بصيغة مقروءة
        
        Args:
            size: الحجم بالبايت
            
        Returns:
            حجم الملف بصيغة مقروءة
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @staticmethod
    def is_file_allowed(file_path: str) -> bool:
        """
        التحقق من أن الملف مسموح به
        
        Args:
            file_path: مسار الملف
            
        Returns:
            هل الملف مسموح به
        """
        extension = FileUtils.get_file_extension(file_path)
        return extension in FileUtils.ALLOWED_EXTENSIONS
    
    @staticmethod
    def is_file_size_allowed(file_path: str, max_size: Optional[int] = None) -> bool:
        """
        التحقق من أن حجم الملف مسموح به
        
        Args:
            file_path: مسار الملف
            max_size: الحد الأقصى للحجم بالبايت
            
        Returns:
            هل حجم الملف مسموح به
        """
        max_size = max_size or settings.MAX_FILE_SIZE
        size = FileUtils.get_file_size(file_path)
        return size <= max_size
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """
        الحصول على نوع MIME للملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            نوع MIME
        """
        try:
            # محاولة استخدام python-magic
            mime = magic.from_file(file_path, mime=True)
            if mime:
                return mime
        except:
            pass
        
        # استخدام mimetypes كبديل
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """
        حساب Hash للملف
        
        Args:
            file_path: مسار الملف
            algorithm: خوارزمية التشفير
            
        Returns:
            Hash الملف
        """
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"❌ Error calculating hash: {str(e)}")
            return ""
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        الحصول على معلومات الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            معلومات الملف
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                "filename": path.name,
                "file_path": str(path),
                "extension": path.suffix.lower(),
                "size": stat.st_size,
                "size_formatted": FileUtils.format_file_size(stat.st_size),
                "mime_type": FileUtils.get_mime_type(str(path)),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_at": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
                "is_allowed": FileUtils.is_file_allowed(str(path)),
                "hash": FileUtils.get_file_hash(str(path))
            }
        except Exception as e:
            logger.error(f"❌ Error getting file info: {str(e)}")
            return {}
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        قراءة ملف نصي
        
        Args:
            file_path: مسار الملف
            encoding: ترميز الملف
            
        Returns:
            محتوى الملف
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Error reading file: {str(e)}")
            return None
    
    @staticmethod
    def write_text_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        كتابة ملف نصي
        
        Args:
            file_path: مسار الملف
            content: المحتوى
            encoding: ترميز الملف
            
        Returns:
            نجاح الكتابة
        """
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"❌ Error writing file: {str(e)}")
            return False
    
    @staticmethod
    def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
        """
        قراءة ملف JSON
        
        Args:
            file_path: مسار الملف
            
        Returns:
            محتوى الملف
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error reading JSON file: {str(e)}")
            return None
    
    @staticmethod
    def write_json_file(file_path: str, data: Dict[str, Any], pretty: bool = True) -> bool:
        """
        كتابة ملف JSON
        
        Args:
            file_path: مسار الملف
            data: البيانات
            pretty: تنسيق جميل
            
        Returns:
            نجاح الكتابة
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ Error writing JSON file: {str(e)}")
            return False
    
    @staticmethod
    def create_directory(directory_path: str) -> bool:
        """
        إنشاء مجلد
        
        Args:
            directory_path: مسار المجلد
            
        Returns:
            نجاح الإنشاء
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"❌ Error creating directory: {str(e)}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        حذف ملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            نجاح الحذف
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting file: {str(e)}")
            return False
    
    @staticmethod
    def delete_directory(directory_path: str) -> bool:
        """
        حذف مجلد
        
        Args:
            directory_path: مسار المجلد
            
        Returns:
            نجاح الحذف
        """
        try:
            path = Path(directory_path)
            if path.exists():
                shutil.rmtree(path)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting directory: {str(e)}")
            return False
    
    @staticmethod
    def copy_file(source_path: str, destination_path: str) -> bool:
        """
        نسخ ملف
        
        Args:
            source_path: مسار المصدر
            destination_path: مسار الوجهة
            
        Returns:
            نجاح النسخ
        """
        try:
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)
            return True
        except Exception as e:
            logger.error(f"❌ Error copying file: {str(e)}")
            return False
    
    @staticmethod
    def move_file(source_path: str, destination_path: str) -> bool:
        """
        نقل ملف
        
        Args:
            source_path: مسار المصدر
            destination_path: مسار الوجهة
            
        Returns:
            نجاح النقل
        """
        try:
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source_path, destination_path)
            return True
        except Exception as e:
            logger.error(f"❌ Error moving file: {str(e)}")
            return False
    
    @staticmethod
    def list_files(directory_path: str, extensions: Optional[List[str]] = None) -> List[str]:
        """
        الحصول على قائمة الملفات في مجلد
        
        Args:
            directory_path: مسار المجلد
            extensions: قائمة الامتدادات المطلوبة
            
        Returns:
            قائمة مسارات الملفات
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                return []
            
            files = []
            for file_path in path.iterdir():
                if file_path.is_file():
                    if extensions:
                        if file_path.suffix.lower() in extensions:
                            files.append(str(file_path))
                    else:
                        files.append(str(file_path))
            return files
        except Exception as e:
            logger.error(f"❌ Error listing files: {str(e)}")
            return []
    
    @staticmethod
    def list_directories(directory_path: str) -> List[str]:
        """
        الحصول على قائمة المجلدات في مجلد
        
        Args:
            directory_path: مسار المجلد
            
        Returns:
            قائمة مسارات المجلدات
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                return []
            
            return [
                str(dir_path) for dir_path in path.iterdir()
                if dir_path.is_dir()
            ]
        except Exception as e:
            logger.error(f"❌ Error listing directories: {str(e)}")
            return []
    
    @staticmethod
    def get_available_space(directory_path: str) -> int:
        """
        الحصول على المساحة المتاحة في القرص
        
        Args:
            directory_path: مسار المجلد
            
        Returns:
            المساحة المتاحة بالبايت
        """
        try:
            import shutil
            _, _, free = shutil.disk_usage(directory_path)
            return free
        except Exception as e:
            logger.error(f"❌ Error getting available space: {str(e)}")
            return 0
    
    @staticmethod
    def get_available_space_formatted(directory_path: str) -> str:
        """
        الحصول على المساحة المتاحة بصيغة مقروءة
        
        Args:
            directory_path: مسار المجلد
            
        Returns:
            المساحة المتاحة بصيغة مقروءة
        """
        free = FileUtils.get_available_space(directory_path)
        return FileUtils.format_file_size(free)
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        التحقق من صحة مسار الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            صحة المسار
        """
        try:
            path = Path(file_path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        تنظيف اسم الملف من الأحرف غير المسموحة
        
        Args:
            filename: اسم الملف
            
        Returns:
            اسم الملف النظيف
        """
        # إزالة الأحرف غير المسموحة
        import re
        clean = re.sub(r'[^\w\-\.\s]', '', filename)
        # إزالة المسافات الزائدة
        clean = ' '.join(clean.split())
        return clean
    
    @staticmethod
    def get_unique_filename(directory: str, filename: str) -> str:
        """
        الحصول على اسم ملف فريد
        
        Args:
            directory: المجلد
            filename: اسم الملف
            
        Returns:
            اسم ملف فريد
        """
        path = Path(directory) / filename
        if not path.exists():
            return filename
        
        # إضافة رقم
        name = path.stem
        extension = path.suffix
        counter = 1
        
        while True:
            new_name = f"{name}_{counter}{extension}"
            new_path = Path(directory) / new_name
            if not new_path.exists():
                return new_name
            counter += 1
    
    @staticmethod
    def get_directory_size(directory_path: str) -> int:
        """
        الحصول على حجم المجلد
        
        Args:
            directory_path: مسار المجلد
            
        Returns:
            حجم المجلد بالبايت
        """
        try:
            total = 0
            for entry in Path(directory_path).rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
            return total
        except Exception as e:
            logger.error(f"❌ Error getting directory size: {str(e)}")
            return 0
