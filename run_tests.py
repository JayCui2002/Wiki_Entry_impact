#!/usr/bin/env python3
"""
Test runner script for Wiki Impact Assessment System
维基影响评估系统的测试运行脚本

使用方法:
python run_tests.py                    # 运行所有测试
python run_tests.py --unit             # 只运行单元测试
python run_tests.py --integration      # 只运行集成测试
python run_tests.py --api              # 只运行API测试
python run_tests.py --coverage         # 运行测试并生成覆盖率报告
python run_tests.py --verbose          # 详细输出
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def setup_environment():
    """
    设置测试环境
    """
    # 确保后端目录在Python路径中
    backend_dir = Path(__file__).parent / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # 设置测试环境变量
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["DB_NAME"] = "wiki_impact_test"
    os.environ["REDIS_ENABLED"] = "false"
    
    print("✅ 测试环境设置完成")


def install_dependencies():
    """
    安装测试依赖
    """
    print("📦 检查并安装测试依赖...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✅ 依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    return True


def run_tests(test_type=None, verbose=False, coverage=False):
    """
    运行测试
    """
    # 切换到backend目录
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # 构建pytest命令
    cmd = [sys.executable, "-m", "pytest"]
    
    # 添加参数
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # 根据测试类型添加标记
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])
    
    # 添加测试目录
    cmd.append("tests/")
    
    print(f"🧪 运行测试命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        return False
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="Wiki Impact Assessment System 测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="只运行单元测试"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="只运行集成测试"
    )
    parser.add_argument(
        "--api", 
        action="store_true", 
        help="只运行API测试"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="生成测试覆盖率报告"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="详细输出"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true", 
        help="安装测试依赖"
    )
    
    args = parser.parse_args()
    
    print("🚀 Wiki Impact Assessment System 测试运行器")
    print("=" * 50)
    
    # 安装依赖（如果需要）
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # 设置环境
    setup_environment()
    
    # 确定测试类型
    test_type = None
    if args.unit:
        test_type = "unit"
        print("🎯 运行类型: 单元测试")
    elif args.integration:
        test_type = "integration"
        print("🎯 运行类型: 集成测试")
    elif args.api:
        test_type = "api"
        print("🎯 运行类型: API测试")
    else:
        print("🎯 运行类型: 所有测试")
    
    # 运行测试
    success = run_tests(
        test_type=test_type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    if success:
        print("\n🎉 所有测试通过!")
        if args.coverage:
            print("📊 覆盖率报告已生成到 backend/htmlcov/ 目录")
    else:
        print("\n❌ 有测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 