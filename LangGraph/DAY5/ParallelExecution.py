from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
import time

# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ✅ State
class MedicalState(TypedDict):
    patient_name: str
    symptoms: str
    blood_test_result: str
    xray_result: str
    ecg_result: str
    final_report: str

# ✅ Node 1 - Blood Test (runs in parallel)
def blood_test(state: MedicalState):
    print("🩸 Blood Test started...")
    response = llm.invoke([
        SystemMessage(content="You are a lab technician. Give a short 1 line blood test result."),
        HumanMessage(content=f"Patient {state['patient_name']} symptoms: {state['symptoms']}")
    ])
    print("🩸 Blood Test completed!")
    return {"blood_test_result": response.content}

# ✅ Node 2 - X-Ray (runs in parallel)
def xray_test(state: MedicalState):
    print("🔬 X-Ray started...")
    response = llm.invoke([
        SystemMessage(content="You are a radiologist. Give a short 1 line X-Ray result."),
        HumanMessage(content=f"Patient {state['patient_name']} symptoms: {state['symptoms']}")
    ])
    print("🔬 X-Ray completed!")
    return {"xray_result": response.content}

# ✅ Node 3 - ECG (runs in parallel)
def ecg_test(state: MedicalState):
    print("❤️  ECG started...")
    response = llm.invoke([
        SystemMessage(content="You are a cardiologist. Give a short 1 line ECG result."),
        HumanMessage(content=f"Patient {state['patient_name']} symptoms: {state['symptoms']}")
    ])
    print("❤️  ECG completed!")
    return {"ecg_result": response.content}

# ✅ Node 4 - Final Report (runs AFTER all parallel nodes finish)
def generate_report(state: MedicalState):
    print("\n📝 Generating final report...")
    response = llm.invoke([
        SystemMessage(content="You are a senior doctor. Generate a short 3 line medical summary report."),
        HumanMessage(content=f"""Patient: {state['patient_name']}
Blood Test: {state['blood_test_result']}
X-Ray: {state['xray_result']}
ECG: {state['ecg_result']}""")
    ])
    return {"final_report": response.content}

# ✅ Build Graph with Parallel Execution
builder = StateGraph(MedicalState)

builder.add_node("blood_test", blood_test)
builder.add_node("xray_test", xray_test)
builder.add_node("ecg_test", ecg_test)
builder.add_node("generate_report", generate_report)

# ✅ Fan Out - START connects to all 3 nodes simultaneously!
builder.add_edge(START, "blood_test")
builder.add_edge(START, "xray_test")
builder.add_edge(START, "ecg_test")

# ✅ Fan In - all 3 nodes connect to generate_report
builder.add_edge("blood_test", "generate_report")
builder.add_edge("xray_test", "generate_report")
builder.add_edge("ecg_test", "generate_report")

builder.add_edge("generate_report", END)

graph = builder.compile()

# ✅ Take User Input
print("🏥 Medical Checkup System - Parallel Execution Demo")
print("-" * 40)
patient_name = input("Enter Patient Name: ")
symptoms = input("Describe Symptoms: ")

print(f"\n⚡ Running Blood Test + X-Ray + ECG simultaneously!")
print("-" * 40)

# ✅ Track time to show speed benefit
start_time = time.time()

result = graph.invoke({
    "patient_name": patient_name,
    "symptoms": symptoms,
    "blood_test_result": "",
    "xray_result": "",
    "ecg_result": "",
    "final_report": ""
})

end_time = time.time()

# ✅ Print Results
print("\n" + "=" * 40)
print(f"👤 Patient      : {result['patient_name']}")
print(f"🩸 Blood Test   : {result['blood_test_result']}")
print(f"🔬 X-Ray        : {result['xray_result']}")
print(f"❤️  ECG          : {result['ecg_result']}")
print(f"\n📋 Final Report :\n{result['final_report']}")
print(f"\n⏱️  Total Time   : {end_time - start_time:.2f} seconds")
print("=" * 40)

