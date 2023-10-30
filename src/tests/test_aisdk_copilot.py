import pytest

from run import run_evaluation

# Test results are stored here
evaluation_results : any

@pytest.fixture(scope="session", autouse=True)
def run_before_any_test():
    from copilot_aisdk import chat
  
    global evaluation_results
    evaluation_results = run_evaluation(chat.chat_completion, 
                                        "test_aisdk_copilot",
                                        "src/tests/evaluation_dataset.jsonl")

def test_gpt_groundedness_atleast4():
    assert(evaluation_results['mean_gpt_groundedness'] >= 4)

def test_gpt_relevance_atleast4():
    assert(evaluation_results['mean_gpt_relevance'] >= 4)
        
def test_gpt_coherence_atleast4():
    assert(evaluation_results['mean_gpt_coherence'] >= 4)
    
    