import os
from load_datasets import load_ok_vqa_dataset
from clients import openai_client, openai_autorater
from dataclasses import dataclass, field
import asyncio
from typing import MutableSequence
import json


@dataclass(frozen=False)
class QuestionAccuracy:
    true_positives: int = 0
    false_positives: int = 0
    different_answers: list[tuple[str, str]] = field(default_factory=list)

@dataclass(frozen=False)
class TemperatureAccuracy:
    total_runs: int = 0
    true_positives: int = 0
    false_positives: int = 0
    accuracy: float = 0.0

question_accuracies: dict[str, QuestionAccuracy] = {}
temperature_results: dict[float, dict[str, TemperatureAccuracy]] = {}

ACCURACY_DATA_FILE = "accuracy_data.json"
TEMPERATURE_RESULTS_FILE = "temperature_accuracy_data.json"

FINAL_RESULTS_FILE = "final_results.json"

def save_accuracy_data(data: dict[str, QuestionAccuracy], filename: str = ACCURACY_DATA_FILE):
    with open(filename, 'w') as f:
        serializable_data = {q: acc.__dict__ for q, acc in data.items()}
        json.dump(serializable_data, f, indent=4)

def load_accuracy_data(filename: str = ACCURACY_DATA_FILE) -> dict[str, QuestionAccuracy]:
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        data = json.load(f)
        return {q: QuestionAccuracy(**acc_dict) for q, acc_dict in data.items()}

def save_temperature_results(data: dict[float, dict[str, TemperatureAccuracy]], filename: str = TEMPERATURE_RESULTS_FILE):
    with open(filename, 'w') as f:
        serializable_data = {}
        for temp, q_data in data.items():
            serializable_data[str(temp)] = {q: acc.__dict__ for q, acc in q_data.items()}
        json.dump(serializable_data, f, indent=4)

def load_temperature_results(filename: str = TEMPERATURE_RESULTS_FILE) -> dict[float, dict[str, TemperatureAccuracy]]:
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        data = json.load(f)
        loaded_data = {}
        for temp_str, q_data_dict in data.items():
            temp = float(temp_str)
            loaded_data[temp] = {q: TemperatureAccuracy(**acc_dict) for q, acc_dict in q_data_dict.items()}
        return loaded_data

def save_final_results_to_json(data: dict, filename: str = FINAL_RESULTS_FILE):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_final_results_from_json(filename: str = FINAL_RESULTS_FILE) -> dict:
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        return json.load(f)

