"""记账本 - 个人财务管理应用"""
import sys
import os

# ensure project root in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
