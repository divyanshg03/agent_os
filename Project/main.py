from agents import agent_1_generate, agent_2_validate
from metrics import measure_latency
from test_cases import TEST_QUERIES
import numpy as np
import json


def run_pipeline(query):
    agent1_output, t1 = measure_latency(agent_1_generate, query)
    agent2_output, t2 = measure_latency(agent_2_validate, agent1_output)

    total_time = t1 + t2

    return {
        "query": query,
        "agent1": agent1_output,
        "agent2": agent2_output,
        "latency": total_time,
        "agent1_latency": t1,
        "agent2_latency": t2
    }


def main():
    latencies = []
    agent1_latencies = []
    agent2_latencies = []
    results = []

    for query in TEST_QUERIES:
        result = run_pipeline(query)

        latencies.append(result["latency"])
        agent1_latencies.append(result["agent1_latency"])
        agent2_latencies.append(result["agent2_latency"])
        results.append(result)

        print("\n---")
        print("Query:", query)
        print("Response:", result["agent1"])
        print("Validation:", result["agent2"])
        print(f"Agent1 latency: {result['agent1_latency']:.2f}s")
        print(f"Agent2 latency: {result['agent2_latency']:.2f}s")
        print(f"Total latency: {result['latency']:.2f}s")

    # Save results to file
    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\n===== FINAL TABLE =====")
    print(f"p50 latency: {np.percentile(latencies, 50):.2f} sec")
    print(f"p95 latency: {np.percentile(latencies, 95):.2f} sec")
    print(f"avg latency: {np.mean(latencies):.2f} sec")
    print(f"Agent1 avg latency: {np.mean(agent1_latencies):.2f}s")
    print(f"Agent2 avg latency: {np.mean(agent2_latencies):.2f}s")


if __name__ == "__main__":
    main()