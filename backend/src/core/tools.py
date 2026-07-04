"""Function Call工具函数封装"""

from langchain_core.tools import tool


@tool
def calculate_net_salary_tool(
    base_salary: float,
    performance_salary: float,
    allowance: float,
    late_count: int = 0,
    leave_days: float = 0,
    overtime_hours: float = 0,
) -> dict:
    """计算员工净工资（包含所有扣款和加班费）

    Args:
        base_salary: 基本月薪（元）
        performance_salary: 绩效工资（元）
        allowance: 岗位津贴（元）
        late_count: 当月迟到次数，默认0
        leave_days: 事假天数，默认0
        overtime_hours: 加班小时数，默认0

    Returns:
        工资明细字典，包含基本工资、绩效、津贴、税前合计、迟到扣款、事假扣款、总扣款、加班费、净工资
    """
    from src.tools.calculator import calculate_net_salary

    return calculate_net_salary(
        base_salary=base_salary,
        performance_salary=performance_salary,
        allowance=allowance,
        late_count=late_count,
        leave_days=leave_days,
        overtime_hours=overtime_hours,
    )


@tool
def calculate_late_deduction_tool(salary: float, late_count: int) -> float:
    """计算迟到扣款金额

    扣款规则：每次迟到扣50元

    Args:
        salary: 月薪金额（元）
        late_count: 当月迟到次数

    Returns:
        总扣款金额（元）
    """
    from src.tools.calculator import calculate_deduction

    return calculate_deduction(salary, late_count)


@tool
def calculate_leave_deduction_tool(salary: float, leave_days: float) -> float:
    """计算事假扣款金额

    月工作日按21.75天计算，扣款 = 日薪 * 请假天数

    Args:
        salary: 月薪金额（元）
        leave_days: 请假天数

    Returns:
        扣款金额（元，保留两位小数）
    """
    from src.tools.calculator import calculate_leave_deduction

    return calculate_leave_deduction(salary, leave_days)


@tool
def calculate_overtime_pay_tool(
    salary: float, overtime_hours: float, multiplier: float = 1.5
) -> float:
    """计算加班费

    月工作小时按174小时计算，加班费 = 时薪 * 加班小时数 * 倍率

    Args:
        salary: 月薪金额（元）
        overtime_hours: 加班小时数
        multiplier: 加班倍率（工作日1.5、周末2.0、节假日3.0），默认1.5

    Returns:
        加班费金额（元，保留两位小数）
    """
    from src.tools.calculator import calculate_overtime_pay

    return calculate_overtime_pay(salary, overtime_hours, multiplier)


# 注册全部工具
ALL_TOOLS = [
    calculate_net_salary_tool,
    calculate_late_deduction_tool,
    calculate_leave_deduction_tool,
    calculate_overtime_pay_tool,
]
