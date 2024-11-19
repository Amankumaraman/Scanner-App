# forms.py
from django import forms
import json

class HandwrittenForm(forms.Form):
    handwritten_data = forms.CharField(widget=forms.Textarea)

    def clean_handwritten_data(self):
        handwritten_text = self.cleaned_data['handwritten_data']
        try:
            # Process handwritten_text (e.g., using OCR or custom logic)
            # Validate the extracted data if needed
            # For demonstration purposes, assume it's valid JSON
            json_data = json.loads(handwritten_text)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid handwritten data")
        return json_data
