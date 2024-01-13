import os
import openai
import json

def auto_grading(student_response, suggested_answer):
    openai.api_type = "azure"
    openai.api_version = "2023-05-15"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")

    response = openai.ChatCompletion.create(
        engine="GPT35TURBO16K",
        messages=[
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
            {"role": "user", "content": f"You are a teacher, your responsibilities is grading the following student response and providing the answer as a JSON file including two key correctness(True/False) and explanation:\n\nQuestion: {student_response}\n\nStudent Response: {student_response}\n\nSuggested Answer: {suggested_answer}\n\n"}
        ]
    )

    return response['choices'][0]['message']['content']

# Example usage:
student_response = "Photosynthesis is the process by which plants take in carbon dioxide and release oxygen. It occurs in the chloroplasts of plant cells and involves the conversion of sunlight into energy, which is used to produce glucose."
suggested_answer = "Photosynthesis is the complex biological process through which plants, algae, and some bacteria convert light energy into chemical energy. During this process, carbon dioxide and water are combined in the chloroplasts, using sunlight to produce glucose and oxygen as byproducts."

result = auto_grading(student_response, suggested_answer)
print(result)