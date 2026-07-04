"""薪资提取与计算函数"""

import csv
from pathlib import Path

import pandas as pd
import pdfplumber


# 文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
RULES_DIR = DATA_DIR / "rules"
SALARY_CSV = RULES_DIR / "salary.csv"
PDF_PATH = RAW_DIR / "员工手册.pdf"


def extract_salary_tables(pdf_path: Path = PDF_PATH) -> pd.DataFrame:
    """使用pdfplumber从PDF提取薪资/绩效表格"""
    all_rows: list[dict[str, str]] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    # 尝试识别薪资相关表格
                    header = table[0]
                    if header and any(
                        keyword in str(cell)
                        for cell in header
                        if cell
                        for keyword in ["薪资", "工资", "绩效", "薪酬"]
                    ):
                        for row in table[1:]:
                            if row and any(cell for cell in row if cell):
                                row_dict = {
                                    f"col{i}": str(cell).strip() if cell else ""
                                    for i, cell in enumerate(row)
                                }
                                all_rows.append(row_dict)

    if not tables:
        # 如果未找到表格，创建默认薪资结构
        return create_default_salary_table()

    return pd.DataFrame(all_rows)


def create_default_salary_table() -> pd.DataFrame:
    """创建默认薪资结构表"""
    data = {
        "员工ID": ["E001", "E002", "E003", "E004", "E005"],
        "姓名": ["张三", "李四", "王五", "赵六", "钱七"],
        "基本工资": [8000, 10000, 12000, 15000, 18000],
        "绩效工资": [2000, 2500, 3000, 3500, 4000],
        "岗位津贴": [500, 800, 1000, 1500, 2000],
        "扣除项": [0, 0, 0, 0, 0],
    }
    return pd.DataFrame(data)


def save_salary_csv(df: pd.DataFrame, output_path: Path = SALARY_CSV) -> None:
    """将薪资DataFrame保存为CSV文件"""
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"薪资CSV已保存: {output_path}")


def calculate_deduction(salary: float, late_count: int) -> float:
    """计算迟到扣款

    Args:
        salary: 月薪金额
        late_count: 当月迟到次数

    Returns:
        总扣款金额
    """
    if salary <= 0:
        raise ValueError("薪资必须为正数")
    if late_count < 0:
        raise ValueError("迟到次数不能为负数")

    # 扣款规则：
    # 迟到<30分钟：每次扣50元
    # 迟到>=30分钟：每次扣100元（按0.5天事假处理）
    deduction = 0.0
    for _ in range(late_count):
        deduction += 50.0  # 假设所有迟到都<30分钟

    return deduction


def calculate_leave_deduction(salary: float, leave_days: float) -> float:
    """计算事假扣款

    Args:
        salary: 月薪金额
        leave_days: 请假天数

    Returns:
        扣款金额
    """
    if salary <= 0:
        raise ValueError("薪资必须为正数")
    if leave_days < 0:
        raise ValueError("请假天数不能为负数")

    # 月工作日：21.75天
    daily_rate = salary / 21.75
    deduction = daily_rate * leave_days

    return round(deduction, 2)


def calculate_overtime_pay(
    salary: float, overtime_hours: float, multiplier: float = 1.5
) -> float:
    """计算加班费

    Args:
        salary: 月薪金额
        overtime_hours: 加班小时数
        multiplier: 加班倍率（工作日1.5，周末2，节假日3）

    Returns:
        加班费金额
    """
    if salary <= 0:
        raise ValueError("薪资必须为正数")
    if overtime_hours < 0:
        raise ValueError("加班小时数不能为负数")
    if multiplier < 1:
        raise ValueError("倍率必须大于等于1")

    # 月工作小时：21.75 * 8 = 174小时
    hourly_rate = salary / 174
    overtime_pay = hourly_rate * overtime_hours * multiplier

    return round(overtime_pay, 2)


def calculate_net_salary(
    base_salary: float,
    performance_salary: float,
    allowance: float,
    late_count: int = 0,
    leave_days: float = 0,
    overtime_hours: float = 0,
) -> dict[str, float]:
    """计算净工资（包含所有扣款和 additions）

    Args:
        base_salary: 基本月薪
        performance_salary: 绩效工资
        allowance: 岗位津贴
        late_count: 迟到次数
        leave_days: 事假天数
        overtime_hours: 加班小时数

    Returns:
        工资明细字典
    """
    gross_salary = base_salary + performance_salary + allowance
    late_deduction = calculate_deduction(base_salary, late_count)
    leave_deduction = calculate_leave_deduction(base_salary, leave_days)
    overtime_pay = calculate_overtime_pay(base_salary, overtime_hours)

    total_deduction = late_deduction + leave_deduction
    net_salary = gross_salary - total_deduction + overtime_pay

    return {
        "base_salary": base_salary,
        "performance_salary": performance_salary,
        "allowance": allowance,
        "gross_salary": gross_salary,
        "late_deduction": late_deduction,
        "leave_deduction": leave_deduction,
        "total_deduction": total_deduction,
        "overtime_pay": overtime_pay,
        "net_salary": round(net_salary, 2),
    }


def init_salary_table() -> None:
    """初始化salary.csv（从PDF或默认数据）"""
    try:
        df = extract_salary_tables()
        save_salary_csv(df)
    except Exception as e:
        print(f"从PDF提取失败: {e}")
        print("使用默认薪资表...")
        df = create_default_salary_table()
        save_salary_csv(df)


if __name__ == "__main__":
    init_salary_table()
