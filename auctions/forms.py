from django import forms
from . models import Listing, Bid, Comment


class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = ('title',
                  'category',
                  'description',
                  'image',
                  'starting_bid',
                  'active',
                  )
        labels = {'title': 'Listing Title',
                  'category': "Select a Category",
                  'description': "Describe your listing",
                  'image': 'Upload an Image',
                  'starting_bid': 'Enter a starting bid',
                  'active': 'Start your Auction'}
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a title'}),
                   'category': forms.Select(attrs={'class': 'form-control'}),
                   'description': forms.Textarea(attrs={'class': 'form-control',
                                                        'placeholder': 'Enter your description'}),
                   }

class BidForm(forms.ModelForm):
    def __init__(self, maximum_bid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_max_bid = maximum_bid

    class Meta:
        model = Bid
        fields = ('bid',)

    # How to pass a parameter to a form.
    # https://stackoverflow.com/questions/14660037/django-forms-pass-parameter-to-form
    # Note that you must return a value as teh bid field requires an integer.
    def clean_bid(self):
        new_bid = self.cleaned_data.get('bid',)

        if self.current_max_bid >= new_bid:
            raise forms.ValidationError(f'Your bid of ${new_bid} must be more than the '
                                        f'current bid of ${self.current_max_bid}.')
        return new_bid

class BidFormOwner(forms.ModelForm):

    class Meta:
        model = Listing
        fields = ('active',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('comment',)
        labels = {'comment': 'Add your comment'}
        widgets = {'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Your Comment'})}





