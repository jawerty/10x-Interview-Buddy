# 10x Interview Buddy
[Try it out here](10x-interview-buddy.streamlit.app)

Generate mock SWE interview questions (and answers) from job descriptions

When I would look for Software Engineering roles I'd often look for mock interview questions but none were catered for the specific job I'd be applying for. I made this 10x Interview Buddy is a tool that uses an LLM (llama 2 13b chat model) to generate interview questions / answers for jobs you find on your search.

(Mostly built during my recent Youtube [livestream](https://www.youtube.com/watch?v=8DA4CpEgtno))

# How it was made
The frontend was built in python with [streamlit](https://streamlit.io/) which I discovered a week ago and have become a fan.

I use Llama 2 for the question/answer generation with some logic to modify prompts based on user input, and I utilize a short term memory (history) to make ensure variability for subsequent questions. I tried to cater each question type to properly vet a SWE candidate.

# Try it out
[Click here](10x-interview-buddy.streamlit.app)