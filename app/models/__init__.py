# # 数据模型

# from app.models.user import User 
# from app.models.hrafile_model import UploadedFile  



# __all__ = ["User", "UploadedFile"]  # 定义 __all__ 变量，控制 from app.models import * 时导入的内容
# 数据模型

from .user import User
from .hrafile_model import UploadedFile  



__all__ = ["User", "UploadedFile"]  # 定义 __all__ 变量，控制 from app.models import * 时导入的内容