# 测试指南 - Wiki Impact Assessment System

本文档说明如何运行和维护 Wiki Impact Assessment System 的测试套件。

## 测试框架

我们使用以下工具进行测试：

- **pytest**: 主要的测试运行器
- **pytest-asyncio**: 支持异步测试
- **pytest-cov**: 代码覆盖率报告
- **httpx**: HTTP客户端测试
- **faker**: 生成测试数据
- **freezegun**: 时间模拟

## 安装测试依赖

```bash
# 安装所有依赖（包括测试依赖）
pip install -r requirements.txt

# 或者仅安装测试相关依赖
pip install pytest pytest-asyncio pytest-cov httpx faker freezegun
```

## 运行测试

### 使用测试运行脚本（推荐）

```bash
# 运行所有测试
python run_tests.py

# 运行单元测试
python run_tests.py --unit

# 运行API测试
python run_tests.py --api

# 运行集成测试
python run_tests.py --integration

# 生成覆盖率报告
python run_tests.py --coverage

# 详细输出
python run_tests.py --verbose

# 安装依赖并运行测试
python run_tests.py --install-deps --coverage
```

### 直接使用pytest

```bash
# 切换到backend目录
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 运行特定测试类
pytest tests/test_services.py::TestImpactCalculator

# 运行特定测试方法
pytest tests/test_api.py::TestWikipediaEndpoints::test_analyze_wiki_page_success

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 详细输出
pytest -v

# 仅运行失败的测试
pytest --lf
```

## 测试结构

```
backend/
├── tests/
│   ├── __init__.py          # 测试模块初始化
│   ├── test_basic.py        # 基础功能测试
│   ├── test_models.py       # 数据模型测试
│   ├── test_services.py     # 服务层测试
│   └── test_api.py          # API端点测试
├── conftest.py              # pytest配置和fixtures
└── pytest.ini              # pytest配置文件
```

## 测试类型

### 1. 单元测试 (Unit Tests)

测试单个函数或方法的功能：

```python
def test_password_hashing():
    user = User(username="test", email="test@example.com")
    user.set_password("password123")
    assert user.verify_password("password123")
```

### 2. 集成测试 (Integration Tests)

测试组件之间的交互：

```python
@pytest.mark.integration
async def test_complete_user_workflow(test_db_session):
    # 测试完整的用户创建和验证流程
    pass
```

### 3. API测试 (API Tests)

测试HTTP端点：

```python
@pytest.mark.api
async def test_analyze_wiki_page(client):
    response = await client.post("/api/v1/wikipedia/analyze", 
                                json={"page_url": "https://zh.wikipedia.org/wiki/Python"})
    assert response.status_code == 202
```

## 测试数据

### 使用Fixtures

```python
@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123"
    }

def test_user_creation(sample_user_data):
    user = User(**sample_user_data)
    assert user.username == "testuser"
```

### 使用Faker生成随机数据

```python
from faker import Faker
fake = Faker("zh_CN")

def test_with_random_data():
    username = fake.user_name()
    email = fake.email()
    # 使用随机数据进行测试
```

## 模拟和Mocking

### 模拟数据库操作

```python
@pytest_asyncio.fixture
async def test_db_session():
    # 返回测试数据库会话
    async with AsyncSessionLocal() as session:
        yield session
```

### 模拟外部API调用

```python
@pytest.fixture
def mock_wikipedia_api(monkeypatch):
    def mock_fetch(*args, **kwargs):
        return {"title": "测试页面", "content": "测试内容"}
    
    monkeypatch.setattr("app.services.wikipedia_service.fetch_page", mock_fetch)
```

## 覆盖率报告

运行测试时生成覆盖率报告：

```bash
# 生成终端报告
pytest --cov=app --cov-report=term-missing

# 生成HTML报告
pytest --cov=app --cov-report=html

# 查看HTML报告
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
start backend/htmlcov/index.html  # Windows
```

## 最佳实践

### 1. 测试命名

- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 2. 测试结构

使用AAA模式（Arrange-Act-Assert）：

```python
def test_user_login():
    # Arrange - 准备测试数据
    user = User(username="test", email="test@example.com")
    user.set_password("password123")
    
    # Act - 执行被测试的操作
    is_valid = user.verify_password("password123")
    
    # Assert - 验证结果
    assert is_valid is True
```

### 3. 独立性

每个测试应该独立运行，不依赖其他测试的结果。

### 4. 清晰的断言

```python
# 好的断言
assert user.is_active is True
assert len(users) == 3
assert "error" in response.json()

# 避免的断言
assert user.is_active  # 不够明确
assert users  # 可能有歧义
```

### 5. 测试边界条件

```python
def test_edge_cases():
    # 测试空值
    assert calculate_impact([]) == 0.0
    
    # 测试极大值
    large_edits = [create_edit() for _ in range(10000)]
    score = calculate_impact(large_edits)
    assert 0 <= score <= 100
    
    # 测试异常情况
    with pytest.raises(ValueError):
        calculate_impact(None)
```

## 持续集成

测试应该在以下情况下运行：

1. 每次代码提交前
2. Pull Request创建时
3. 主分支更新时
4. 定期调度运行

## 故障排除

### 常见问题

1. **数据库连接错误**
   ```bash
   # 确保测试使用内存数据库
   export ENVIRONMENT=testing
   ```

2. **依赖缺失**
   ```bash
   pip install -r requirements.txt
   ```

3. **权限问题**
   ```bash
   # 确保有执行权限
   chmod +x run_tests.py
   ```

### 调试测试

```bash
# 运行特定测试并显示详细输出
pytest tests/test_models.py::TestUserModel::test_password_hashing -v -s

# 进入调试模式
pytest --pdb

# 仅运行失败的测试
pytest --lf --tb=short
```

## 贡献测试

添加新功能时，请确保：

1. 为新功能编写相应的测试
2. 保持测试覆盖率在70%以上
3. 测试通过所有现有测试
4. 遵循项目的测试约定

## 测试标记

使用pytest标记组织测试：

```python
@pytest.mark.unit
def test_simple_function():
    pass

@pytest.mark.integration
async def test_database_integration():
    pass

@pytest.mark.slow
def test_performance():
    pass
```

运行特定标记的测试：

```bash
pytest -m unit          # 只运行单元测试
pytest -m "not slow"    # 跳过慢速测试
pytest -m "unit or api" # 运行单元测试或API测试
``` 