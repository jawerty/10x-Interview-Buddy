import os
import json
import time
import random
import copy
import requests

from PIL import Image

import streamlit as st

st.set_page_config(
	page_title='10x Interview Buddy - Instant SWE Mock Interview Questions From Job Descriptions',
	page_icon="👨‍💻"                
)

loading_image = Image.open('./bean-eater.gif')

API_KEY = os.getenv('API_KEY')

general_question_types = ["Multiple Choice", "Open Ended"]
question_types = general_question_types + ["System Design", "Take Home Assessment", "Data Structure and Algorithms", "Behavioral"]

class Prompt:
	def __init__(self, job_description, job_position):
		self.job_description = job_description
		self.job_position = job_position
		self.previous_questions = []

	def add_question(self, question):
		self.previous_questions.append(question)

	def get_template(self):
		if len(self.previous_questions) > 0:
			questions = f"\nQuestion: ".join(self.previous_questions[-3:])
			question_prompt = f"Here are the previous questions:\n{questions}"
		else:
			question_prompt = ""

		return f"""
			[INST]
			<<SYS>>
			%s

			{question_prompt}

			Here is the Job Description:
			{self.job_description}

			Here is the Job Position:
			{self.job_position}
			

			Only respond with your interview question, do not respond with anything other than the interview question you generate.
			<</SYS>>
			[/INST]
		""".strip()

	def get_prompt_for_general_question(self, question_type):
		prompt = f"""
			You are a software engineering interviewing bot, your role is to generate interview questions for the given job description and job title.
			
			You must follow these instructions:
			- First you must analyze the job description and the job position and determine what would be a challenging interview question for this role
			- Generate an interview question that would vet the candidate based on their problem solving abilities and general domain knowledge
			- Your question MUST be a "{question_type}" question! Please format your questions as a "{question_type}" question.
			- If you are given previous questions please think of a unique question not related to the previous questions.
			- Keep the question brief and concise
			- Only respond with the interview question, do not respond with any explanation ONLY respond with the interview question.

		""".strip()
		template = self.get_template()

		return self.get_template() % prompt 

	def get_prompt_for_behavioral_question(self, question_type):
		prompt = f"""
			You are a software engineering interviewing bot, your role is to generate behavioral interview questions for the given job description and job title.
			
			You must follow these instructions:
			- First you must analyze the job description and the job position and determine what would be a good behavioral interview question for this role
			- Think of a behavioral question that would vet whether or not the candidate would either work well in a team, be a dependable engineer, have quality communication and other behavioral things.
			- If you are given previous questions please think of a unique question not related to the previous questions given.
			- Keep the question brief and concise
			- Only respond with the interview question, do not respond with any explanation ONLY respond with the interview question.
		""".strip()
		template = self.get_template()

		return self.get_template() % prompt 

	def get_prompt_for_system_design_question(self, question_type):
		prompt = f"""
			You are a software engineering interviewing bot, your role is to generate System Design interview questions for the given job description and job title.
			
			You must follow these instructions:
			- First you must analyze the job description and the job position and determine what would be a good System Design interview question for this role
			- System design questions are good at vetting an interview candidates knowledge of many aspects of the system they will work in; keep this in mind.
			- Think of what architecture the candidate will be working in based on the given job description. Using this architcture think of a good System Design question
			- If you are given previous questions please think of a unique question not related to the previous questions given.
			- Keep the question brief and concise
			- Only respond with the interview question, do not respond with any explanation ONLY respond with the interview question.
		""".strip()
		template = self.get_template()

		return self.get_template() % prompt 

	def get_prompt_for_algorithm_question(self, question_type):
		prompt = f"""
			You are a software engineering interviewing bot, your role is to generate Data Structure and Algorithm interview questions for the given job description and job title.
			
			You must follow these instructions:
			- First you must analyze the job description and the job position and determine what would be a good Data Structure and Algorithm interview question for this role
			- You must present a problem for the candidate to solve that would test the candidates general Computer Science knowledge and competence with Data Structure and Algorithms.
			- Also, use the job description to pick whick programming language you believe would be appropriate to write the problem code in
			- For the problem you generate for the candidate: explain what the constraints are and what time complexity the candidate must respond with.
			- Explain a possible use case for the problem that you think of after generating the problem.
			- If you are given previous questions please think of a unique question not related to the previous questions given.
			- Only respond with the interview problem, do not respond with any explanation ONLY respond with the interview problem.
		""".strip()
		template = self.get_template()

		return self.get_template() % prompt 

	def get_prompt_for_take_home_question(self, question_type):
		prompt = f"""
			You are a software engineering interviewing bot, your role is to generate a Take Home Assessment to vet the candidate for the given job description and job title.
			
			You must follow these instructions:
			- First you must analyze the job description and the job position and determine what would be a good Take Home Assessment for this role
			- Your take home assessment must vet the software engineers ability to build (code) a project that would require the skills needed to do the job position.
			- The take home assessment you think of must vet the candidate based on technologies mentioned in the job description
			- Think of a take home assessment that could be coded in a weekend (no more than 3 days)
			- If you are given previous questions please think of a unique question not related to the previous questions given.
			- Only respond with the interview problem, do not respond with any explanation ONLY respond with the interview problem.
		""".strip()
		template = self.get_template()

		return self.get_template() % prompt 


	def get_prompt_for_answering_question(self, question, is_algo=False):
		prompt = f"""
			[INST]
			<<SYS>>
			You are a senior software engineer bot, your role is to provide an answer to software engineering interview questions given an interview question.
			
			You must follow these instructions:
			{"" if is_algo else "- You must determine whether the given question is multiple choice or open ended."}
			{"-The question you will be given will be a data structure and algorithm coding problem. Pick a programming language and solve the problem. Write out the full solution and an explanation of how you implemented it." if is_algo else ""}
			- Respond with an accurate answer and if the question is open ended provide and in-depth reason for why your answer is good
			{"- Write out your answer to this coding problem in one of the following programming languages (python, C, javascript, go, ruby, c# or Java) " if is_algo else ""}
			- Breakdown why your answer would be good as if an engineer had to review your response to prepare for an interview
			- If there are any specific technologies, architectures, design paradigms that you utilize in your answer, provide brief definitions for each of these.

			Here is the interview question you need to answer:
			{question}

			Only respond with the question's answer, do not respond with any introduction or affirmative ONLY respond with the answer.
			<</SYS>>
			[/INST]
		""".strip()

		return prompt 

