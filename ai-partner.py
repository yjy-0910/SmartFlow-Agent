"""
ai-partner.py - 应用入口文件
Gradio 部署时指定的主文件，实际逻辑在 app.py 中。
"""
from app import demo  # noqa: F401

demo.launch()
