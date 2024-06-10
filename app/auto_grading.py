import os
import openai
import json
import timeit

def auto_grading(question_title, question_type, options, student_response, suggested_answer):
    openai.api_type = "azure"
    openai.api_version = "2023-05-15"
    openai.api_base = "https://sunhackathon26.openai.azure.com/"
    openai.api_key = "31de78c622dc481b9d25cb3ffde694f0"
    # Create the prompt with the question title and options
    if question_type == 'multiple_choice':
        prompt = f"You are a teacher, your responsibilities is grading the following student response andproviding the answer as a JSON file including two key correctness(True/False) and explanation:\n\nQuestion: {question_title}\n\nOptions: {', '.join(options)}\n\n Student Response: {student_response}\n\nSuggested Answer: {suggested_answer}\n\n"
    else:
        prompt = f"You are a teacher, your responsibilities is grading the following student response and providing the answer as a JSON file including two key correctness(True/False) and explanation:\n\nQuestion: {question_title}\n\nStudent Response: {student_response}\n\nSuggested Answer: {suggested_answer}\n\n"

    response = openai.ChatCompletion.create(
        engine="GPT35TURBO16K",
        messages=[
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
            {"role": "user", "content": prompt}
        ]
    )
    
    data_dict = json.loads(response['choices'][0]['message']['content'])
    return data_dict

title = "What is the capital of France?"
options = ["A. Paris", "B. London", "C. Berlin", "D. Rome"]
student_response = "Paris"
suggested_answer = "A. Paris"
question_type='multiple_choice'

start= timeit.default_timer()
result = auto_grading(title,question_type, options, student_response, suggested_answer)
end= timeit.default_timer()
print(result)
print(end-start)