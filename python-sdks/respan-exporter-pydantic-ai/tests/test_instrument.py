import pytest
from pydantic_ai.agent import Agent
from respan_exporter_pydantic_ai import instrument_pydantic_ai
from respan_tracing import RespanTelemetry
from respan_tracing.core.tracer import RespanTracer

@pytest.fixture(autouse=True)
def reset_tracer():
    RespanTracer.reset_instance()
    # Reset Pydantic AI agent instrumentation
    Agent._instrument_default = False
    yield
    RespanTracer.reset_instance()

def test_instrument_global():
    """Verify global instrumentation: after instrument_pydantic_ai(), the default used for agents has a tracer."""
    telemetry = RespanTelemetry(app_name="test-app", api_key="test-key", is_enabled=True)

    instrument_pydantic_ai()

    # Behavior: the global default (used for agents that don't set their own) must have a tracer
    default_instrument = Agent._instrument_default
    assert default_instrument is not False
    assert hasattr(default_instrument, "tracer")
    assert default_instrument.tracer is not None

def test_instrument_disabled():
    """Tests the telemetry-disabled path: when RespanTelemetry(is_enabled=False), instrumentation is skipped."""
    telemetry = RespanTelemetry(app_name="test-app", api_key="test-key", is_enabled=False)

    instrument_pydantic_ai()

    # When disabled, global default is not set (instrumentation was skipped)
    assert Agent._instrument_default is False

def test_instrument_specific_agent():
    # Initialize telemetry
    telemetry = RespanTelemetry(app_name="test-app", api_key="test-key", is_enabled=True)
    
    # Create an agent
    agent = Agent(model='test')
    
    # By default, not instrumented with specific settings
    assert getattr(agent, "instrument", None) in (None, False)
    
    # Instrument specific agent
    instrument_pydantic_ai(agent=agent)
    
    # Global should not be changed by this
    assert Agent._instrument_default is False
    
    # Agent should have instrumentation settings
    assert getattr(agent, "instrument", None) is not None
    assert getattr(agent, "instrument", None) is not False
    assert hasattr(agent.instrument, "tracer")
    assert agent.instrument.tracer is not None
