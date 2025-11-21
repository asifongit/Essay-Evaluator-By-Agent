# Code Flow Documentation

This document outlines the flow of the UPSC Essay Evaluation application.
![UPSC Essay Evaluation Flow Diagram](img.png)

## 1. User Interface (Frontend)
- **Entry Point**: The user accesses the web application via the browser.
- **Input**: The user can either:
    - Paste the essay text directly into a text area.
    - Upload a PDF file containing the essay.
- **Submission**: The user clicks the "Evaluate" button, sending the data to the backend.

## 2. Web Server (Backend - Flask)
- **Request Handling**: The `app.py` file receives the request at the `/evaluate` endpoint.
- **Data Processing**:
    - If a PDF is uploaded, the text is extracted using `pypdf`.
    - If text is pasted, it is used directly.
- **Workflow Invocation**: The extracted essay text is passed to the LangGraph workflow.

## 3. Evaluation Logic (LangGraph)
The core logic resides in `upsc_essay.py`, which uses a graph-based workflow to evaluate the essay.

### Workflow Steps:
1.  **Start**: The workflow begins with the essay text.
2.  **Parallel Evaluation**: The essay is sent to three separate evaluators simultaneously:
    -   **Language Evaluator**: Checks grammar, vocabulary, and style.
    -   **Analysis Evaluator**: Checks the depth and quality of the analysis.
    -   **Thought Evaluator**: Checks the clarity and flow of thought.
    *Each evaluator provides specific feedback and a score out of 10.*
3.  **Final Evaluation**:
    -   Collects feedback and scores from all three evaluators.
    -   Generates a summarized overall feedback.
    -   Calculates the average score.
4.  **End**: The workflow outputs the final results.

## 4. Response
- The backend sends the detailed feedback, individual scores, and average score back to the frontend as a JSON response.
- The frontend displays the results to the user.
