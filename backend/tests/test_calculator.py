"""calculator模块的单元测试"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.calculator import (
    calculate_deduction,
    calculate_leave_deduction,
    calculate_net_salary,
    calculate_overtime_pay,
    create_default_salary_table,
    extract_salary_tables,
)


class TestCalculateDeduction:
    """calculate_deduction函数测试"""

    def test_no_late(self) -> None:
        """测试无迟到情况"""
        result = calculate_deduction(10000, 0)
        assert result == 0.0

    def test_one_late(self) -> None:
        """测试一次迟到"""
        result = calculate_deduction(10000, 1)
        assert result == 50.0

    def test_multiple_late(self) -> None:
        """测试多次迟到"""
        result = calculate_deduction(10000, 5)
        assert result == 250.0

    def test_invalid_salary_negative(self) -> None:
        """测试负数薪资报错"""
        with pytest.raises(ValueError, match="薪资必须为正数"):
            calculate_deduction(-1000, 1)

    def test_invalid_salary_zero(self) -> None:
        """测试零薪资报错"""
        with pytest.raises(ValueError, match="薪资必须为正数"):
            calculate_deduction(0, 1)

    def test_invalid_late_count_negative(self) -> None:
        """测试负数迟到次数报错"""
        with pytest.raises(ValueError, match="迟到次数不能为负数"):
            calculate_deduction(10000, -1)


class TestCalculateLeaveDeduction:
    """calculate_leave_deduction函数测试"""

    def test_no_leave(self) -> None:
        """测试无请假情况"""
        result = calculate_leave_deduction(10000, 0)
        assert result == 0.0

    def test_one_day_leave(self) -> None:
        """测试一天事假"""
        result = calculate_leave_deduction(10000, 1)
        expected = round(10000 / 21.75, 2)
        assert result == expected

    def test_half_day_leave(self) -> None:
        """测试半天事假"""
        result = calculate_leave_deduction(10000, 0.5)
        expected = round((10000 / 21.75) * 0.5, 2)
        assert result == expected

    def test_invalid_leave_days(self) -> None:
        """测试负数请假天数报错"""
        with pytest.raises(ValueError, match="请假天数不能为负数"):
            calculate_leave_deduction(10000, -1)


class TestCalculateOvertimePay:
    """calculate_overtime_pay函数测试"""

    def test_no_overtime(self) -> None:
        """测试无加班情况"""
        result = calculate_overtime_pay(10000, 0)
        assert result == 0.0

    def test_weekday_overtime(self) -> None:
        """测试工作日加班（1.5倍）"""
        result = calculate_overtime_pay(10000, 8, multiplier=1.5)
        hourly_rate = 10000 / 174
        expected = round(hourly_rate * 8 * 1.5, 2)
        assert result == expected

    def test_weekend_overtime(self) -> None:
        """测试周末加班（2倍）"""
        result = calculate_overtime_pay(10000, 8, multiplier=2.0)
        hourly_rate = 10000 / 174
        expected = round(hourly_rate * 8 * 2.0, 2)
        assert result == expected

    def test_invalid_multiplier(self) -> None:
        """测试倍率小于1报错"""
        with pytest.raises(ValueError, match="倍率必须大于等于1"):
            calculate_overtime_pay(10000, 8, multiplier=0.5)


class TestCalculateNetSalary:
    """calculate_net_salary函数测试"""

    def test_basic_salary(self) -> None:
        """测试基本工资计算"""
        result = calculate_net_salary(
            base_salary=10000,
            performance_salary=2500,
            allowance=800,
        )
        assert result["gross_salary"] == 13300
        assert result["total_deduction"] == 0
        assert result["overtime_pay"] == 0
        assert result["net_salary"] == 13300

    def test_with_deductions(self) -> None:
        """测试有扣款情况"""
        result = calculate_net_salary(
            base_salary=10000,
            performance_salary=2500,
            allowance=800,
            late_count=2,
        )
        assert result["late_deduction"] == 100
        assert result["net_salary"] == 13200

    def test_with_overtime(self) -> None:
        """测试有加班情况"""
        result = calculate_net_salary(
            base_salary=10000,
            performance_salary=2500,
            allowance=800,
            overtime_hours=8,
        )
        hourly_rate = 10000 / 174
        expected_overtime = round(hourly_rate * 8 * 1.5, 2)
        assert result["overtime_pay"] == expected_overtime
        assert result["net_salary"] == 13300 + expected_overtime


class TestSalaryTable:
    """薪资表操作测试"""

    def test_create_default_table(self) -> None:
        """测试创建默认薪资表"""
        df = create_default_salary_table()
        assert len(df) == 5
        assert list(df.columns) == [
            "员工ID",
            "姓名",
            "基本工资",
            "绩效工资",
            "岗位津贴",
            "扣除项",
        ]

    def test_extract_salary_tables(self) -> None:
        """测试从PDF提取薪资表"""
        df = extract_salary_tables()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
