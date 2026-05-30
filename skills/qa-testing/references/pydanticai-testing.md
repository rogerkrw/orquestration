# PydanticAI Agent Testing

PydanticAI ships first-class testing utilities that let you test agent logic without burning API tokens or hitting network.

## Block real API calls in tests

```python
# conftest.py
import pytest
from pydantic_ai import models

@pytest.fixture(autouse=True)
def block_real_models():
    models.ALLOW_MODEL_REQUESTS = False
    yield
```

`ALLOW_MODEL_REQUESTS = False` makes any unintercepted model call raise immediately. Catches "test forgot to mock the model" bugs.

## TestModel — fast structural tests

`TestModel` returns deterministic structured output matching the agent's `output_type`. No reasoning, no tool calls (unless requested), no cost.

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    bullets: list[str]

agent = Agent("openai:gpt-5.4-mini", output_type=Summary)

def test_agent_returns_summary():
    with agent.override(model=TestModel()):
        result = agent.run_sync("Summarize this article: ...")
    assert isinstance(result.output, Summary)
    assert isinstance(result.output.title, str)
    assert isinstance(result.output.bullets, list)
```

Use for: schema conformance, tool invocation paths, message history flow.

## FunctionModel — custom test behavior

When you need control over what the model "says":

```python
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.messages import ModelResponse, TextPart

def my_response(messages, info: AgentInfo) -> ModelResponse:
    last = messages[-1].parts[-1].content
    if "weather" in last.lower():
        return ModelResponse(parts=[TextPart(content="It is sunny.")])
    return ModelResponse(parts=[TextPart(content="I don't know.")])

def test_weather_path():
    with agent.override(model=FunctionModel(my_response)):
        result = agent.run_sync("What's the weather?")
    assert "sunny" in result.output
```

Use for: testing branching logic, fallbacks, error handling within the agent flow.

## Testing tools

```python
from pydantic_ai import Agent, RunContext

agent = Agent("openai:gpt-5.4-mini")

@agent.tool_plain
def get_weather(city: str) -> str:
    return f"Weather in {city}: sunny"

def test_tool_is_callable_via_test_model():
    with agent.override(model=TestModel(call_tools="all")):
        result = agent.run_sync("Use the weather tool for Berlin")
    # TestModel will invoke all tools available
    assert any("Berlin" in str(m) for m in result.all_messages())
```

For tools with external deps, mock the dep — not the tool function:

```python
@agent.tool
async def fetch_user(ctx: RunContext[Deps], user_id: int) -> User:
    return await ctx.deps.db.get_user(user_id)

def test_fetch_user():
    fake_db = FakeDB()
    fake_db.users[1] = User(id=1, name="Alice")
    deps = Deps(db=fake_db)

    with agent.override(model=TestModel(call_tools=["fetch_user"])):
        result = agent.run_sync("Get user 1", deps=deps)
    # assertions on fake_db calls + result
```

## Recording real LLM responses (cassettes)

For end-to-end-ish tests against a real model, record once, replay forever:

```python
# Using vcrpy or pydantic-ai's built-in capture (if available)
import vcr

@vcr.use_cassette("tests/cassettes/agent_summary.yaml")
def test_real_agent_summary():
    result = agent.run_sync("Summarize: ...")
    assert len(result.output.bullets) >= 3
```

- Cassettes go in `tests/cassettes/`
- Re-record by deleting the cassette and re-running
- Review cassette diffs in PR — they reveal what changed in model behavior
- Use sparingly — they're slow and version-sensitive

## Output validators

If the agent has output validators:

```python
@agent.output_validator
async def validate_summary(ctx: RunContext, output: Summary) -> Summary:
    if len(output.bullets) < 3:
        raise ModelRetry("Need at least 3 bullets")
    return output

def test_validator_retries_on_short_output():
    call_count = 0
    def response(messages, info):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return ModelResponse(parts=[ToolCallPart(
                tool_name="final_result",
                args={"title": "T", "bullets": ["one"]}
            )])
        return ModelResponse(parts=[ToolCallPart(
            tool_name="final_result",
            args={"title": "T", "bullets": ["one", "two", "three"]}
        )])

    with agent.override(model=FunctionModel(response)):
        result = agent.run_sync("Summarize")
    assert call_count == 2  # validator retried
```

## Pattern: deps injection in tests

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Deps:
    db: Any
    cache: Any
    clock: Callable[[], datetime] = datetime.utcnow

agent = Agent("openai:gpt-5.4-mini", deps_type=Deps)

@agent.tool
async def get_user_age(ctx: RunContext[Deps], user_id: int) -> int:
    user = await ctx.deps.db.get_user(user_id)
    return (ctx.deps.clock().date() - user.birthdate).days // 365

# Test with frozen clock
def test_age_calculation():
    deps = Deps(db=FakeDB({1: User(birthdate=date(2000, 1, 1))}),
                cache=None,
                clock=lambda: datetime(2026, 1, 1))
    with agent.override(model=TestModel(call_tools=["get_user_age"])):
        result = agent.run_sync("How old is user 1?", deps=deps)
    # assert on the tool call result
```

Always inject time, randomness, and external services through `deps` so tests can swap them.
