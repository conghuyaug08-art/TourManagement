import json
import os
import shutil

class DataManager:
    """
    Lớp xử lý nghiệp vụ đọc/ghi JSON an toàn.
    Đáp ứng tiêu chí: Dùng with, xử lý FileNotFoundError, JSONDecodeError, file rỗng, sao lưu dữ liệu.
    """
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # Đảm bảo thư mục data luôn tồn tại
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_path(self, filename):
        return os.path.join(self.data_dir, filename)

    def read_data(self, filename):
        """Đọc dữ liệu từ file JSON, tự động khôi phục nếu file hỏng."""
        file_path = self._get_path(filename)
        
        if not os.path.exists(file_path):
            print(f"[*] File '{filename}' không tồn tại. Đang trả về danh sách rỗng.")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:  # Xử lý trường hợp file rỗng
                    return []
                return json.loads(content)
                
        except json.JSONDecodeError:
            print(f"[!] Lỗi định dạng JSON tại '{filename}'. Đang thử khôi phục từ bản sao lưu...")
            return self._restore_from_backup(filename)
        except PermissionError:
            print(f"[!] Lỗi: Không có quyền đọc file '{filename}'.")
            return []
        except Exception as e:
            print(f"[!] Lỗi hệ thống khi đọc '{filename}': {e}")
            return []

    def write_data(self, filename, data):
        """Ghi dữ liệu ra file JSON, tạo bản sao lưu trước khi ghi đè."""
        file_path = self._get_path(filename)
        
        # Luôn backup trước khi ghi để chống mất dữ liệu khi app crash giữa chừng
        self._backup_file(filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except TypeError:
            print(f"[!] Lỗi: Cấu trúc dữ liệu không thể chuyển đổi sang JSON.")
            return False
        except Exception as e:
            print(f"[!] Lỗi hệ thống khi ghi '{filename}': {e}")
            return False

    def _backup_file(self, filename):
        """Tạo file _bak.json trước khi thay đổi dữ liệu chính."""
        file_path = self._get_path(filename)
        if os.path.exists(file_path):
            name_only = filename.split('.')[0]
            backup_path = self._get_path(f"{name_only}_bak.json")
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                print(f"[-] Không thể tạo file sao lưu cho '{filename}': {e}")

    def _restore_from_backup(self, filename):
        """Khôi phục dữ liệu từ file backup khi file chính bị lỗi cấu trúc."""
        name_only = filename.split('.')[0]
        backup_path = self._get_path(f"{name_only}_bak.json")
        
        if os.path.exists(backup_path):
            try:
                with open(backup_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"[!] File sao lưu '{name_only}_bak.json' cũng bị hỏng định dạng.")
        return []