def llama2_request(prompt):
	url = f"https://api.runpod.ai/v2/llama2-13b-chat/runsync"

	headers = {
	  "Authorization": API_KEY,
	  "Content-Type": "application/json"
	}

	payload = {
	  "input": {
		"prompt": prompt,
		"sampling_params": {
		  "max_tokens": 4096,
		  "n": 1,
		  "frequency_penalty": 0.01,
		  "temperature": 0.75,
		}
	  }
	}

	start_time = time.time()
	response = requests.post(url, headers=headers, json=payload)

	response_json = response.json()

	output = ""
	if response_json["status"] == "COMPLETED":
		output += "".join(response_json["output"]["text"])
		return output

	status_url = f"https://api.runpod.ai/v2/llama2-13b-chat/stream/{response_json['id']}"
  
	while True:
		time.sleep(.5)
		try:
			get_status = requests.get(status_url, headers=headers)
			get_status_json = get_status.json()
			if "stream" in get_status_json:
				for stream in get_status_json["stream"]:
					next_tokens = "".join(stream["output"]["text"])
					output += next_tokens
			
			if get_status_json["status"] == "IN_PROGRESS":
				continue
			else:
				end_time = time.time()
				output += "".join(response_json["output"]["text"])
				return output

		except Exception as e:
			print(str(e))
			return output

