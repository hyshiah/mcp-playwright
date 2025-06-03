# Playwright MCP Server - 技术架构方案

## 🏗️ 整体架构设计

### 1. 架构层次图

```
┌─────────────────────────────────────────────┐
│             MCP 客户端 (Claude等)             │
├─────────────────────────────────────────────┤
│              MCP 协议层                      │
├─────────────────────────────────────────────┤
│            FastMCP 框架                      │
├─────────────────────────────────────────────┤
│        Playwright MCP 服务器                 │
│  ┌─────────────┬─────────────┬─────────────┐ │
│  │   会话管理   │   工具层     │   资源层     │ │
│  └─────────────┴─────────────┴─────────────┘ │
├─────────────────────────────────────────────┤
│           Playwright 管理器                  │
│  ┌─────────────┬─────────────┬─────────────┐ │
│  │ 浏览器池     │  页面管理    │  生命周期    │ │
│  └─────────────┴─────────────┴─────────────┘ │
├─────────────────────────────────────────────┤
│            浏览器引擎层                       │
│  ┌─────────────┬─────────────┬─────────────┐ │
│  │  Chromium   │   Firefox   │   WebKit    │ │
│  └─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────┘
```

### 2.1 工程化原则

- **模块化设计**: 清晰的模块边界和职责分离
- **依赖注入**: 通过构造函数注入依赖，便于测试
- **配置管理**: 集中化的配置管理机制
- **错误处理**: 统一的错误处理和日志记录

#### 2.2 稳定性原则

- **资源管理**: 严格的资源生命周期管理
- **异步安全**: 使用asyncio锁保证并发安全
- **超时控制**: 所有操作都有合理的超时设置
- **优雅关闭**: 支持优雅的服务器关闭和资源清理

#### 2.3 可扩展性原则

- **插件架构**: 工具和资源的插件化设计
- **会话隔离**: 支持多会话并发处理
- **浏览器池**: 支持浏览器实例池化管理
- **类型安全**: 完整的类型注解支持

## 🔧 核心组件设计

### 3. BrowserManager (浏览器管理器)

#### 职责

- 管理Playwright浏览器实例的生命周期
- 提供浏览器会话的创建、获取、删除功能
- 维护会话池和资源清理

#### 关键特性

```python
class BrowserManager:
    """浏览器管理器 - 核心管理类"""

    # 初始化参数
    - browser_type: str = "chromium"
    - headless: bool = True
    - max_sessions: int = 10
    - default_viewport: Dict[str, int]
    - default_timeout: int = 30000

    # 核心方法
    async def initialize() -> None
    async def cleanup() -> None
    async def create_session() -> BrowserSession
    async def remove_session() -> bool
    async def health_check() -> Dict[str, Any]
```

#### 并发安全

- 使用 `asyncio.Lock`保护会话操作
- 使用 `weakref.WeakValueDictionary`防止内存泄漏
- 异步上下文管理器确保资源清理

### 4. BrowserSession (浏览器会话)

#### 职责

- 管理单个浏览器上下文和页面
- 提供页面操作的基础接口
- 维护会话状态和配置

#### 状态管理

```python
class BrowserSession:
    """浏览器会话类"""

    # 状态属性
    - session_id: str
    - browser: Browser
    - context: Optional[BrowserContext]
    - page: Optional[Page]
    - _closed: bool

    # 核心方法
    async def initialize() -> None
    async def cleanup() -> None
    async def navigate() -> None
    async def take_screenshot() -> bytes

    @property
    def is_ready() -> bool
```

### 5. BrowserTools (工具集合)

#### 职责

- 封装浏览器操作为MCP工具
- 提供统一的错误处理和结果格式化
- 管理当前活动会话

#### 工具分类

```python
# 浏览器控制
- create_session()
- close_session()
- navigate_to_url()

# 页面交互
- click_element()
- fill_input()
- wait_for_selector()

# 数据提取
- get_text_content()
- get_element_attribute()
- get_page_title()
- get_page_url()

# 高级功能
- take_screenshot()
- execute_javascript()
```

### 6. FastMCP 服务器

#### 生命周期管理

```python
@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """服务器生命周期管理"""

    # 启动阶段
    - 初始化BrowserManager
    - 初始化BrowserTools
    - 设置日志记录

    # 运行阶段
    yield context_data

    # 关闭阶段
    - 清理所有会话
    - 关闭浏览器实例
    - 停止Playwright
```

#### 工具注册

- 使用 `@mcp.tool()`装饰器注册工具
- 完整的类型注解和文档字符串
- 统一的参数验证和错误处理

#### 资源接口

- `session://status` - 会话状态信息
- `browser://health` - 浏览器健康检查
- `help://tools` - 工具使用帮助

#### 提示模板

- `web_automation_prompt` - 网页自动化任务模板

## 🛡️ 错误处理策略

### 7. 分层错误处理

#### 7.1 Playwright层错误

```python
try:
    await page.click(selector)
except PlaywrightTimeoutError:
    return f"点击超时: {selector}"
except PlaywrightError as e:
    return f"Playwright错误: {str(e)}"
```

#### 7.2 会话层错误

