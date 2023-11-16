import pytest

from run import run_evaluation, simulate_conversation_and_evaluate

# Test results are stored here
evaluation_results : any

@pytest.fixture(scope="session", autouse=True)
def run_before_any_test():
    from copilot_aisdk import chat
  
    global metrics_summary, metrics_summary_chat
    metrics_summary, tabular_result = run_evaluation(chat.chat_completion,
                                        "test_aisdk_copilot",
                                        "src/tests/evaluation_dataset.jsonl")
    metrics_summary_chat, tabular_result_chat = simulate_conversation_and_evaluate(
        chat_completion_fn=chat.chat_completion,
        persona_profile="src/tests/example_persona.json",
        num_conv_turn=2, max_tokens=500, temperature=0.0 ,
        eval_name = "test_aisdk_chat")

def test_gpt_groundedness_atleast4():
    assert(metrics_summary.metrics_summary['mean_gpt_groundedness'] >= 4)

def test_gpt_relevance_atleast4():
    assert(metrics_summary.metrics_summary['mean_gpt_relevance'] >= 4)

def test_gpt_coherence_atleast4():
    assert(metrics_summary.metrics_summary['mean_gpt_coherence'] >= 4)

def test_chat_gpt_groundedness_atleast4():
    assert(metrics_summary_chat.metrics_summary['mean_gpt_groundedness'] >= 4)

def test_chat_gpt_relevance_atleast4():
    assert(metrics_summary_chat.metrics_summary['mean_gpt_relevance'] >= 4)

def test_chat_gpt_retrieval_score_atleast4():
    assert(metrics_summary_chat.metrics_summary['mean_gpt_retrieval_score'] >= 4)