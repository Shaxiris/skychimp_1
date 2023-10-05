from django import forms
from blog.models import BlogEntry


class BlogEntryForm(forms.ModelForm):
    """Форма для записи блога"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = BlogEntry
        exclude = ('views_number', 'publication_date')
