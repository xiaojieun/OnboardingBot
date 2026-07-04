"""
环境检测脚本

验证以下内容：
1. API_KEY 环境变量可正常读取
2. text-embedding-v4 接口连通性
3. 核心依赖包已安装

使用方法：
    python scripts/check_environment.py

成功输出：
    Environment Ready
"""

import os
import sys
from typing import Optional


def check_api_key() -> bool:
    """检查 API_KEY 环境变量是否已设置。"""
    api_key = os.environ.get("API_KEY")
    if not api_key:
        print("[ERROR] API_KEY 环境变量未设置")
        print("请设置环境变量：$env:API_KEY='your-api-key'")
        return False
    
    if len(api_key) < 10:
        print("[ERROR] API_KEY 长度不足，请检查是否正确")
        return False
    
    print("[OK] API_KEY 环境变量已设置")
    return True


def check_python_version() -> bool:
    """检查 Python 版本是否为 3.12.10。"""
    version = sys.version_info
    if version.major != 3 or version.minor != 12:
        print(f"[ERROR] Python 版本 {version.major}.{version.minor}.{version.micro} 不符合要求")
        print("要求：Python 3.12.10")
        return False
    
    print(f"[OK] Python 版本 {version.major}.{version.minor}.{version.micro} 符合要求")
    return True


def check_dependencies() -> bool:
    """检查核心依赖包是否已安装。"""
    required_packages = [
        "langchain",
        "dashscope",
        "chromadb",
        "pandas",
        "numpy",
        "fastapi",
        "uvicorn",
        "pdfplumber",
        "pydantic",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"[ERROR] {package} 未安装")
    
    if missing_packages:
        print(f"\n请安装缺失的依赖包：")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_dashscope_connection() -> bool:
    """检查 DashScope API 连通性（text-embedding-v4）。"""
    try:
        import dashscope
        from dashscope import TextEmbedding
        
        # 设置 API Key
        api_key = os.environ.get("API_KEY")
        if api_key:
            dashscope.api_key = api_key
        
        # 尝试调用 text-embedding-v4 模型
        test_text = "这是一个连通性测试"
        response = TextEmbedding.call(
            model="text-embedding-v4",
            input=test_text
        )
        
        if response.status_code == 200:
            print("[OK] DashScope text-embedding-v4 接口连通")
            return True
        else:
            print(f"[ERROR] DashScope API 调用失败：{response.code} - {response.message}")
            return False
            
    except Exception as e:
        print(f"[ERROR] DashScope 连接测试失败：{str(e)}")
        return False


def main() -> None:
    """主函数：执行所有环境检查。"""
    print("=" * 50)
    print("入职智引系统 - 环境检测")
    print("=" * 50)
    
    results = []
    
    # 1. 检查 Python 版本
    print("\n[1/4] 检查 Python 版本...")
    results.append(check_python_version())
    
    # 2. 检查 API_KEY
    print("\n[2/4] 检查 API_KEY 环境变量...")
    results.append(check_api_key())
    
    # 3. 检查依赖包
    print("\n[3/4] 检查依赖包...")
    results.append(check_dependencies())
    
    # 4. 检查 DashScope 连通性
    print("\n[4/4] 检查 DashScope 接口连通性...")
    results.append(check_dashscope_connection())
    
    # 汇总结果
    print("\n" + "=" * 50)
    
    if all(results):
        print("Environment Ready")
        sys.exit(0)
    else:
        print("环境检测未通过，请检查上述错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()