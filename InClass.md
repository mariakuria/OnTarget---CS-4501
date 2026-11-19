What is our Moat?

One of our moats is our Leetcode-interface for problems. Although our application does not have integration with user Leetcode accounts yet, if we integrate that, that feature would allow us to have a connector with a system that users are familiar with. 
The fact that our application uses data from community-approved common company problems also helps us create a moat, and we can increase this moat by increasing our LLM validation for output (to continue to double-check the accuracy of our results). To increase our moat, we could also implement a system where users can give feedback on whether their prep was accurate to their specific company interview, as well.

How will you validate the output of the LLM you are using?

We can use checks against other LLMs or other prompts to double check that the generated output is accurate to commonly asked company questions. Our application also uses Human-in-the-Loop elements through the feedback system (where users can give feedback on whether or not the prep was accurate to the specific company interview).


How good is your system?

Benchmark:

Inputs - Several companies with varying expected interview dates.
Outputs - The generated plans should be different for each company and date. The plan should also be accurate to what companies usually ask. 
Mechanism to compute metrics - An LLM can be used to check output