```python
def _get_current_session() -> BrowserSession:
    if not self._current_session or not self._current_session.is_ready:
        raise RuntimeError("浏览器会话未初始化，请先创建会话")
    return self._current_session
```

#### 7.3 管理器层错误

```python
async def create_session():
    if len(self._sessions) >= self.max_sessions:
        raise RuntimeError(f"已达到最大会话数限制: {self.max_sessions}")
```

### 8. 日志记录

#### 日志级别

- **INFO**: 正常操作流程
- **WARNING**: 可恢复的错误
- **ERROR**: 严重错误需要关注

#### 日志格式

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 示例
logger.info(f"会话 {session_id} 初始化成功")
logger.warning(f"关闭会话 {session_id} 上下文时出错: {e}")
logger.error(f"浏览器管理器初始化失败: {e}")
```

## 🔄 资源管理策略

### 9. 内存管理

#### 9.1 会话生命周期

```python
# 创建会话时
session = BrowserSession(...)
await session.initialize()
self._sessions[session_id] = session

# 清理会话时
await session.cleanup()
del self._sessions[session_id]
```

#### 9.2 弱引用管理

```python
self._session_refs: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
```

#### 9.3 自动清理

```python
async def cleanup():
    cleanup_tasks = []
    for session in list(self._sessions.values()):
        cleanup_tasks.append(session.cleanup())

    if cleanup_tasks:
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
```

### 10. 并发控制

#### 10.1 会话锁

```python
async with self._lock:
    # 关键会话操作
    session = await self.create_session()
```

#### 10.2 最大会话限制

```python
if len(self._sessions) >= self.max_sessions:
    raise RuntimeError(f"已达到最大会话数限制: {self.max_sessions}")
```

#### 10.3 上下文管理器

```python
@asynccontextmanager
async def session_context(self, **kwargs) -> AsyncIterator[BrowserSession]:
    session = await self.create_session(**kwargs)
    try:
        yield session
    finally:
        await self.remove_session(session.session_id)
```

## 📊 性能优化策略

### 11. 浏览器优化

#### 11.1 无头模式

- 默认启用无头模式减少资源消耗
- 支持可配置的图形模式用于调试

#### 11.2 视口优化

- 默认1280x720分辨率平衡性能和兼容性
- 支持自定义视口配置

#### 11.3 超时控制

- 默认30秒超时避免长时间等待
- 支持按操作类型自定义超时

### 12. 会话管理优化

#### 12.1 会话复用

- 会话创建后可执行多个操作
- 避免频繁创建/销毁浏览器实例

#### 12.2 延迟初始化

- 浏览器管理器延迟初始化
- 仅在需要时启动Playwright

#### 12.3 资源池化

- 支持最大会话数限制
- 自动清理无效会话

## 🧪 测试策略

### 13. 单元测试

#### 13.1 组件测试

```python
# BrowserManager测试
async def test_browser_manager_initialization()
async def test_session_creation()
async def test_session_cleanup()

# BrowserSession测试
async def test_session_navigation()
async def test_session_screenshot()

# BrowserTools测试
async def test_click_element()
async def test_fill_input()
```

#### 13.2 集成测试

```python
# 端到端测试
async def test_complete_workflow()
async def test_error_recovery()
async def test_concurrent_sessions()
```

### 14. 错误模拟测试

#### 14.1 网络错误

- 模拟网络超时
- 模拟连接失败
- 模拟页面加载错误

#### 14.2 元素错误

- 模拟元素不存在
- 模拟元素不可交互
- 模拟JavaScript错误

## 🚀 部署和监控

### 15. 部署配置

#### 15.1 环境要求

- Python 3.10+
- Playwright浏览器引擎
- 足够的内存和CPU资源

#### 15.2 配置选项

```python
# 浏览器配置
BROWSER_TYPE = "chromium"
HEADLESS = True
MAX_SESSIONS = 10

# 超时配置
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 60000

# 视口配置
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 720
```

### 16. 健康检查

#### 16.1 浏览器健康

```python
async def health_check() -> Dict[str, Any]:
    return {
        "initialized": self._initialized,
        "browser_type": self.browser_type,
        "session_count": self.session_count,
        "max_sessions": self.max_sessions,
        "active_sessions": list(self._sessions.keys())
    }
```

#### 16.2 会话监控

- 活跃会话数量
- 会话创建/销毁速率
- 平均会话生命周期

## 📈 未来扩展方向

### 17. 功能扩展

#### 17.1 高级交互

- 拖拽操作
- 键盘快捷键
- 多文件上传
- Cookie管理

#### 17.2 性能监控

- 页面加载时间
- 资源使用统计
- 操作成功率

#### 17.3 安全增强

- 请求过滤
- 域名白名单
- 资源访问控制

### 18. 架构演进

#### 18.1 微服务化

- 拆分为独立的浏览器服务
- 支持水平扩展
- 负载均衡

#### 18.2 持久化

- 会话状态持久化
- 操作历史记录
- 配置热更新

这个技术架构方案提供了一个全面、稳定、可扩展的Playwright MCP服务器实现基础，确保了工程化质量和生产环境的可靠性。
