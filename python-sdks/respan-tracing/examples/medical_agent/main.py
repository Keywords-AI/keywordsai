# Importing the needed modules
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from Utils.Agents import (
    Cardiologist,
    Psychologist,
    Pulmonologist,
    MultidisciplinaryTeam,
)
import json, os
from respan_tracing.main import RespanTelemetry
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
MEDICAL_REPORT_PATH = (
    PROJECT_ROOT
    / "Medical Reports"
    / "Medical Rerort - Michael Johnson - Panic Attack Disorder.txt"
)


# Loading API key from a dotenv file.
load_dotenv(dotenv_path=".env", override=True)
# Initialize Respan with proper configuration
k_tl = RespanTelemetry(
    api_key=os.getenv("RESPAN_API_KEY"),
    base_url=os.getenv("RESPAN_BASE_URL"),
    log_level="DEBUG",
)

from respan_tracing.decorators import workflow, task, tool

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@tool(name="Load Medical Report")
def load_medical_report():
    """Load and return the patient's medical report"""
    with open(
        MEDICAL_REPORT_PATH,
        "r",
    ) as file:
        medical_report = file.read()
    print("✅ Medical report loaded successfully")
    return medical_report


@task(name="Create Agents")
def create_agents(medical_report):
    """Create the three specialist AI agents"""
    agents = {
        "Cardiologist": Cardiologist(medical_report),
        "Psychologist": Psychologist(medical_report),
        "Pulmonologist": Pulmonologist(medical_report),
    }
    print("✅ Created 3 specialist agents: Cardiologist, Psychologist, Pulmonologist")
    return agents


@task(name="Run Individual Agent")
def get_response(agent_name, agent):
    """Run individual agent analysis"""
    response = agent.run()
    print(f"✅ {agent_name} analysis completed")
    return agent_name, response


@task(name="Run Specialist Agents")
def run_specialist_agents(agents):
    """Run all specialist agents concurrently and collect their responses"""
    responses = {}
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(get_response, name, agent): name
            for name, agent in agents.items()
        }

        for future in as_completed(futures):
            agent_name, response = future.result()
            responses[agent_name] = response

    print("✅ All specialist analyses completed concurrently")
    return responses


@task(name="Run Multidisciplinary Team Analysis")
def run_multidisciplinary_analysis(responses):
    """Run the multidisciplinary team analysis to generate final diagnosis"""
    team_agent = MultidisciplinaryTeam(
        cardiologist_report=responses["Cardiologist"],
        psychologist_report=responses["Psychologist"],
        pulmonologist_report=responses["Pulmonologist"],
    )

    final_diagnosis = team_agent.run()
    print("✅ Multidisciplinary team analysis completed")
    return final_diagnosis



@task(name="Save Diagnosis")
def save_diagnosis(final_diagnosis):
    """Save the final diagnosis to a text file"""
    final_diagnosis_text = "### Final Diagnosis:\n\n" + final_diagnosis
    txt_output_path = "Results/final_diagnosis.txt"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(txt_output_path), exist_ok=True)

    # Write the final diagnosis to the text file
    with open(txt_output_path, "w") as txt_file:
        txt_file.write(final_diagnosis_text)

    print(f"✅ Final diagnosis saved to {txt_output_path}")
    return txt_output_path


@workflow(name="AI Medical Diagnosis Workflow")
def run_complete_workflow():
    """Execute the complete AI medical diagnosis workflow"""
    print("🚀 Starting AI Medical Diagnosis Workflow...")

    # Step 1: Load medical report
    medical_report = load_medical_report()

    # Step 2: Create specialist agents
    agents = create_agents(medical_report)

    # Step 3: Run specialist analyses concurrently
    specialist_responses = run_specialist_agents(agents)

    # Step 4: Run multidisciplinary team analysis
    final_diagnosis = run_multidisciplinary_analysis(specialist_responses)

    # Step 5: Save results
    output_path = save_diagnosis(final_diagnosis)

    print("🎉 Complete workflow finished successfully!")
    return output_path


# Execute the complete workflow
if __name__ == "__main__":
    output_file = run_complete_workflow()
