from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Form for submitting product reviews and ratings.
    """
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        min_value=1,
        max_value=5
    )
    
    review_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your experience with this product...',
            'rows': 4,
            'maxlength': 1000
        }),
        required=False,
        max_length=1000,
        help_text='Optional: Write a detailed review (max 1000 characters)'
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating

