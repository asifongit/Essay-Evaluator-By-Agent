import os
from dotenv import load_dotenv
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    from upsc_essay import workflow
    print("Import successful")
    
    initial_state = {'essay': "This is a test essay to check if the system is working."}
    print("Invoking workflow...")
    result = workflow.invoke(initial_state)
    print("Workflow result:", result)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