def generate_questions(loading_state, main_container):
	loading_state.write("""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto; background: rgba(241, 242, 243, 0); display: block; shape-rendering: auto;" width="200px" height="200px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
	<g>
	  <circle cx="60" cy="50" r="4" fill="#47fffa">
	    <animate attributeName="cx" repeatCount="indefinite" dur="1s" values="95;35" keyTimes="0;1" begin="-0.67s"></animate>
	    <animate attributeName="fill-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="-0.67s"></animate>
	  </circle>
	  <circle cx="60" cy="50" r="4" fill="#47fffa">
	    <animate attributeName="cx" repeatCount="indefinite" dur="1s" values="95;35" keyTimes="0;1" begin="-0.33s"></animate>
	    <animate attributeName="fill-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="-0.33s"></animate>
	  </circle>
	  <circle cx="60" cy="50" r="4" fill="#47fffa">
	    <animate attributeName="cx" repeatCount="indefinite" dur="1s" values="95;35" keyTimes="0;1" begin="0s"></animate>
	    <animate attributeName="fill-opacity" repeatCount="indefinite" dur="1s" values="0;1;1" keyTimes="0;0.2;1" begin="0s"></animate>
	  </circle>
	</g><g transform="translate(-15 0)">
	  <path d="M50 50L20 50A30 30 0 0 0 80 50Z" fill="#ffdc00" transform="rotate(90 50 50)"></path>
	  <path d="M50 50L20 50A30 30 0 0 0 80 50Z" fill="#ffdc00">
	    <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" dur="1s" values="0 50 50;45 50 50;0 50 50" keyTimes="0;0.5;1"></animateTransform>
	  </path>
	  <path d="M50 50L20 50A30 30 0 0 1 80 50Z" fill="#ffdc00">
	    <animateTransform attributeName="transform" type="rotate" repeatCount="indefinite" dur="1s" values="0 50 50;-45 50 50;0 50 50" keyTimes="0;0.5;1"></animateTransform>
	  </path>
	</g>""", unsafe_allow_html=True)
	st.session_state.questions = []
	questions = []

	prompt = Prompt(st.session_state.job_description, st.session_state.job_position)
	
	main_container.write("")
	with main_container:
		content = main_container.container()
		with content:
			for i in range(0, st.session_state.question_count):
				if len(st.session_state.question_types) == 0:
					question_type = "Open Ended"
				else:
					question_type = random.choice(st.session_state.question_types)
				
				if question_type in general_question_types:
					question_prompt = prompt.get_prompt_for_general_question(question_type)
				elif question_type == "Behavioral":
					question_prompt = prompt.get_prompt_for_behavioral_question(question_type)
				elif question_type == "System Design":
					question_prompt = prompt.get_prompt_for_system_design_question(question_type)
				elif question_type == "Data Structure and Algorithms":
					question_prompt = prompt.get_prompt_for_algorithm_question(question_type)
				elif question_type == "Take Home Assessment":
					question_prompt = prompt.get_prompt_for_take_home_question(question_type)
				else:
					question_prompt = ""

				question = llama2_request(question_prompt)
				print("Got question", len(question))
				prompt.add_question(question)

				is_algo = question_type == "Data Structure and Algorithms"
				answer_prompt = prompt.get_prompt_for_answering_question(question, is_algo=is_algo)
			
				if question_type != "Take home Assessment":
					answer = llama2_request(answer_prompt)
					print("Got Answer", len(answer))
				else:
					answer = None

				question_object = {
					"question": question,
					"question_type": question_type,
				}

				if answer:
					question_object["answer"] = answer

				st.markdown(f"### Question #{i+1}")
				st.markdown(f":orange[Type: {question_object['question_type']}]")
				st.markdown(question_object['question'])
				if 'answer' in question_object:
					with st.expander(":green[Answer (Spoiler)]"):
						st.markdown(question_object["answer"])
				st.divider()

	st.session_state.questions = copy.deepcopy(questions)
	print("QUESTIONS", len(st.session_state.questions))
	loading_state.write("")
			
loading_state = st.empty()
main_container = st.empty()

if 'questions' not in st.session_state or len(st.session_state.questions) == 0:
	with main_container:
		content = main_container.container()
		content.title("👨‍💻 10x Interview Buddy 👨‍💻")
		content.markdown("### :orange[Generate Mock SWE Interview Questions / Answers From Job Descriptions]")
		content.markdown("Made With ❤️ By [jaredthecoder](https://www.youtube.com/@jaredthecoder)")
		content.markdown("**SWE Interview Prep Sucks.** `JuNioRs mUsT HaVe 10 yEaRS Of ExPERiEnCe.`")
		content.markdown("### Why I built this")
		content.markdown("When I would look for Software Engineering roles I'd often look for mock interview questions but none were catered for the specific job I'd be applying for. I made this 10x Interview Buddy is a tool that uses an LLM (llama 2 13b chat model) to generate interview questions / answers for jobs you find on your search.")
		content.image("https://programmerhumor.io/wp-content/uploads/2022/11/programmerhumor-io-programming-memes-f8ce535399d3f25-758x590.jpg")
		st.session_state.questions = []

with st.sidebar:
	st.markdown("## Enter Job Details")
	st.markdown("*Paste the basic info for the job you're applying to*")
	st.session_state.job_position = st.text_input("Job Position", placeholder="Paste your job position here (e.g. Junior Software Engineer)")

	st.session_state.job_description = st.text_area("Job Description", placeholder="Paste your job description text here")

	st.divider()

	st.markdown("## Options")

	st.session_state.question_count = st.slider("Amount of Questions You Want", min_value=1, max_value=25)


	st.session_state.question_types = st.multiselect(
		'What type of questions do you want to generate (randomized per question)',
		question_types,
		question_types[-2:])

	st.divider()

	generate_click = st.button("Generate Interview Questions")

	if generate_click:
		generate_questions(loading_state, main_container)

