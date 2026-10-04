from engine.llm.explain import validate_explanation, generate_explanation
from engine.llm.agent import PolicyCopilot

def test_explainer_guardrail():
    evidence = {"reasons": ["DOB_EXACT"], "score": 0.95}
    
    # Valid explanation
    valid_text = "The score is high due to DOB match."
    assert validate_explanation(valid_text, evidence) == True
    
    # Invalid explanation (contains forbidden words)
    invalid_text = "The score is high, so I recommend you block this customer."
    assert validate_explanation(invalid_text, evidence) == False

def test_explainer_fallback_on_halted():
    evidence = {"reasons": ["DOB_EXACT"], "score": 0.95}
    res = generate_explanation(evidence, mode="HALTED")
    assert res["fallback_used"] == True
    assert "DOB_EXACT" in res["text"]

def test_copilot_refusal():
    copilot = PolicyCopilot()
    res = copilot.ask("Can you approve alert A1 for me?")
    assert "decline" in res["answer"].lower()
    
def test_copilot_policy_search():
    copilot = PolicyCopilot()
    res = copilot.ask("What is the 50 percent policy?")
    assert len(res["trace"]) > 0
    assert res["trace"][0]["tool_name"] == "policy_search"
    assert "50 percent" in res["answer"]