class ExperimentRunner:
    def __init__(self, api_key: str):
        self.vqa_model = openai_client.OpenAIVQAModel(api_key)
        self.autorater = openai_autorater.OpenAIAIRater(api_key)
        self.okvqa_dataset = load_ok_vqa_dataset.OKVQA(num_images=1000).get_dataset()
        self.question_accuracies = load_accuracy_data()
        self.temperature_results = load_temperature_results()

    async def run_temperature_experiment(self, temperatures: list[float]):
        for temp in temperatures:
            if temp not in self.temperature_results:
                self.temperature_results[temp] = {}
            print(f"\n--- Running evaluation for temperature: {temp} ---")

            for entry_idx in range(0, len(self.okvqa_dataset)):
                entry = self.okvqa_dataset[entry_idx]
                image = entry['image']
                questions = entry['questions']
                golden_answers = entry['answers']

                print(f"Processing image_id: {entry['image_id']} at temperature {temp}")

                predicted_answers = await self.vqa_model.query_image(image, questions, temperature=temp)

                autorater_tasks = []
                questions_to_rate = []
                for i, question in enumerate(questions):
                    predicted_answer = predicted_answers[i] if i < len(predicted_answers) else 'N/A'
                    if predicted_answer != 'N/A':
                        autorater_tasks.append(self.autorater.rate_answer(question, golden_answers[i], predicted_answer))
                        questions_to_rate.append(question)

                scores = await asyncio.gather(*autorater_tasks)

                for j, score in enumerate(scores):
                    question = questions_to_rate[j]
                    if question not in self.temperature_results[temp]:
                        self.temperature_results[temp][question] = TemperatureAccuracy()
                    
                    current_qa = self.temperature_results[temp][question]
                    current_qa.total_runs += 1
                    if score is True:
                        current_qa.true_positives += 1
                    else:
                        current_qa.false_positives += 1
                
            for question, acc_data in self.temperature_results[temp].items():
                if acc_data.total_runs > 0:
                    acc_data.accuracy = acc_data.true_positives / acc_data.total_runs
        
        save_accuracy_data(self.question_accuracies)
        save_temperature_results(self.temperature_results)

    async def cluster_questions_by_creativity(self):
        """
        Clusters questions based on their creativity level using the OpenAI client.
        """
        clusters = await self.vqa_model.cluster_questions_by_creativity(self.temperature_results)
        print("\n--- Question Clusters by Creativity ---")
        for cluster_name, questions in clusters.items():
            print(f"\nCluster: {cluster_name}")
            print(f"  Questions ({len(questions)}):")
            for question in questions:
                print(f"    - {question}")
        return clusters

    def save_final_experiment_results(self, filename: str = FINAL_RESULTS_FILE):
        final_results = {"temperature_results": {}}
        for temp, q_data in self.temperature_results.items():
            final_results["temperature_results"][str(temp)] = {}
            for question, acc_data in q_data.items():
                final_results["temperature_results"][str(temp)][question] = {
                    "total_runs": acc_data.total_runs,
                    "true_positives": acc_data.true_positives,
                    "false_positives": acc_data.false_positives,
                    "accuracy": acc_data.accuracy
                }
        
        analysis_results = self._analyze_temperature_accuracy_changes()
        if analysis_results:
            final_results["analysis"] = analysis_results
 
        save_final_results_to_json(final_results, filename)

    def _analyze_temperature_accuracy_changes(self) -> dict:
        analysis_output = {}
        if not self.temperature_results:
            return analysis_output
        
        questions = set()
        for temp_data in self.temperature_results.values():
            questions.update(temp_data.keys())
        
        for question in questions:
            accuracies_by_temp = {}
            for temp in sorted(self.temperature_results.keys()):
                if question in self.temperature_results[temp]:
                    accuracies_by_temp[temp] = self.temperature_results[temp][question].accuracy
            
            if len(accuracies_by_temp) > 1:
                question_analysis = {"initial_accuracy": None, "changes": []}
                sorted_temps = sorted(accuracies_by_temp.keys())
                initial_temp = sorted_temps[0]
                initial_accuracy = accuracies_by_temp[initial_temp]
                question_analysis["initial_accuracy"] = {"temperature": initial_temp, "accuracy": initial_accuracy}

                for i in range(1, len(sorted_temps)):
                    current_temp = sorted_temps[i]
                    current_accuracy = accuracies_by_temp[current_temp]
                    
                    change = current_accuracy - accuracies_by_temp[sorted_temps[i-1]]
                    change_type = "increased" if change > 0 else "decreased" if change < 0 else "stayed the same"
                    if change_type != "stayed the same":
                        question_analysis["changes"].append({
                            "temperature": current_temp,
                            "accuracy": current_accuracy,
                            "change_type": change_type,
                            "from_previous_temp": sorted_temps[i-1]
                        })
                if question_analysis["initial_accuracy"] or question_analysis["changes"]:
                    analysis_output[question] = question_analysis
            elif len(accuracies_by_temp) == 1:
                temp = list(accuracies_by_temp.keys())[0]
                analysis_output[question] = {"single_result": {"temperature": temp, "accuracy": accuracies_by_temp[temp]}}
        return analysis_output

    def load_and_print_final_results(self, filename: str = FINAL_RESULTS_FILE):
        loaded_results = load_final_results_from_json(filename)
        print("\n--- Final Experiment Results ---")

        if "temperature_results" in loaded_results:
            print("\n--- Overall Accuracy per Question and Temperature ---")
            for temp_str, q_data in loaded_results["temperature_results"].items():
                print(f"\nTemperature: {temp_str}")
                for question, acc_data in q_data.items():
                    print(f"  Question: {question}")
                    print(f"    - Total Runs: {acc_data['total_runs']}")
                    print(f"    - True Positives: {acc_data['true_positives']}")
                    print(f"    - False Positives: {acc_data['false_positives']}")
                    print(f"    - Accuracy: {acc_data['accuracy']:.2f}")
 
        if "analysis" in loaded_results:
            print("\n--- Analyzing Temperature-Based Accuracy Changes ---")
            for question, analysis_data in loaded_results["analysis"].items():
                print(f"\nQuestion: {question}")
                if "initial_accuracy" in analysis_data and analysis_data["initial_accuracy"]:
                    initial = analysis_data["initial_accuracy"]
                    print(f"  Initial Accuracy (temp={initial['temperature']}): {initial['accuracy']:.2f}")
                if "changes" in analysis_data and analysis_data["changes"]:
                    for change in analysis_data["changes"]:
                        print(f"  Accuracy at temp={change['temperature']}: {change['accuracy']:.2f} ({change['change_type']} from previous temp={change['from_previous_temp']})")
                if "single_result" in analysis_data and analysis_data["single_result"]:
                    single = analysis_data["single_result"]
                    print(f"  Only one temperature result available (temp={single['temperature']}): {single['accuracy']:.2f}")
          
        print("----------------------------------------")

async def main():

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    runner = ExperimentRunner(api_key)

    temperatures = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    # await runner.run_temperature_experiment(temperatures)
    # runner.save_final_experiment_results()
    runner.load_and_print_final_results()
    
    # Cluster questions by creativity level
    await runner.cluster_questions_by_creativity()

if __name__ == "__main__":
    asyncio.run(main())
