import pytest

from evaluate import run_evaluation

# Test results are stored here
evaluation_results : any

@pytest.fixture(scope="session", autouse=True)
def run_before_any_test():
    from copilot_aisdk import chat
  
    global evaluation_results
    evaluation_results = run_evaluation(chat.chat_completion, 
                                        "test_aisdk_copilot",
                                        "/src/evaluation_dataset.jsonl")

def get_metric_average(metric_name):    
    # metrics format is e.g.: ['3', '5', '5', '5', '5', '4', '3', '5', '5', '5', '5', '5', '1']
    metrics_array_str = evaluation_results["artifacts"][metric_name]
    
    # convert to array of floats
    metrics_array_float = [float(value) for value in metrics_array_str]
    average = sum(metrics_array_float) / len(metrics_array_float)
    
    print(f"{metric_name}: average {average}")
    return average
    
def test_gpt_groundedness_atleast4():
    assert(get_metric_average("gpt_groundedness") >= 4)

def test_gpt_similarity_atleast4():
    assert(get_metric_average("gpt_similarity") >= 4)

def test_gpt_relevance_atleast4():
    assert(get_metric_average("gpt_relevance") >= 4)
        
def test_gpt_coherence_atleast4():
    assert(get_metric_average("gpt_coherence") >= 4)
    
def test_gpt_fluency_atleast4():
    assert(get_metric_average("gpt_fluency") >= 4)
    
    