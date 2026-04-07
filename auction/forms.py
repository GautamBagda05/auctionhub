from django import forms
from .models import Auction, Bid

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'category', 'image', 'starting_bid', 'reserve_price', 'end_time']
        widgets = {
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def __init__(self, *args, auction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.auction = auction

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if not self.auction:
            return amount

        min_bid = self.auction.highest_bid()

        if amount <= min_bid:
            raise forms.ValidationError(
                f"Bid must be greater than current highest bid (₹{min_bid})"
            )

        return amount