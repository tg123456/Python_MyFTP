import os
import sys

# 保证项目在其他环境也能正常运行
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from core import core

# 程序的开始入口
if __name__ == '__main__':
    core.main()
