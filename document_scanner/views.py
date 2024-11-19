import os
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import time
import uuid
import json

API_KEY = 'K85954640988957'

@csrf_exempt
def scan_document(request):
    if request.method == 'POST':
        image_data = request.FILES.get('image')
        if image_data:
            try:
                # Create the 'temp_images' directory if it doesn't exist
                if not os.path.exists('temp_images'):
                    os.makedirs('temp_images')
                
                # Save the image to a temporary location
                image_path = os.path.join('temp_images', str(uuid.uuid4()) + '.jpg')
                with open(image_path, 'wb') as f:
                    for chunk in image_data.chunks():
                        f.write(chunk)
                
                # Make a request to the OCR.space API
                payload = {
                    'apikey': API_KEY,
                    'language': 'eng',  # You can specify the language code here
                    'isTable': True,  # If your document contains tables
                    'OCREngine': 2,  # OCR Engine mode (1: basic, 2: advanced)
                }
                with open(image_path, 'rb') as f:
                    response = requests.post('https://api.ocr.space/parse/image', files={'file': f}, data=payload)
                
                # Check if the OCR.space API call was successful
                if response.status_code == 200:
                    parsed_response = response.json()
                    extracted_text = parsed_response.get('ParsedResults', [{}])[0].get('ParsedText', '')
                    # Serialize the extracted text to JSON
                    extracted_data = extract_form_data(extracted_text)
                    # Save the extracted data to a JSON file
                    save_json_data(extracted_data)
                    # Generate API payload
                    api_payload = generate_api_payload(extracted_data)
                    # Return the extracted information and API payload in the response
                    return JsonResponse({'extracted_data': extracted_data, 'api_payload': api_payload})
                else:
                    return JsonResponse({'error': 'An error occurred while processing the document.'}, status=500)
                
            except Exception as e:
                print(f"Error in scan_document: {e}")
                return JsonResponse({'error': 'An error occurred while processing the document.'}, status=500)
        else:
            return JsonResponse({'error': 'No image data received.'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


def extract_form_data(extracted_text):
    formData = {}

    # Mapping of field names to their expected labels in the OCR extracted text
    field_mapping = {
        "Reg No": ["Reg No", "Registration No"],
        "Enquiry No": ["Enquiry No", "Enquiry Number"],
        "Without Enquiry": ["Without Enquiry"],
        "Class": ["Class"],
        "DOB": ["DOB", "Date of Birth"],
        "Student Name": ["Student Name"],
        "Father's Name": ["Father's Name"],
        "Mother's Name": ["Mother's Name"],
        "Grand Father's Name": ["Grand Father's Name"],
        "Prospectus": ["Prospectus", "Aadhar No"],
        "Gender": ["Gender"],
        "Nationality": ["Nationality"],
        "Mobile No": ["Mobile No"],
        "Alternate Mobile No": ["Alternate Mobile No"],
        "Email-Id": ["Email-Id", "Email"],
        "Pin Code": ["Pin Code", "Postal Code"],
        "Country": ["Country"],
        "State": ["State"],
        "City": ["City", "City/Town"]
    }

    # Search for each field in the extracted text and extract corresponding values
    for field, labels in field_mapping.items():
        for label in labels:
            if label in extracted_text:
                start_index = extracted_text.index(label) + len(label)
                end_index = extracted_text.find('\n', start_index)
                field_value = extracted_text[start_index:end_index].strip()
                formData[field] = field_value
                break

    return formData


def save_json_data(data):
    timestamp = int(time.time())
    json_filename = f'extracted_data_{timestamp}.json'
    json_path = os.path.join('json_files', json_filename)
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Create a text file with the formatted registration form information
    text_filename = f'registration_form_{timestamp}.txt'
    text_path = os.path.join('text_files', text_filename)
    with open(text_path, 'w') as text_file:
        text_file.write('Registration Form\n')
        text_file.write('Registration Number: ' + str(data.get('Reg No', '')) + '\n')
        text_file.write('Enquiry Number: ' + str(data.get('Enquiry No', '')) + '\n')
        text_file.write('Without Enquiry: ' + str(data.get('Without Enquiry', '')) + '\n')
        text_file.write('Class Details\n')
        text_file.write('• Class: ' + str(data.get('Class', '')) + '\n')
        text_file.write('• Date of Birth (DOB): ' + str(data.get('DOB', '')) + '\n')
        text_file.write('Personal Details\n')
        text_file.write('• Student Name: ' + str(data.get('Student Name', '')) + '\n')
        text_file.write('• Father’s Name: ' + str(data.get("Father's Name", '')) + '\n')
        text_file.write('• Mother’s Name: ' + str(data.get("Mother's Name", '')) + '\n')
        text_file.write('• Grandfather’s Name: ' + str(data.get("Grand Father's Name", '')) + '\n')
        text_file.write('• Prospectus: ' + str(data.get('Prospectus', '')) + '\n')
        text_file.write('• Gender: ' + str(data.get('Gender', '')) + '\n')
        text_file.write('• Nationality: ' + str(data.get('Nationality', '')) + '\n')
        text_file.write('• Mobile Number: ' + str(data.get('Mobile No', '')) + '\n')
        text_file.write('• Alternate Mobile Number: ' + str(data.get('Alternate Mobile No', '')) + '\n')
        text_file.write('• Email Address: ' + str(data.get('Email-Id', '')) + '\n')
        text_file.write('Address\n')
        text_file.write('• Pin Code: ' + str(data.get('Pin Code', '')) + '\n')
        text_file.write('• Country: ' + str(data.get('Country', '')) + '\n')
        text_file.write('• State: ' + str(data.get('State', '')) + '\n')
        text_file.write('• City: ' + str(data.get('City', '')) + '\n')


def generate_api_payload(data):
    # Example implementation of generating API payload from extracted data
    # Modify this function according to your API requirements
    api_payload = {}
    api_payload['registration_number'] = data.get('Reg No')
    api_payload['enquiry_number'] = data.get('Enquiry No')
    api_payload['without_enquiry'] = data.get('Without Enquiry')
    api_payload['class'] = data.get('Class')
    api_payload['date_of_birth'] = data.get('DOB')
    api_payload['student_name'] = data.get('Student Name')
    api_payload["father_name"] = data.get("Father's Name")
    api_payload["mother_name"] = data.get("Mother's Name")
    api_payload["grandfather_name"] = data.get("Grand Father's Name")
    api_payload['prospectus'] = data.get('Prospectus')
    api_payload['gender'] = data.get('Gender')
    api_payload['nationality'] = data.get('Nationality')
    api_payload['mobile_number'] = data.get('Mobile No')
    api_payload['alternate_mobile_number'] = data.get('Alternate Mobile No')
    api_payload['email_id'] = data.get('Email-Id')
    api_payload['pin_code'] = data.get('Pin Code')
    api_payload['country'] = data.get('Country')
    api_payload['state'] = data.get('State')
    api_payload['city'] = data.get('City')
    # Add more fields as needed
    return api_payload


def index(request):
    return render(request, 'index.html')
