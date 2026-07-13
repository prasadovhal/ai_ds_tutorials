# evaluations
review of evaluations for LLM and agents


is answer
1. Correctness
2. relevant
3. complete
4. helpful
5. clear
6. faithfulness
7. groundness
8. safe
9. 


here's the recommended sequence:

1. theory.md — Read first. All concepts, intuition, diagrams, comparison tables, interview questions. This is your learning material.  
2. sample_data.json — Skim it. See the 10 questions and simulated model predictions that the code uses.
3. dataset.py — Read the data loading functions. Understand how train.csv and sample_data.json get loaded and how predictions are simulated.                         
4. evaluator.py — Read the implementations. All 13 evaluator classes (OfflineEvaluator, OnlineEvaluator, RegressionTester, CICDGate, etc.). This is where the logic
lives.
5. main.py — Run it (python main.py). It calls everything from steps 3-4 and shows live output. Now the results will make sense because you've read the theory and   
code.
6. README.md — Reference. Come back to it for the topics table or project structure.
