"""
Basic tests to verify testing framework is working
基础测试，用于验证测试框架正常工作
"""

import pytest
import asyncio
from datetime import datetime


class TestBasicFunctionality:
    """
    基础功能测试类
    """
    
    def test_python_environment(self):
        """
        测试Python环境
        """
        assert True  # 基本断言
        assert isinstance("hello", str)
        assert 1 + 1 == 2
    
    def test_datetime_functionality(self):
        """
        测试日期时间功能
        """
        now = datetime.now()
        assert isinstance(now, datetime)
        assert now.year >= 2024
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """
        测试异步功能
        """
        async def async_function():
            await asyncio.sleep(0.001)  # 模拟异步操作
            return "async result"
        
        result = await async_function()
        assert result == "async result"
    
    def test_list_operations(self):
        """
        测试列表操作
        """
        test_list = [1, 2, 3, 4, 5]
        
        assert len(test_list) == 5
        assert 3 in test_list
        assert test_list[0] == 1
        assert test_list[-1] == 5
        
        # 测试列表推导式
        squared = [x**2 for x in test_list]
        assert squared == [1, 4, 9, 16, 25]
    
    def test_dictionary_operations(self):
        """
        测试字典操作
        """
        test_dict = {
            "name": "测试用户",
            "age": 25,
            "active": True
        }
        
        assert test_dict["name"] == "测试用户"
        assert test_dict.get("age") == 25
        assert test_dict.get("email", "未设置") == "未设置"
        assert "active" in test_dict
    
    @pytest.mark.parametrize("input_value,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
        (10, 20)
    ])
    def test_parametrized_double_function(self, input_value, expected):
        """
        参数化测试示例
        """
        def double(x):
            return x * 2
        
        result = double(input_value)
        assert result == expected 